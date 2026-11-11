# AI-Powered CRM Analytics Assistant

Ask questions about CRM data in everyday language and get read-only SQL results, concise summaries, and charts. The app uses Gemini to classify questions, generate MySQL queries, and summarize results in a Streamlit interface.

## Features

- Natural-language analytics for customers, products, orders, order items, leads, and employees.
- SQL validation that permits a single read-only `SELECT` (including CTEs) against the configured CRM database.
- Read-only MySQL transactions and a 1,000-row result limit.
- Tabular results, concise summaries, and automatically selected Plotly charts.
- Sample CRM schema and data in [`crm.sql`](crm.sql), plus an exploratory notebook in [`crm.ipynb`](crm.ipynb).

## Requirements

- Python 3.10 or later
- MySQL 8.0 or a compatible MySQL server
- A Gemini API key

## Setup

1. Clone the repository and move into the project directory:

   ```shell
   git clone https://github.com/swetha-ev/CRM_GENAI_Project.git
   cd CRM_GENAI_Project
   ```

2. Create and activate a virtual environment, then install the dependencies:

   ```shell
   python -m venv .venv
   ```

   Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   macOS or Linux:

   ```shell
   source .venv/bin/activate
   ```

   ```shell
   python -m pip install -r requirements.txt
   ```

3. Create the sample database. From the project directory, start the MySQL client:

   ```shell
   mysql -u root -p
   ```

   At the MySQL prompt, run:

   ```sql
   SOURCE crm.sql;
   ```

   The script creates the `crm_ai` database and its sample tables and records. Run this initialization with an account allowed to create databases and insert data. The application should use a separate MySQL account with read access to `crm_ai` and permission to inspect its schema.

4. Configure the application. Copy `.env.example` to `.env` and set your Gemini API key and MySQL connection details:

   ```dotenv
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini-3.5-flash

   MYSQL_HOST=127.0.0.1
   MYSQL_PORT=3306
   MYSQL_USER=crm_readonly
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=crm_ai
   ```

   Keep `.env` private; it is excluded from Git. The app also supports Streamlit secrets for deployments.

5. Start the app:

   ```shell
   streamlit run app.py
   ```

   Open the local URL printed by Streamlit in your browser.

## Usage

Choose a suggested question or enter your own, for example:

- “What is the total sales?”
- “Show the top 5 customers by revenue.”
- “How many orders are pending?”
- “Show the number of leads by status.”

The app displays the generated SQL, returned records, and a chart when the results are suitable for visualization. Questions and database schema are sent to Gemini for processing. The app sends a summary of retrieved data to Gemini to generate the written answer.

## Run tests

```shell
python -m unittest discover -s tests -v
```

## Project files

| File | Description |
| --- | --- |
| `app.py` | Streamlit user interface |
| `backend.py` | Gemini integration, SQL validation, and CRM question workflow |
| `database.py` | MySQL connection, schema inspection, and read-only query execution |
| `visualization.py` | Automatic Plotly chart generation |
| `config.py` | Environment and Streamlit secrets configuration |
| `crm.sql` | Sample CRM database schema and data |
| `crm.ipynb` | Exploratory CRM notebook |
| `tests/test_backend.py` | SQL validation and visualization tests |
