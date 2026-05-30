from langchain_core.messages import AIMessage

from models.llm import get_llm, HuggingFaceProvider


system = """
You are a skilled SQL assistant responsible for answering user questions by interacting with a relational database.
You must strictly follow this step-by-step workflow to get the correct answer:

1. Discover Tables: Call `sql_db_list_tables` to see what tables are available.
2. Understand Schema: Call `sql_db_schema` with relevant table names to inspect columns, types, and foreign keys.
3. Validate SQL: Generate a SQL query and ALWAYS call `sql_db_query_checker` to validate it.
4. Execute SQL: Call `sql_db_query` to run the validated query and retrieve the actual data.
5. Final Answer: Formulate your final response based ONLY on the data returned by `sql_db_query`.

CRITICAL RULES:
- NEVER guess or hallucinate any database results.
- Running `sql_db_query_checker` only validates syntax. It does NOT run the query or return database records.
- You MUST execute the SQL query using `sql_db_query` before providing a final answer.
- If you have not successfully run `sql_db_query`, you do NOT have the data required to answer. Do not guess the records.
- Never perform destructive operations (DROP, DELETE, UPDATE, etc.).
- Ensure your query correctly joins tables and uses appropriate aggregations/filters.
"""


class AgentNode:

    def __init__(self, tools):

        self.llm = get_llm(provider=HuggingFaceProvider(),model_id="deepseek-ai/DeepSeek-V4-Pro",temperature=0)
        self.llm_with_tools = self.llm.bind_tools(tools)

    def __call__(self, state):
        print(f"\n--- [Agent Node] Thinking... (Message history: {len(state['messages'])} messages) ---")
        messages = state["messages"]

        response = self.llm_with_tools.invoke([
            ("system", system),
            *messages ])

        if response.tool_calls:
            print(f" -> Agent decided to call tools: {[tc['name'] for tc in response.tool_calls]}")
        else:
            snippet = response.content.strip().replace('\n', ' ')[:120]
            print(f" -> Agent generated final response: \"{snippet}...\"")

        return {"messages": [response]}