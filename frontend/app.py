import os
import requests
import gradio as gr

API_URL = os.environ.get("SQL_AGENT_API_URL", "http://127.0.0.1:8000")

def get_databases():
    try:
        r = requests.get(f"{API_URL}/api/databases", timeout=5)
        if r.status_code == 200:
            return r.json().get("databases", [])
    except Exception as e:
        print(f"Error fetching databases: {e}")
    return []

def query_agent(question, history, source_type, source):
    if not source:
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": " Please select, upload, or specify a database first."})
        return history
        
    try:
        payload = {
            "source_type": source_type,
            "source": source,
            "question": question
        }
        r = requests.post(f"{API_URL}/api/query", json=payload, timeout=1200)
        if r.status_code == 200:
            answer = r.json().get("answer", "No answer received.")
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": answer})
        else:
            try:
                err_msg = r.json().get("detail", r.text)
            except:
                err_msg = r.text
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": f"❌ Error: {err_msg}"})
    except Exception as e:
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": f"❌ Failed to connect to backend: {str(e)}"})
        
    return history

with gr.Blocks(title="SQL Agent") as demo:
    gr.Markdown("#  SQL Agent Chatbot")
    gr.Markdown("Configure your database connection source and query it with Natural Language.")
    
    with gr.Row():
        source_type = gr.Radio(
            choices=["local", "url"],
            value="local",
            label="Source Type"
        )
        
    with gr.Row():
        source = gr.Textbox(
            label="Source",
            placeholder="Enter file path (e.g. Chinook.db) or connection URI (e.g. postgresql+psycopg2://...)",
            scale=4
        )
        connect_btn = gr.Button("Connect Database", scale=1)
        
    status_output = gr.Markdown(value="*Status: Not connected*")
    
    def update_placeholder(choice):
        if choice == "local":
            return gr.Textbox(placeholder="Enter file path (e.g. Chinook.db) or connection URI (e.g. postgresql+psycopg2://...)")
        else:
            return gr.Textbox(placeholder="Enter public download URL (e.g. https://.../Chinook.db)")
            
    source_type.change(
        fn=update_placeholder,
        inputs=[source_type],
        outputs=[source]
    )
    
    def test_db_connection(source_type, source):
        if not source.strip():
            return " Please enter a source first."
        try:
            payload = {"source_type": source_type, "source": source}
            r = requests.post(f"{API_URL}/api/connect", json=payload, timeout=30)
            if r.status_code == 200:
                return f" {r.json().get('message', 'Database connected successfully.')}"
            else:
                try:
                    err = r.json().get("detail", r.text)
                except:
                    err = r.text
                return f" Connection failed: {err}"
        except Exception as e:
            return f" Failed to connect to backend: {str(e)}"
            
    connect_btn.click(
        fn=test_db_connection,
        inputs=[source_type, source],
        outputs=[status_output]
    )
        
    chatbot = gr.Chatbot(label="Chatbot History")
    
    with gr.Row():
        textbox = gr.Textbox(
            placeholder="Type your question here (e.g., Which artist has the most albums?)...",
            label="Enter Question",
            scale=4
        )
        submit_btn = gr.Button("Submit", scale=1)
        
    def handle_submit(question, history, source_type, source):
        if not question.strip():
            return "", history
            
        new_history = query_agent(question, history, source_type, source)
        return "", new_history

    submit_btn.click(
        fn=handle_submit,
        inputs=[textbox, chatbot, source_type, source],
        outputs=[textbox, chatbot]
    )
    
    textbox.submit(
        fn=handle_submit,
        inputs=[textbox, chatbot, source_type, source],
        outputs=[textbox, chatbot]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
