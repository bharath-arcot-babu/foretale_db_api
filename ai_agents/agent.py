import sys
import json
import logging
from langgraph.graph import StateGraph, START,END

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent.log')
    ]
)
logger = logging.getLogger(__name__)

#models
from models.summarizer_model import SummarizerOutput

#tools
from tools.summarizer_tool import TestCaseSummarizer
from tools.ambiguity_resolver import AmbiguityResolver
from tools.metadata_extractor_tool import MetadataExtractor
from tools.table_resolver_tool import TableResolverTool
from tools.column_resolver_tool import ColumnResolverTool
from tools.generate_sql_tool import SQLGenerationTool
from tools.sql_formatter_tool import SQLFormatterTool
from tools.update_config_to_database_tool import UpdateConfigToDatabaseTool

#llm
from layer_llm_service.bedrock_langchain_utils import BedrockLangChainService

# Initialize the LLM
llm = BedrockLangChainService().get_llm()

def summarize_test_case(state):
    logger.info("Starting test case summarization")
    logger.debug(f"Input state: {state}")
    
    test_case=state.get("test_case", ""),
    test_description=state.get("test_description", ""),
    past_user_responses=state.get("past_user_responses", ""),

    result = TestCaseSummarizer().summarize(
        test_case=test_case,
        test_description=test_description,
        past_user_responses=past_user_responses,
    )

    logger.info("Test case summarization completed")
    logger.debug(f"Summarization result: {result}")

    # If result is a JSON string, parse it
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON result, using raw string")
            result = {"summary": result}

    summarizer_output = SummarizerOutput(
        summary=result.get("summary", ""),
        key_tables=result.get("key_tables", []),
        key_columns=result.get("key_columns", []),
        key_criteria=result.get("key_criteria", []),
        ambiguities=result.get("ambiguities", []),
    )

    messages = state.get("messages", [])
    assistant_content = json.dumps(result, indent=2)
    messages = messages + [{"role": "assistant", "content": assistant_content}]

    return {
        **state,
        "messages": messages,
        "summary": summarizer_output.summary,
        "key_tables": summarizer_output.key_tables,
        "key_columns": summarizer_output.key_columns,
        "key_criteria": summarizer_output.key_criteria,
        "ambiguities": summarizer_output.ambiguities,
    }

def ambiguity_resolver(state):
    logger.info("Starting ambiguity resolution")
    ambiguities = state.get("ambiguities")

    if ambiguities:
        logger.info(f"Found {len(ambiguities)} ambiguities to resolve")
        for ambiguity in ambiguities:
            project_id = state.get("project_id")
            test_id = state.get("test_id")
            last_updated_by = state.get("last_updated_by")
            question_type = "Input"

            logger.debug(f"Resolving ambiguity: {ambiguity}")
            result = AmbiguityResolver().resolve_ambiguity(
                project_id=project_id,
                test_id=test_id,
                last_updated_by=last_updated_by,
                question_type=question_type,
                response_text= ambiguity
            )
            logger.debug(f"Ambiguity resolution result: {result}")
    else:
        logger.info("No ambiguities found to resolve")
    
    return state
        

def extract_tables(state):
    logger.info("Starting table extraction")
    schema_name = state.get("schema_name", "")
    logger.debug(f"Extracting tables for schema: {schema_name}")

    result = MetadataExtractor().get_schema_tables(schema_name=schema_name)
    logger.info(f"Found {len(result)} tables")
    logger.debug(f"Extracted tables: {result}")

    messages = state.get("messages", [])
    assistant_content = json.dumps(result, indent=2)
    messages = messages + [{"role": "assistant", "content": assistant_content}]

    return {
        **state,
        "messages": messages,
        "all_database_target_tables_with_description": assistant_content
    }

def resolve_tables(state):
    logger.info("Starting table resolution")
    key_tables = state.get("key_tables")
    database_tables = state.get("all_database_target_tables_with_description")
    logger.debug(f"Resolving tables: {key_tables}")

    result = TableResolverTool().resolve_tables(
        key_tables=key_tables,
        database_tables=database_tables
    )
    logger.info("Table resolution completed")
    logger.debug(f"Resolved tables: {result}")

    messages = state.get("messages", [])
    assistant_content = json.dumps(result, indent=2)
    messages = messages + [{"role": "assistant", "content": assistant_content}]

    return {
        **state,
        "messages": messages,
        "resolved_tables": assistant_content
    }

def extract_columns(state):
    logger.info("Starting column extraction")
    resolved_tables = json.loads(state.get("resolved_tables"))
    schema_name = state.get("schema_name","")
    logger.debug(f"Extracting columns for tables: {resolved_tables}")
    
    target_table_list = ','.join(resolved_tables.values())

    result = MetadataExtractor().get_table_columns(
        schema_name=schema_name,
        target_table_list=target_table_list
    )

    logger.info("Column extraction completed")
    logger.debug(f"Extracted columns: {result}")

    messages = state.get("messages", [])
    assistant_content = json.dumps(result, indent=2)
    messages = messages + [{"role": "assistant", "content": assistant_content}]

    return {
        **state,
        "messages": messages,
        "all_columns_from_the_target_tables": assistant_content
    }

def resolve_columns(state):
    logger.info("Starting column resolution")
    business_attributes = state.get("key_columns")
    target_table_columns = json.loads(state.get("all_columns_from_the_target_tables"))
    logger.debug(f"Resolving columns for attributes: {business_attributes}")

    result = ColumnResolverTool().resolve_columns(
        business_attributes=business_attributes,
        target_table_columns=target_table_columns
    )
    logger.info("Column resolution completed")
    logger.debug(f"Resolved columns: {result}")

    messages = state.get("messages", [])
    assistant_content = json.dumps(result, indent=2)
    messages = messages + [{"role": "assistant", "content": assistant_content}]

    return {
        **state,
        "messages": messages,
        "resolved_columns": assistant_content
    }

