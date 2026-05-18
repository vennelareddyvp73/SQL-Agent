from abc import ABC, abstractmethod
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


class DatabaseProvider(ABC):

    @abstractmethod
    def get_engine(self) -> Engine:
        pass


class URLDatabaseProvider(DatabaseProvider):

    def __init__(self, db_url: str):
        self.db_url = db_url

    def get_engine(self) -> Engine:

        return create_engine(
            self.db_url,
            pool_pre_ping=True
        )



class FileDatabaseProvider(DatabaseProvider):

    SUPPORTED_EXTENSIONS = [".db", ".sqlite", ".sqlite3"]

    def __init__(self, file_path: str):
        self.file_path = file_path

    def validate_file(self):

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"File not found: {self.file_path}"
            )

        extension = os.path.splitext(
            self.file_path
        )[1]

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

    def get_engine(self) -> Engine:

        self.validate_file()

        db_url = f"sqlite:///{self.file_path}"

        return create_engine(
            db_url,
            pool_pre_ping=True
        )



class DatabaseFactory:

    @staticmethod
    def create(
        source_type: str,
        value: str
    ) -> DatabaseProvider:

        source_type = source_type.lower()

        if source_type == "url":
            return URLDatabaseProvider(value)

        elif source_type == "file":
            return FileDatabaseProvider(value)

        else:
            raise ValueError(
                f"Unsupported source type: {source_type}"
            )


class DatabaseIngestionService:

    def __init__(
        self,
        source_type: str,
        value: str
    ):

        provider = DatabaseFactory.create(
            source_type,
            value
        )

        self.engine = provider.get_engine()

    def load_database(self):

        try:

            with self.engine.connect() as connection:
                print("Database loaded successfully")

            return self.engine

        except Exception as e:
            raise Exception(
                f"Failed to load database: {e}"
            )




if __name__ == "__main__":



    service = DatabaseIngestionService(
        source_type="url",
        value="sqlite:///sample.db"
    )


    # OPTION 2 -> DATABASE FILE

    # service = DatabaseIngestionService(
    #     source_type="file",
    #     value="sample.db"
    # )

    engine = service.load_database()

    print(engine)