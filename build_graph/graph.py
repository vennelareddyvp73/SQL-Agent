from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition

from build_graph.state import AgentState

from build_graph.nodes.agent_node import AgentNode
from build_graph.nodes.tool_node import SQLToolNode

from build_graph.tool.list_tables import ListTablesTool
from build_graph.tool.get_schema import GetSchemaTool
from build_graph.tool.query_checker import QueryCheckerTool
from build_graph.tool.run_query import RunQueryTool

from langchain_core.messages import HumanMessage
from langchain_community.utilities import SQLDatabase
from db_ingestion.ingestion import DatabaseIngestionService



class SQLAgentGraph:

    def __init__(self, db):
        self.tools = [ ListTablesTool(db=db),GetSchemaTool(db=db),QueryCheckerTool(db=db),RunQueryTool(db=db) ]

    def build(self):

        builder = StateGraph(AgentState)
        agent_node = AgentNode(self.tools)

        tool_node = SQLToolNode(self.tools)

        builder.add_node("agent", agent_node)

        builder.add_node("tools", tool_node)
        builder.add_edge(START, "agent")
        builder.add_conditional_edges(
            "agent",
            tools_condition,
            {
                "tools": "tools",
                END: END
            }
        )
        builder.add_edge("tools", "agent")

        return builder.compile()

def create_sql_agent(llm, db):
    """
    Helper function to compile the SQL Agent graph.
    """
    return SQLAgentGraph(db).build()


if __name__ == "__main__":

    db_path = r"postgresql+psycopg2://postgres:password@localhost:5433/customer_support_db"
    db_service = DatabaseIngestionService(source_type="local", source=db_path)
    db = db_service.load_database()

    graph = SQLAgentGraph(db).build()

    response = graph.invoke({

        "messages": [

            HumanMessage(
                content="fetch first 3 rows of first table in the database."
            )
        ]
    })

    print("\nFinal Answer:\n")
    content = response["messages"][-1].content
    print(content)