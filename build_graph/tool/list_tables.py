from langchain_core.tools import BaseTool
from langchain_community.utilities import SQLDatabase


class ListTablesTool(BaseTool):
    """
    Tool to list all available tables in the SQL database.

    This helps the agent understand what tables
    exist before generating SQL queries.
    """

    name: str = "sql_db_list_tables"
    description: str = (
        "Returns all available table names in the database "
        "as a comma-separated string." )
    
    db: SQLDatabase

    def __init__(self, db: SQLDatabase):
        super().__init__(db=db)

    def _run(self, tool_input: str = "", **kwargs) -> str:
        try:
            tables = self.db.get_usable_table_names()

            if not tables:
                return "No tables found in the database."

            return ", ".join(tables)

        except Exception as e:
            return f"Error listing tables: {str(e)}"

if __name__ == "__main__":

    db_path = r"../db_ingestion/Chinook.db"
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    tool = ListTablesTool(db=db)

    result = tool.run("")

    print("\nDatabase Tables:\n")
    print(result)