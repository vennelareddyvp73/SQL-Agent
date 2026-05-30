from abc import ABC, abstractmethod
import os
import requests

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy import inspect, text

from langchain_community.utilities import SQLDatabase



class DatabaseProvider(ABC):
    @abstractmethod
    def get_engine(self) -> Engine:
        pass

class LocalDatabaseProvider(DatabaseProvider):

    SQLITE_EXTENSIONS = (".db", ".sqlite", ".sqlite3")

    def __init__(self, source: str):
        self.source = source

    def _is_sqlite_file(self) -> bool:
        return self.source.endswith(self.SQLITE_EXTENSIONS)

    def _build_connection_string(self) -> str:
        print(f"[DEBUG] LocalDatabaseProvider._build_connection_string self.source='{self.source}'")
        if self._is_sqlite_file():
            if not os.path.exists(self.source):
                raise FileNotFoundError(f"Database file not found: {self.source}")
            conn_str = f"sqlite:///{self.source}"
            print(f"[DEBUG] LocalDatabaseProvider computed sqlite conn_str='{conn_str}'")
            return conn_str
        print(f"[DEBUG] LocalDatabaseProvider returning raw connection_string='{self.source}'")
        return self.source

    def get_engine(self) -> Engine:
        connection_string = self._build_connection_string()
        print(f"[DEBUG] LocalDatabaseProvider.get_engine creating engine for='{connection_string}'")
        return create_engine(connection_string, pool_pre_ping=True)

class URLDatabaseProvider(DatabaseProvider):

    def __init__(self,url: str,download_dir: str = "downloaded_dbs"):
        self.url = url
        self.download_dir = download_dir

    def _download_database(self) -> str:

        os.makedirs(self.download_dir,exist_ok=True)
        filename = self.url.split("/")[-1]
        save_path = os.path.join(self.download_dir,filename)
        response = requests.get(self.url)
        if response.status_code != 200:
            raise Exception("Failed to download database" + f"Status Code: {response.status_code}")
        with open(save_path, "wb") as file:
            file.write(response.content)
        return save_path

    def get_engine(self) -> Engine:
        db_path = self._download_database()
        connection_string = f"sqlite:///{db_path}"
        return create_engine(connection_string,pool_pre_ping=True)


class DatabaseFactory:

    @staticmethod
    def create(source_type: str,source: str) -> DatabaseProvider:

        source_type = source_type.lower()
        if source_type == "local":
            return LocalDatabaseProvider(source=source)
        elif source_type == "url":
            return URLDatabaseProvider(url=source)
        else:
            raise ValueError("Unsupported source type: "+f"{source_type}")


class DatabaseIngestionService:

    def __init__(self,source_type: str,source: str):

        self.provider = DatabaseFactory.create(source_type=source_type,source=source)
        self.engine = self.provider.get_engine()

    def load_database(self) -> SQLDatabase:

        try:
            with self.engine.connect():
                print("Database connected successfully.")
            return SQLDatabase(engine=self.engine)

        except Exception as e:
            import traceback
            print(f"[DEBUG] DatabaseIngestionService.load_database failed with exception:")
            traceback.print_exc()
            raise Exception("Failed to load database: " + f"{str(e)}")




if __name__ == "__main__":

    # LOCAL SQLITE FILE

    # service = DatabaseIngestionService(
    
    #     source_type="local",
    
    #     source=(
    #         "C:/Users/venne/Music/Documents/"
    #         "SQL-Agent/db_ingestion/Chinook.db"
    #     )
    # )


    # POSTGRESQL

    # service = DatabaseIngestionService(

    #     source_type="local",

    #     source=(
    #         "postgresql+psycopg2://postgres:password@localhost:5433/customer_support_db"
    #     )
    # )


    # DOWNLOAD SQLITE DB FROM URL

    service = DatabaseIngestionService(
    
        source_type="url",
        source=(
            "https://github.com/bradleygrant/"
            "sakila-sqlite3/raw/main/sakila_master.db"
        )
    )



    db = service.load_database()
    print("\nDATABASE OBJECT:\n")
    print(db)
    print("\nAVAILABLE TABLES:\n")
    tables = db.get_usable_table_names()
    print(tables)



    inspector = inspect(db._engine)
    table_names = inspector.get_table_names()
    if not table_names:
        print("\nNo tables found in database.")
    else:
        first_table = table_names[0]
        print(f"\nFIRST TABLE:\n{first_table}")

        with db._engine.connect() as connection:
            query = text(f"SELECT * FROM {first_table} LIMIT 5")
            result = connection.execute(query)
            rows = result.fetchall()
            print(f"\nFIRST 5 ROWS FROM {first_table}:\n")
            for row in rows:
                print(row)