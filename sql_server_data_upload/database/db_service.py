import pandas as pd
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from layer_db_utils.config import Config


class DatabaseService:
    def __init__(self):
        self.connection_string = quote_plus(
            f"DRIVER={Config.DRIVER};"
            f"SERVER={Config.SERVER};"
            f"DATABASE={Config.DATABASE};"
            f"UID={Config.USERNAME};"
            f"PWD={Config.PASSWORD};"
            "Encrypt=yes;TrustServerCertificate=yes;autocommit=True"
        )

    def execute_upload(self, rows, columns, target_table, schema_name):
        df = pd.DataFrame(rows, columns=columns)

        engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={self.connection_string}",
            fast_executemany=True
        )

        df.to_sql(
            name=target_table,
            con=engine,
            schema=schema_name,
            if_exists='append',
            index=False
        )

        return {"status": "success", "rows_inserted": len(df)}
