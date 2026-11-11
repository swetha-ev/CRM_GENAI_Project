from dataclasses import dataclass

import pandas as pd
import pymysql
from pymysql.connections import Connection

from config import get_setting


class DatabaseConfigurationError(RuntimeError):
    """Raised when required MySQL configuration is missing."""


class DatabaseError(RuntimeError):
    """Raised when a MySQL operation cannot be completed."""


@dataclass
class QueryResult:
    dataframe: pd.DataFrame
    truncated: bool = False


MAX_RESULT_ROWS = 1000


def get_connection() -> Connection:
    password = get_setting("MYSQL_PASSWORD")
    if password is None:
        raise DatabaseConfigurationError(
            "MySQL is not configured. Set MYSQL_PASSWORD in your environment "
            "or Streamlit secrets."
        )

    try:
        port = int(get_setting("MYSQL_PORT", "3306") or "3306")
    except ValueError as exc:
        raise DatabaseConfigurationError("MYSQL_PORT must be a valid port number.") from exc

    try:
        return pymysql.connect(
            host=get_setting("MYSQL_HOST", "127.0.0.1"),
            port=port,
            user=get_setting("MYSQL_USER", "root"),
            password=password,
            database=get_setting("MYSQL_DATABASE", "crm_ai"),
            charset="utf8mb4",
            connect_timeout=10,
            read_timeout=30,
            write_timeout=30,
            autocommit=False,
        )
    except pymysql.MySQLError as exc:
        raise DatabaseError(
            "Could not connect to the CRM database. Check that MySQL is running "
            "and the connection settings are correct."
        ) from exc


def _read_metadata(query: str, database: str) -> list[tuple]:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (database,))
            return cursor.fetchall()
    except pymysql.MySQLError as exc:
        raise DatabaseError(
            "Could not retrieve the CRM database schema. Check the database "
            "name and the account's metadata permissions."
        ) from exc
    finally:
        connection.close()


def get_schema() -> str:
    database = get_setting("MYSQL_DATABASE", "crm_ai") or "crm_ai"
    rows = _read_metadata(
        """
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = %s
        ORDER BY table_name, ordinal_position
        """,
        database,
    )

    lines: list[str] = []
    current_table: str | None = None
    for table, column, data_type, nullable in rows:
        if current_table != table:
            lines.append(f"\nTABLE: {table}")
            current_table = table
        lines.append(f"  {column} ({data_type}) NULLABLE={nullable}")
    return "\n".join(lines)


def get_relationships() -> str:
    database = get_setting("MYSQL_DATABASE", "crm_ai") or "crm_ai"
    rows = _read_metadata(
        """
        SELECT table_name, column_name, referenced_table_name,
               referenced_column_name
        FROM information_schema.key_column_usage
        WHERE table_schema = %s
          AND referenced_table_name IS NOT NULL
        ORDER BY table_name, column_name
        """,
        database,
    )
    relationships = ["\nRELATIONSHIPS:"]
    relationships.extend(
        f"{table}.{column} --> {referenced_table}.{referenced_column}"
        for table, column, referenced_table, referenced_column in rows
    )
    return "\n".join(relationships)


def build_context() -> str:
    return f"{get_schema()}{get_relationships()}"


def execute_read_query(sql: str) -> QueryResult:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("START TRANSACTION READ ONLY")
            cursor.execute(sql)
            columns = [description[0] for description in cursor.description or ()]
            rows = cursor.fetchmany(MAX_RESULT_ROWS + 1)
            connection.rollback()
    except pymysql.MySQLError as exc:
        connection.rollback()
        raise DatabaseError(
            "The database could not run this query. The query may reference "
            "an unknown field or contain an unsupported operation."
        ) from exc
    finally:
        connection.close()

    truncated = len(rows) > MAX_RESULT_ROWS
    return QueryResult(
        dataframe=pd.DataFrame(rows[:MAX_RESULT_ROWS], columns=columns),
        truncated=truncated,
    )
