# Conversational SQL Agent

A Conversational SQL Agent built using **LangGraph**, **LangChain**, and **FastAPI**, with a **Gradio** web interface. This application allows users to query relational databases in natural language by automatically discovering table schemas, generating and validating SQL queries, and returning data-backed answers.

---

##  Key Features

- **Graph-Based Flow**: Uses LangGraph to implement a stateful control flow that manages the agent decision-making process and tool execution.
- **LLM Provider Support**: Supports local models using **Ollama** and remote models using **Hugging Face** endpoints.
- **Database Ingestion**: Supports local SQLite database files, remote SQLite database downloads, and connection URIs (such as PostgreSQL or MySQL).
- **SQL Query Validation**: Passes generated SQL queries through a checker node to validate syntax before execution.
- **Backend & Frontend Components**: Features a FastAPI backend API and a Gradio chatbot frontend interface.

---

## Project Structure

Here is the layout of the SQL Agent project:

```text
├── api/
│   └── main.py                     # FastAPI application exposing connectivity and query endpoints
├── build_graph/
│   ├── graph.py                    # Orchestrates the LangGraph state machine flow
│   ├── state.py                    # Defines the TypedDict state tracking the conversation history
│   ├── nodes/
│   │   ├── agent_node.py           # Handles LLM reasoning, prompting, and tool binding
│   │   └── tool_node.py            # Executes LLM-chosen tools dynamically
│   └── tool/
│       ├── get_schema.py           # Tool: Inspects schema for specific tables
│       ├── list_tables.py          # Tool: Lists all available database tables
│       ├── query_checker.py        # Tool: Validates SQL syntax and safety checks
│       └── run_query.py            # Tool: Safely executes queries on the database
├── db_ingestion/
│   └── ingestion.py                # Ingestion service for SQLite files, URLs, and DB engines
├── downloaded_dbs/                 # Cache directory for databases downloaded via URLs
├── frontend/
│   └── app.py                      # Gradio web frontend interface
├── models/
│   └── llm.py                      # Singleton manager for Ollama and Hugging Face providers
├── notebook/
│   └── sql_agent.ipynb             # Jupyter Notebook for testing the LangGraph pipeline
├── pyproject.toml                  # Python packaging & dependencies configuration
├── template.py                     # Python script to scaffold/verify the project structure
└── .env                    # Sample environment variables file
```

---

##  ReAct Agent Architecture

The agent is implemented as a ReAct (Reasoning and Acting) loop using a stateful LangGraph workflow:

```mermaid
graph TD
    START([Start]) --> Agent[Agent Node <br> Reasoning / Decision]
    Agent -->|Call Tools| Tools[Tool Node <br> Action Execution]
    Tools --> Agent
    Agent -->|Return Answer| END([End])
```

### Components of the ReAct Loop:

1. **Agent Node (Reasoning)**:
   - Receives the conversation history and guides the flow.
   - Evaluates whether it has enough information to construct a final response. If not, it requests to call one or more of the database tools.

2. **Tool Node (Acting)**:
   - Executes the tool calls requested by the Agent. The available tools include:
     - `sql_db_list_tables`: Lists all available tables in the database.
     - `sql_db_schema`: Retrieves column definitions, data types, and keys for selected tables.
     - `sql_db_query_checker`: Validates the syntax of the generated SQL query before execution.
     - `sql_db_query`: Executes the query against the database and returns the raw rows.

3. **Loop Execution**:
   - The state machine transitions back and forth between the Agent and Tool nodes.
   - Once the Agent node obtains the query results and determines no further actions are needed, it generates a natural language answer and routes the flow to the end state.

---

##  Setup & Installation

### 1. Prerequisites
- **Python**: version `3.13` or higher.
- **uv** (recommended) or **pip**: for dependency management.

### 2. Install Dependencies
Clone the repository and install the dependencies.

Using `uv` (recommended):
```bash
uv sync
```

Or using standard `pip`:
```bash
pip install -r pyproject.toml
```

### 3. Environment Configuration
Create a `.env` file at the root of the project to configure your access keys.

```bash
HF_TOKEN=your_huggingface_api_token_here


SQL_AGENT_API_URL=http://127.0.0.1:8000
```

---

##  Running the Application

To run the complete system, start the **FastAPI Backend** first, followed by the **Gradio Frontend**.

### Step 1: Start the Backend API
The backend exposes connection tests and execution endpoints. Run it using:
```bash
uv run python api/main.py
```
*The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).*

### Step 2: Start the Gradio Web UI
The frontend provides a user-friendly chatbot interface to select and query databases. Run it in a separate terminal using:
```bash
uv run python frontend/app.py
```
*The Web UI will be available at [http://127.0.0.1:7860](http://127.0.0.1:7860).*

---

##  Example Usage

Once the web application is running:
1. Open the web interface in your browser.
2. Under **Source Type**, select `local` or `url`.
3. Provide a path or connection URL in the **Source** field:
   - For a local SQLite database, you can use `notebook/Chinook.db` (or upload one to the `db_ingestion/` directory).
   - Alternatively, use a PostgreSQL connection URI.
4. Click **Connect Database** to verify connection.
5. Enter natural language queries into the chat box, such as:
   - *"Which artist has the most albums?"*
   - *"What are the top 5 longest tracks?"*
   - *"How many invoices were billed in each country?"*
