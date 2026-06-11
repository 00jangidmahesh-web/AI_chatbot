from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from langgraph_rag_backend import (
    chatbot,
    ingest_pdf,
    retrieve_all_threads,
    get_thread_messages,  # Naya helper method history load karne ke liye
)

app = FastAPI()

# React frontend CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
def chat(message: str, thread_id: str):
    try:
        CONFIG = {
            "configurable": {"thread_id": thread_id}
        }

        response = chatbot.invoke(
            {"messages": [HumanMessage(content=message)]},
            config=CONFIG
        )

        final_response = response["messages"][-1].content
        return {"response": final_response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat Error: {str(e)}")


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    thread_id: str = Form(...)
):
    try:
        file_bytes = await file.read()

        summary = ingest_pdf(
            file_bytes=file_bytes,
            thread_id=thread_id,
            filename=file.filename
        )

        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Error: {str(e)}")


@app.get("/threads")
def get_threads():
    try:
        return {"threads": retrieve_all_threads()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/thread/{thread_id}/messages")
def get_messages(thread_id: str):
    """
    Frontend jab kisi thread par click karega ya page refresh hoga,
    toh yeh endpoint us specific thread ki saari puraani chat history return karega.
    """
    try:
        messages = get_thread_messages(thread_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")