# 🧠 Conversational SQL Agent with LangGraph and Chinook Music Database

This project builds a powerful SQL agent that interprets **natural language queries** and executes them against the **Chinook** SQLite music database using **LangChain**, **LangGraph**, and **Qwen 1.7B** LLM from **Ollama**.

The agent is capable of:
- Understanding the database schema
- Generating valid SQL queries
- Validating and correcting them
- Executing the query
- Returning friendly, human-readable answers

---

## 🎯 Project Objective

Enable users to ask questions like:
> “Which artist has the most albums?”  
> “Which genre has the longest average track length?”  

…and receive accurate answers by letting an LLM act as an **autonomous analyst**.

---

## 🧠 Models and Tools Used

| Component            | Tool/Model                          | Description                                      |
|---------------------|-------------------------------------|--------------------------------------------------|
| Language Model       | `qwen3:1.7b`                        | LLM used for reasoning, SQL generation, and QA   |
| LLM Host             | [Ollama](https://ollama.com/)       | Local model hosting backend                      |
| Framework            | [LangChain](https://www.langchain.com/) | Used for agent orchestration and tools        |
| Flow Engine          | [LangGraph](https://www.langgraph.dev/) | State-aware control flow for complex reasoning |
| SQL Toolkit          | `SQLDatabaseToolkit` (LangChain)    | Tools for schema inspection and query execution  |
| Database             | [Chinook SQLite DB](https://github.com/lerocha/chinook-database) | Music store simulation database |

---

## 🎵 The Chinook Dataset

The Chinook database represents a **digital music store** with customers, artists, tracks, albums, genres, and invoices.


### 📂 Sample Table Schema

```text
Artist
├── ArtistId (PK)
└── Name

Album
├── AlbumId (PK)
├── Title
└── ArtistId (FK)

Track
├── TrackId (PK)
├── Name
├── AlbumId (FK)
└── GenreId (FK)
```

## 🔁 Flow of Execution (Agent Logic)

This agent is modeled as a state machine using LangGraph. The process is broken into steps that mimic how a human would query a database.

START

1. List Tables
  
2. Get Table Schema
  
3. Generate SQL Query
  
4. Check SQL Validity
  
5. Run Query
  
6. Generate Answer
  

END


---

## 🧩 What Each Step Does

### 1️⃣ List Tables
- **Tool**: `sql_db_list_tables`  
- **Purpose**: Lists all available tables in the database.  
- **Why?** This gives the LLM an overview of what entities (like `Track`, `Album`, `Genre`, etc.) are available to query.

---

### 2️⃣ Get Table Schema
- **Tool**: `sql_db_schema`  
- **Purpose**: Retrieves the column names, data types, and constraints for only the **relevant tables**.  
- **Why?** Prevents guessing. The agent sees the **actual structure** of the tables it's querying.

---

### 3️⃣ Generate SQL Query
- **Model**: `qwen3:1.7b`  
- **Framework**: LangChain's ReAct-style prompting  
- **Purpose**: The agent constructs a well-formed SQL query tailored to the user’s question, based on schema understanding.

#### 💡 Example:
```sql
SELECT Genre.Name, AVG(Track.Milliseconds) AS AvgDuration
FROM Genre
JOIN Track ON Genre.GenreId = Track.GenreId
GROUP BY Genre.Name
ORDER BY AvgDuration DESC
LIMIT 5;
```

### 4️⃣ Check SQL Query Validity
- Tool: sql_db_query_checker
- Purpose: Ensures the query is valid and executable.
- Failure? ✅ If invalid, the flow loops back to regenerate a fixed query.

### 5️⃣ Run Query
- Tool: sql_db_query
- Purpose: Executes the validated query and returns result rows.

### 6️⃣ Generate Final Answer
- Purpose: Converts the SQL output into a clear, natural-language response.
