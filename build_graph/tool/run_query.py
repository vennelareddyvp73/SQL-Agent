from langchain_core.tools import BaseTool
from langchain_community.utilities import SQLDatabase


class RunQueryTool(BaseTool):
    """
    Tool to execute SQL queries on the database.

    Used by the agent to fetch final answers
    from the database.
    """

    name: str = "sql_db_query"

    description: str = "Executes a SQL query and returns the result."

    db: SQLDatabase
    def __init__(self, db: SQLDatabase):
        super().__init__(db=db)

    def _run(self, query: str = "", **kwargs) -> str:
        try:
            if not query:
                query = kwargs.get("sql", kwargs.get("sql_query", ""))
            if not query:
                return "Error: No SQL query specified."
            result = self.db.run(query)

            return str(result)

        except Exception as e:
            return f"Error executing query: {str(e)}"


if __name__ == "__main__":

    db_path = r"../db_ingestion/Chinook.db"
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    tool = RunQueryTool(db=db)
    result = tool.run("SELECT * FROM Artist LIMIT 5;")
    print("\nQuery Result:\n")
    print(result)