from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_community.tools import StructuredTool
from langchain.schema import AIMessage

from ai_agents.models.schema_table_model import SchemaTableInput
from ai_agents.models.summarizer_model import SummarizerInput
from ai_agents.models.table_resolver_model import TableResolverInput
from ai_agents.models.column_resolver_model import ColumnResolverInput
from ai_agents.models.schema_column_model import SchemaColumnInput
from ai_agents.tools.summarizer_tool import TestCaseSummarizer
from ai_agents.tools.metadata_extractor_tool import MetadataExtractor
from ai_agents.tools.table_resolver_tool import TableResolverTool
from ai_agents.tools.column_resolver_tool import ColumnResolverTool

from layer_llm_service.bedrock_langchain_utils import BedrockLangChainService

# Initialize the LLM
llm = BedrockLangChainService().get_llm()

# Initialize the tools
summarizer = TestCaseSummarizer()
metadata_extractor = MetadataExtractor()
table_resolver = TableResolverTool()
column_resolver = ColumnResolverTool()

# Create LangChain tools
tools = [
    StructuredTool(
        name="summarize_test_case",
        func=summarizer.summarize,
        description="""
Generates a structured summary of a test case by analyzing the test case name, description, and previous user responses.

Input:
- test_case_name: str – The name or title of the test case.
- test_description: str – A detailed description of the test case.
- past_user_responses: Optional[str] – Any previous clarifications or user responses relevant to the test case.

Output:
- A dictionary with the following fields:
  - summary: str – A clear and concise summary of the test case.
  - key_tables: List[str] – The main tables involved in the test case.
  - key_columns: List[str] – The main columns mentioned or implied in the test case.
  - key_criteria: List[str] – The main business rules, filters, or conditions being tested.
  - ambiguities: List[str] – Unclear or underspecified parts of the test case that may require clarification.

""",
        args_schema=SummarizerInput
    ),
    StructuredTool(
        name="extract_target_tables",
        func=metadata_extractor.get_schema_tables,
        description="""
        This tool extracts the target table names from the database by passing the schema name. This fetchs all the tables in the schema.
        This can be helpful in resolving the table names to target tables from the key entities identified by the test case summary.
        """,
        args_schema=SchemaTableInput
    ),
    StructuredTool(
        name="resolve_tables",
        func=table_resolver.resolve_tables,
        description="""
        This tool extracts and resolves table names identified by the test case summarizer tool with the target tables fetched by the extract_target_tables tool.
        It returns a JSON object with the following fields:
        - target_tables: A list of the target tables involved in the test case
        - target_columns: A list of the target columns involved in the test case
        - target_relationships: A list of the target relationships between the tables
        """,
        args_schema=TableResolverInput
    ),
    StructuredTool(
        name="extract_target_columns",
        func=metadata_extractor.get_table_columns,
        description="""
        This tool extracts the target columns from the database by passing the table name. This fetchs all the columns in the table.
        This can be helpful in resolving the column names to target columns from the key entities identified by the test case summary.
        It returns a JSON object with the following fields:
        - target_tables: A list of the target tables involved in the test case
        - target_columns: A list of the target columns involved in the test case
        """,
        args_schema=SchemaColumnInput
    ),
    StructuredTool(
        name="resolve_columns",
        func=column_resolver.resolve_columns,
        description="""
        This tool resolves the business attributes to the target table columns. 
        It returns a JSON object with the following fields:
        - business_attributes: A list of the business attributes involved in the test case
        - target_columns: A list of the target columns involved in the test case.
        """,
        args_schema=ColumnResolverInput
    )
]

# Create the ReAct agent node
agent_node = create_react_agent(
    model=llm, 
    tools=tools
)

# Define the graph structure
graph_builder = StateGraph(dict)
graph_builder.add_node("agent", agent_node)
graph_builder.set_entry_point("agent")
graph_builder.add_edge("agent", END)

# Compile the graph
graph_app = graph_builder.compile()

# Define input
input_data = {
    "messages": [
        {"role": "user", "content": "test_case: Idenitfy invalid purchase order line amount."},
        {"role": "user", "content": "test_description: Idenitfy invalid purchase order line amount."},
        {"role": "user", "content": "schema_name: p2p"},
        {"role": "user", "content": "GENERATE A STRUCTURED SUMMARY OF THE ABOVE TEST CASE."},
    ]
}
# Run the graph
result = graph_app.invoke(input_data)

#print(result)
# Extract AI message (last message)
ai_message = next(msg for msg in result["messages"] if isinstance(msg, AIMessage))

# Print only the content of the AI response
#print("--------------------------------")
print(ai_message.content)
#print("--------------------------------")
