import pandas as pd
import streamlit as st

import backend
import visualization


st.set_page_config(
    page_title="AI-Powered CRM Analytics Assistant",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 1180px; padding-top: 2rem; }
    .hero {
        padding: 1.7rem 2rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #10243a, #174f66);
        color: #fff;
        margin-bottom: 1.5rem;
    }
    .hero h1 { margin: 0 0 .45rem 0; font-size: 2rem; }
    .hero p { margin: 0; color: #d7e8ef; font-size: 1.05rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>AI-Powered CRM Analytics Assistant</h1>
      <p>Ask a question about your CRM data in everyday language and explore the answer.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("What would you like to know?")
st.caption("Choose an example or type a question about customers, sales, orders, products, or leads.")

examples = [
    "What is the total sales?",
    "How many customers are from Kerala?",
    "Show the top 5 customers by revenue.",
    "Which products have the highest sales?",
    "How many orders are pending?",
    "Show the number of leads by status.",
]

for start in range(0, len(examples), 3):
    columns = st.columns(3)
    for column, example in zip(columns, examples[start : start + 3]):
        if column.button(example, key=f"example_{examples.index(example)}", use_container_width=True):
            st.session_state["question_input"] = example

with st.form("crm_question_form"):
    question = st.text_area(
        "Your question",
        key="question_input",
        height=120,
        placeholder="For example: Show monthly sales for the last six months",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Ask CRM Assistant", type="primary", use_container_width=True)

    if submitted:
        if not question or not question.strip():
            st.error("Please enter a question before submitting.")
        else:
            try:
                with st.spinner("Checking CRM data and preparing your answer..."):
                    st.session_state["crm_response"] = backend.ask_crm_secure(question)
                st.session_state.pop("crm_error", None)
            except backend.CRMAppError as exc:
                st.session_state.pop("crm_response", None)
                st.session_state["crm_error"] = str(exc)

if st.session_state.get("crm_error"):
    st.error(st.session_state["crm_error"])

response = st.session_state.get("crm_response")
if response is not None:
    st.divider()
    st.markdown("### Your question")
    st.write(response.question)

    st.markdown("### Answer")
    if response.answer:
        st.success(response.answer)
    else:
        st.warning(response.answer_error or "An answer could not be generated.")

    if response.dataframe.shape == (1, 1):
        value = response.dataframe.iat[0, 0]
        if pd.api.types.is_number(value):
            st.metric("Result", f"{value:,.2f}" if isinstance(value, float) else f"{value:,}")

    with st.expander("View Generated SQL"):
        st.code(response.sql, language="sql")

    st.markdown("### Data results")
    st.caption(f"{len(response.dataframe):,} record(s) returned")
    if response.truncated:
        st.info("Showing the first 1,000 records. Refine your question to narrow the results.")

    if response.dataframe.empty:
        st.info("No records matched your question.")
    else:
        st.dataframe(
            response.dataframe,
            use_container_width=True,
            hide_index=True,
        )

        figure = visualization.auto_visualize(response.dataframe, response.question)
        if figure is not None:
            st.markdown("### Visualization")
            st.plotly_chart(figure, use_container_width=True)
