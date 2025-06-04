from langgraph.graph import StateGraph, START,END
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

def summarize_test_case(input: SummarizerInput):
    result = TestCaseSummarizer().summarize(
        test_case=input.test_case,
        test_description=input.test_description,
        past_user_responses=input.past_user_responses
    )
    
    return result

summarize_tool = StructuredTool(
    name="summarize_test_case",
    func=summarize_test_case,
    description="Summarizes a test case into key tables, columns, criteria, and ambiguities",
    args_schema=SummarizerInput,
)

llm_with_tools = llm.bind_tools([summarize_tool])
agent = create_react_agent(
    model=llm_with_tools, 
    tools=[summarize_tool]
    )


# Define input
input_data = {
    "messages": [
        {
            "role": "system",
            "content": "You are an assistant that provides list of all tables from the database."
        },
        {
            "role": "user",
            "content": (
                "Please summarize the following test case using the SUM_V_101 tool:\n"
                "Test case name: Identify invalid purchase order line amount.\n"
                "Test description: Identify invalid purchase order line amount.\n"
                "Past user responses: Purchase order date between 2025-01-01 and 2025-01-31 and status is not cancelled.\n"
                "Include key tables, columns, criteria, and ambiguities."
            )
        }
    ]
}

# Run the graph
result = agent.invoke(input_data)

print(result)

#print(result)
# Extract AI message (last message)
ai_message = next(msg for msg in result["messages"] if isinstance(msg, AIMessage))

# Print only the content of the AI response
#print("--------------------------------")
print(ai_message.content)
#print("--------------------------------")
