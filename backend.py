import json
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import httpx
import pandas as pd
from google import genai
from google.genai import errors
from sqlglot.errors import ParseError
from sqlglot import exp, parse

import database
from config import get_setting


MODEL_NAME = get_setting("GEMINI_MODEL", "gemini-3.5-flash-lite") or "gemini-3.5-flash-lite"
BLOCKED_FUNCTIONS = {
    "BENCHMARK",
    "GET_LOCK",
    "LOAD_FILE",
    "RELEASE_ALL_LOCKS",
    "RELEASE_LOCK",
    "SLEEP",
}
SENSITIVE_COLUMNS = ("name", "email", "phone", "address")


class CRMAppError(RuntimeError):
    """Base class for errors that can be presented safely in the interface."""


class GeminiServiceError(CRMAppError):
    pass


class UnsupportedQuestionError(CRMAppError):
    pass


class SQLValidationError(CRMAppError):
    pass


class QueryExecutionError(CRMAppError):
    pass


@dataclass
class CRMResponse:
    question: str
    sql: str
    dataframe: pd.DataFrame
    answer: str | None
    answer_error: str | None = None
    truncated: bool = False


@dataclass
class ExecutionResult:
    query_result: database.QueryResult
    sql: str


@lru_cache(maxsize=1)
def _gemini_client() -> genai.Client:
    api_key = get_setting("GEMINI_API_KEY")
    if not api_key:
        raise GeminiServiceError(
            "Gemini is not configured. Set GEMINI_API_KEY in your environment "
            "or Streamlit secrets."
        )
    return genai.Client(api_key=api_key)


def _generate_content(prompt: str) -> str:
    try:
        response = _gemini_client().models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
    except (errors.APIError, httpx.HTTPError) as exc:
        print("Gemini Error Type:", type(exc).__name__)
        print("Gemini Error Details:", str(exc))

        raise GeminiServiceError(
        f"Gemini API Error: {str(exc)}"
    ) from exc
    '''except (errors.APIError, httpx.HTTPError) as exc:
        raise GeminiServiceError(
            "Gemini could not process the request. Check the API key and network "
            "connection, then try again."
        ) from exc'''

    if not response.text or not response.text.strip():
        raise GeminiServiceError("Gemini returned an empty response. Please try again.")
    return response.text.strip()


def _remove_code_fence(text: str) -> str:
    return re.sub(r"^\s*```(?:sql)?\s*|\s*```\s*$", "", text, flags=re.IGNORECASE).strip()


def classify_intent(user_query: str) -> bool:
    prompt = f"""
You are an intent router for a read-only CRM analytics assistant.
The CRM covers customers, products, orders, order items, leads, and employees.
Classify whether the question asks to retrieve, summarize, or analyze these CRM
data or related business metrics. Requests to change data, run commands, or
perform unrelated tasks are not allowed.
Return only YES or NO.

Question:
<question>
{user_query}
</question>
"""
    response = _generate_content(prompt).strip().upper()
    if response not in {"YES", "NO"}:
        raise GeminiServiceError("Gemini could not classify that question. Please rephrase it.")
    return response == "YES"


def build_context() -> str:
    try:
        return database.build_context()
    except database.DatabaseConfigurationError as exc:
        raise CRMAppError(str(exc)) from exc
    except database.DatabaseError as exc:
        raise CRMAppError(str(exc)) from exc


def generate_sql(user_question: str, schema_context: str | None = None) -> str:
    context = schema_context if schema_context is not None else build_context()
    prompt = f"""
You are an expert MySQL developer writing read-only CRM analytics queries.
Use only the database schema and relationships below.
Return exactly one executable MySQL SELECT statement (a WITH ... SELECT is
allowed). Never return DDL, DML, stored procedures, multiple statements,
comments, markdown, or explanations. Use joins when required.

DATABASE SCHEMA AND RELATIONSHIPS:
{context}

USER QUESTION:
<question>
{user_question}
</question>
"""
    return _remove_code_fence(_generate_content(prompt))


def validate_sql(sql: str) -> bool:
    if not sql or not sql.strip():
        raise SQLValidationError("Gemini did not generate a query. Please try again.")

    try:
        statements = parse(sql, read="mysql")
    except (ParseError, ValueError, TypeError) as exc:
        raise SQLValidationError("The generated query was not valid MySQL.") from exc

    if len(statements) != 1 or statements[0] is None:
        raise SQLValidationError("Only one read-only query can be run at a time.")

    query = statements[0]
    if not isinstance(query, exp.Query):
        raise SQLValidationError("Only read-only SELECT queries are allowed.")

    tables = list(query.find_all(exp.Table))
    if not tables:
        raise SQLValidationError("The query must read from CRM data.")

    crm_database = (get_setting("MYSQL_DATABASE", "crm_ai") or "crm_ai").casefold()
    for table in tables:
        if table.catalog or (table.db and table.db.casefold() != crm_database):
            raise SQLValidationError("Queries may only read from the configured CRM database.")

    if any(node.key.lower() in {"into", "lock"} for node in query.walk()):
        raise SQLValidationError(
            "Queries that write files or lock database records are not allowed."
        )

    for function in query.find_all(exp.Func):
        name = (
            function.name.upper()
            if isinstance(function, exp.Anonymous)
            else function.sql_name().upper()
        )
        if name in BLOCKED_FUNCTIONS:
            raise SQLValidationError("This query contains a restricted SQL function.")

    return True


