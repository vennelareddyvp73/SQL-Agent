from langchain_core.tools import BaseTool
from langchain_community.utilities import SQLDatabase


class GetSchemaTool(BaseTool):
    """
    Tool to fetch schema information for tables.

    Helps the agent understand table columns,
    relationships, and sample rows.
    """

    name: str = "sql_db_schema"
    description: str = (
        "Input should be comma-separated table names. "
        "Returns schema and sample rows for those tables.")

    db: SQLDatabase

    def __init__(self, db: SQLDatabase):
        super().__init__(db=db)

    def _run(self, table_names: str = "", **kwargs) -> str:
        try:
            if not table_names:
                table_names = kwargs.get("tables", kwargs.get("table", ""))
            if not table_names:
                return "Error: No table names specified."
            schema = self.db.get_table_info(table_names.split(","))
            return schema

        except Exception as e:
            return f"Error getting schema: {str(e)}"


if __name__ == "__main__":

    db_path = r"../db_ingestion/Chinook.db"
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    tool = GetSchemaTool(db=db)
    result = tool.run("Artist,Album")

    print("\nSchema:\n")
    print(result)