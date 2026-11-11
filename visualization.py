import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def auto_visualize(dataframe: pd.DataFrame, user_query: str) -> go.Figure | None:
    if dataframe is None or dataframe.empty or len(dataframe) <= 1:
        return None

    chart_data = dataframe.copy()
    numeric_columns: list[str] = []
    for column in chart_data.columns:
        converted = pd.to_numeric(chart_data[column], errors="coerce")
        if converted.notna().sum() == len(chart_data) and not str(column).lower().endswith("id"):
            chart_data[column] = converted
            numeric_columns.append(column)

    if not numeric_columns:
        return None

    category_columns = [
        column
        for column in chart_data.columns
        if column not in numeric_columns
        and (
            pd.api.types.is_object_dtype(chart_data[column])
            or pd.api.types.is_categorical_dtype(chart_data[column])
            or pd.api.types.is_datetime64_any_dtype(chart_data[column])
        )
    ]
    if not category_columns:
        return None

    x_column = category_columns[0]
    y_column = numeric_columns[0]
    question = user_query.lower()
    if any(word in question for word in ("share", "distribution", "proportion", "breakdown")):
        fig = px.pie(
            chart_data,
            names=x_column,
            values=y_column,
            title=f"Distribution: {user_query}",
        )
    elif any(word in str(x_column).lower() for word in ("date", "created", "month", "year")):
        fig = px.line(
            chart_data,
            x=x_column,
            y=y_column,
            markers=True,
            title=f"Trend: {user_query}",
        )
    else:
        fig = px.bar(
            chart_data,
            x=x_column,
            y=y_column,
            text_auto=True,
            title=f"Results: {user_query}",
        )

    fig.update_layout(
        template="plotly_white",
        xaxis_title=str(x_column).replace("_", " ").title(),
        yaxis_title=str(y_column).replace("_", " ").title(),
        legend_title_text=str(x_column).replace("_", " ").title(),
        xaxis_tickangle=-35,
        margin={"t": 70, "b": 70},
    )
    return fig
