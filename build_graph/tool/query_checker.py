from langchain_core.tools import BaseTool
from langchain_community.utilities import SQLDatabase
from models.llm import get_llm, HuggingFaceProvider
from langchain_community.tools.sql_database.tool import QuerySQLCheckerTool
from typing import Any

class QueryCheckerTool(BaseTool):
    """
    Tool to validate SQL queries before execution.

    Helps prevent invalid SQL generation.
    """

    name: str = "sql_db_query_checker"

    description: str = (
        "Checks if a SQL query is valid and correct "
        "before execution.")

    db: SQLDatabase
    llm: Any

    def __init__(self, db: SQLDatabase, llm: Any = None):
        if llm is None:
            llm = get_llm(provider=HuggingFaceProvider(), model_id="meta-llama/Llama-3.3-70B-Instruct", temperature=0)
        super().__init__(db=db, llm=llm)

    def _run(self, query: str = "", **kwargs) -> str:
        try:
            if not query:
                query = kwargs.get("sql", kwargs.get("sql_query", ""))
            if not query:
                return "Error: No SQL query specified."
            tool = QuerySQLCheckerTool(db=self.db,llm=self.llm)
            response = tool.run(query)
            return response

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error checking query: {str(e)}"


if __name__ == "__main__":

    db_path = r"../db_ingestion/Chinook.db"
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    tool = QueryCheckerTool(db=db)
    result = tool.run( "SELECT * FORM Artist;")

    print("\nQuery Check:\n")
    print(result)