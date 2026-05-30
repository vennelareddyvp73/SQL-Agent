from pathlib import Path


PROJECT_STRUCTURE = [
    "api/main.py",
    "frontend/app.py",
    "build_graph/graph.py",
    "build_graph/state.py",
    "build_graph/nodes/agent_node.py",
    "build_graph/nodes/tool_node.py",
    "build_graph/tool/list_tables.py",
    "build_graph/tool/get_schema.py",
    "build_graph/tool/query_checker.py",
    "build_graph/tool/run_query.py",
    "models/llm.py",
    "db_ingestion/ingestion.py",
    "notebook/sql_agent.ipynb",
]


def create_file(path: str):
    file_path = Path(path)
    
    if file_path.name == ".gitkeep":
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        print(f"Created Directory: {file_path.parent}/")
        return

    if not file_path.exists():
   
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.touch()
        print(f"Created File: {file_path}")
    else:
        print(f"Skipped (Already Exists): {file_path}")


def generate():
   
    base_path = Path.cwd()

    for file_path in PROJECT_STRUCTURE:
        create_file(str(base_path / file_path))
        
    print("Project structure generated")


if __name__ == "__main__":
    generate()