def generate_sql_query(state):
    logger.info("Starting SQL query generation")
    test_summary = state.get("summary")
    criteria = state.get("key_criteria")
    resolved_tables = json.loads(state.get("resolved_tables"))
    table_hints = ','.join(resolved_tables.values())

    resolved_columns = json.loads(state.get("resolved_columns"))
    column_hints = ','.join(resolved_columns.values())

    join_hints = ""#state.get("key_join_hints")
    schema_name = state.get("schema_name")

    logger.debug(f"Generating SQL with criteria: {criteria}")
    print(f"Generating SQL with criteria: {criteria}")
    print(f"Table hints: {table_hints}")
    print(f"Column hints: {column_hints}")

    result = SQLGenerationTool().generate_sql(
        test_summary=test_summary,
        criteria=criteria,
        table_hints=table_hints,
        column_hints=column_hints,
        join_hints=join_hints,
        schema_name=schema_name
    )
    print(f"Generated SQL: {result}")
    logger.info("SQL query generation completed")
    logger.debug(f"Generated SQL: {result}")

    messages = state.get("messages", [])
    assistant_content = json.dumps(result, indent=2)
    messages = messages + [{"role": "assistant", "content": assistant_content}]

    return {
        **state,
        "messages": messages,   
        "ai_written_sql_query": assistant_content
    }

def format_sql_query(state):
    logger.info("Starting SQL query formatting")
    sql_query = state.get("ai_written_sql_query")
    logger.debug(f"Formatting SQL query: {sql_query}")

    result = SQLFormatterTool().format_sql(sql_query=sql_query)

    messages = state.get("messages", [])
    assistant_content = json.dumps(result, indent=2)
    messages = messages + [{"role": "assistant", "content": assistant_content}]

    return {
        **state,
        "messages": messages,
        "formatted_sql_query": assistant_content
    }

def update_config_to_database(state):
    logger.info("Starting database config update")
    project_id = state.get("project_id")
    test_id = state.get("test_id")
    logger.debug(f"Updating config for project {project_id}, test {test_id}")

    summary = state.get("summary")
    resolved_tables = json.loads(state.get("resolved_tables"))
    resolved_columns = json.loads(state.get("resolved_columns"))
    key_criteria = state.get("key_criteria")
    key_join_hints = "" #state.get("key_join_hints")
    ambiguities = state.get("ambiguities")
    full_state = state
    config = state.get("formatted_sql_query")
    last_updated_by = state.get("last_updated_by")

    result = UpdateConfigToDatabaseTool().update_config_to_database(
        project_id=project_id, 
        test_id=test_id, 
        ai_summary=summary,
        ai_key_tables=json.dumps(resolved_tables),
        ai_key_columns=json.dumps(resolved_columns),
        ai_key_criteria=json.dumps(key_criteria),
        ai_key_join_hints=json.dumps(key_join_hints),
        ai_ambiguities=json.dumps(ambiguities),
        ai_full_state=json.dumps(full_state),
        config=config,  
        last_updated_by=last_updated_by,
        status="Completed"
    )
    logger.info("Database config update completed")
    logger.debug(f"Update result: {result}")


def process_test_case(initial_state):
    logger.info("Starting test case processing")
    logger.debug(f"Initial state: {initial_state}")
    
    # Initialize the graph
    graph = StateGraph(dict)

    #add nodes
    graph.add_node("test_case_summarizer", summarize_test_case)
    graph.add_node("ambiguity_resolver", ambiguity_resolver)
    graph.add_node("all_tables_extractor", extract_tables)
    graph.add_node("table_resolver", resolve_tables)
    graph.add_node("target_columns_extractor", extract_columns)
    graph.add_node("column_resolver", resolve_columns)
    graph.add_node("sql_query_generator", generate_sql_query)
    graph.add_node("sql_query_formatter", format_sql_query)
    graph.add_node("update_config_to_database", update_config_to_database)

    #add edges
    graph.add_edge(START, "test_case_summarizer")
    graph.add_edge("test_case_summarizer", "ambiguity_resolver")
    #graph.add_conditional_edges("test_case_summarizer", ambiguity_resolver, {False: "all_tables_extractor", True: "all_tables_extractor"})
    graph.add_edge("ambiguity_resolver", "all_tables_extractor")
    graph.add_edge("all_tables_extractor", "table_resolver")
    graph.add_edge("table_resolver", "target_columns_extractor")
    graph.add_edge("target_columns_extractor", "column_resolver")
    graph.add_edge("column_resolver", "sql_query_generator")
    graph.add_edge("sql_query_generator", "sql_query_formatter")
    graph.add_edge("sql_query_formatter", "update_config_to_database")
    graph.add_edge("update_config_to_database", END)

    # Compile the graph
    logger.info("Compiling workflow graph")
    orchestrator = graph.compile()
    
    logger.info("Executing workflow")
    result = orchestrator.invoke(initial_state)
    logger.info("Workflow execution completed")
    logger.debug(f"Final result: {result}")

    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Invalid number of arguments")
        sys.exit(1)

    try:
        logger.info("Starting agent execution")
        initial_state = json.loads(sys.argv[1])
        process_test_case(initial_state)
        logger.info("Agent execution completed successfully")
    except json.JSONDecodeError as e:
        
        logger.error(f"Failed to parse JSON input: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)