def explain_error(user_query: str, sql: str, error: str) -> str:
    prompt = f"""
You are a CRM assistant. Explain briefly in simple business language why this
read-only CRM question could not be answered. Do not expose SQL, credentials,
stack traces, or technical database details, and suggest how to rephrase it.

Question: {user_query}
Failed query (for diagnosis only; do not include it in the answer): {sql}
Query failure: {error}
"""
    return _generate_content(prompt)


def execute_sql_with_retry(
    sql: str,
    user_query: str,
    max_retries: int = 2,
    schema_context: str | None = None,
) -> ExecutionResult:
    current_sql = sql
    for attempt in range(max_retries + 1):
        validate_sql(current_sql)
        try:
            return ExecutionResult(
                query_result=database.execute_read_query(current_sql),
                sql=current_sql,
            )
        except database.DatabaseConfigurationError as exc:
            raise CRMAppError(str(exc)) from exc
        except database.DatabaseError as exc:
            error_detail = str(exc.__cause__) if exc.__cause__ is not None else str(exc)
            if attempt == max_retries:
                try:
                    explanation = explain_error(user_query, current_sql, error_detail)
                except GeminiServiceError as gemini_error:
                    raise QueryExecutionError(
                        "The CRM query could not be completed, and Gemini is "
                        "currently unavailable to explain the issue."
                    ) from gemini_error
                raise QueryExecutionError(explanation) from exc

            correction_prompt = f"""
You are correcting a failed, read-only MySQL CRM analytics query.
Return exactly one SELECT statement (WITH ... SELECT is allowed), with no
markdown, comments, or explanation. Never generate data-changing statements.

CRM schema and relationships:
{schema_context or ""}

User question:
{user_query}

Failed query:
{current_sql}

Failure:
{error_detail}
"""
            current_sql = _remove_code_fence(_generate_content(correction_prompt))

    raise QueryExecutionError("The CRM query could not be completed.")


def _answer_facts(dataframe: pd.DataFrame) -> dict[str, Any]:
    facts: dict[str, Any] = {"record_count": len(dataframe), "columns": list(dataframe.columns)}
    numeric: dict[str, dict[str, float | int]] = {}
    categories: dict[str, dict[str, int]] = {}

    for column in dataframe.columns:
        lowered = str(column).lower()
        if any(sensitive in lowered for sensitive in SENSITIVE_COLUMNS):
            continue

        values = dataframe[column]
        converted = pd.to_numeric(values, errors="coerce")
        if converted.notna().any() and not lowered.endswith("id"):
            numeric[str(column)] = {
                "sum": float(converted.sum()),
                "min": float(converted.min()),
                "max": float(converted.max()),
            }
        elif values.dtype == object:
            top_values = values.astype(str).value_counts().head(8)
            if not top_values.empty:
                categories[str(column)] = {
                    str(value): int(count) for value, count in top_values.items()
                }

    facts["numeric_summary"] = numeric
    facts["category_counts"] = categories
    return facts


def generate_answer(user_question: str, dataframe: pd.DataFrame) -> str:
    facts = json.dumps(_answer_facts(dataframe), default=str)
    prompt = f"""
You are a concise CRM analytics assistant. Answer the user's question in clear,
simple business language using only the facts provided. Do not invent values.
If the facts are insufficient for a narrative, state how many records were
returned and direct the user to the results table. Keep the answer to two
sentences or fewer. Do not include SQL.

Question: {user_question}
Retrieved-data summary:
{facts}
"""
    return _generate_content(prompt)


def ask_crm_secure(question: str) -> CRMResponse:
    question = question.strip()
    if not question:
        raise UnsupportedQuestionError("Enter a question about your CRM data.")
    if not classify_intent(question):
        raise UnsupportedQuestionError(
            "I can help analyze CRM customers, products, orders, leads, and employees."
        )

    context = build_context()
    sql = generate_sql(question, context)
    validate_sql(sql)
    execution = execute_sql_with_retry(
        sql,
        question,
        schema_context=context,
    )
    result = execution.query_result

    answer: str | None
    answer_error: str | None = None
    try:
        answer = generate_answer(question, result.dataframe)
    except GeminiServiceError:
        answer = None
        answer_error = (
            "The query succeeded, but Gemini could not generate a written summary. "
            "The retrieved records are shown below."
        )

    return CRMResponse(
        question=question,
        sql=execution.sql,
        dataframe=result.dataframe,
        answer=answer,
        answer_error=answer_error,
        truncated=result.truncated,
    )
