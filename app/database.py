import pyodbc

from app.config import config

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={config.db_hostname};"
    f"DATABASE={config.db_name};"
    f"UID={config.db_username};"
    f"PWD={config.db_password}"
)


def get_db():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        yield cursor
    finally:
        cursor.close()
        conn.close()
