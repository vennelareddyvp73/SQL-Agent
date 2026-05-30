import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List

from build_graph.graph import create_sql_agent
from db_ingestion.ingestion import DatabaseIngestionService
from langchain_core.messages import HumanMessage

app = FastAPI(title="SQL Agent API")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db_ingestion")

class QueryRequest(BaseModel):
    source_type: str
    source: str
    question: str

class ConnectRequest(BaseModel):
    source_type: str
    source: str

@app.get("/api/databases")
def get_databases():
    """List available databases in the db_ingestion folder."""
    if not os.path.exists(DB_DIR):
        return {"databases": []}
    files = os.listdir(DB_DIR)
    db_files = [f for f in files if f.endswith(('.db', '.sqlite', '.sqlite3'))]
    return {"databases": sorted(db_files)}

@app.post("/api/upload")
def upload_db(file: UploadFile = File(...)):
    """Upload a database file to the db_ingestion folder."""
    if not file.filename.endswith(('.db', '.sqlite', '.sqlite3')):
        raise HTTPException(status_code=400, detail="Only SQLite database files (.db, .sqlite, .sqlite3) are allowed")
    
    os.makedirs(DB_DIR, exist_ok=True)
    file_path = os.path.join(DB_DIR, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/connect")
def test_connection(request: ConnectRequest):
    """Test connection to the database."""
    source_type = request.source_type
    source = request.source
    print(f"[DEBUG] API.test_connection: source_type='{source_type}', source='{source}'")
    
    if source_type == "local" and source.endswith(('.db', '.sqlite', '.sqlite3')) and not os.path.isabs(source) and "://" not in source:
        source = os.path.join(DB_DIR, source)
        print(f"[DEBUG] API.test_connection resolved sqlite source='{source}'")
        
    try:
        db_service = DatabaseIngestionService(source_type=source_type, source=source)
        db_service.load_database()
        return {"status": "success", "message": "Database connected successfully."}
    except Exception as e:
        import traceback
        print("[DEBUG] API.test_connection failed with exception:")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/query")
def run_query(request: QueryRequest):
    """Execute query using SQL Agent graph and return the text response."""
    source_type = request.source_type
    source = request.source
    print(f"[DEBUG] API.run_query: source_type='{source_type}', source='{source}', question='{request.question}'")
    
    if source_type == "local" and source.endswith(('.db', '.sqlite', '.sqlite3')) and not os.path.isabs(source) and "://" not in source:
        source = os.path.join(DB_DIR, source)
        print(f"[DEBUG] API.run_query resolved sqlite source='{source}'")
        
    try:
        db_service = DatabaseIngestionService(source_type=source_type, source=source)
        db = db_service.load_database()
        
        graph = create_sql_agent(llm=None, db=db)
        
        response = graph.invoke({"messages": [HumanMessage(content=request.question)]})
        final_answer = response["messages"][-1].content
        return {"answer": final_answer}
        
    except Exception as e:
        import traceback
        print("[DEBUG] API.run_query failed with exception:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
