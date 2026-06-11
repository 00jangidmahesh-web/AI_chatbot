from __future__ import annotations

import os
import sqlite3
import shutil
from typing import Annotated, Any, Dict, Optional, TypedDict

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import requests

load_dotenv()

# Vector stores save karne ke liye ek local folder declare karein
VECTOR_STORE_DIR = "stored_vectors"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# -------------------
# 1. LLM + embeddings
# -------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# -------------------
# 2. Local FAISS Storage Strategy (Persistent)
# -------------------
def _get_thread_vector_path(thread_id: str) -> str:
    return os.path.join(VECTOR_STORE_DIR, f"thread_{thread_id}")

def _get_retriever_for_thread(thread_id: Optional[str]):
    """Fetch the retriever from disk for a specific thread."""
    if not thread_id:
        return None
    
    db_path = _get_thread_vector_path(thread_id)
    if os.path.exists(db_path):
        try:
            # Dangerous deserialization true karna safe hai kyunki hum khud generate kar rahe hain local filesystem par
            vector_store = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
            return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
        except Exception as e:
            print(f"Error loading vector store for thread {thread_id}: {e}")
            return None
    return None


def ingest_pdf(file_bytes: bytes, thread_id: str, filename: Optional[str] = None) -> dict:
    """Builds a FAISS retriever, persists it to disk under the thread directory."""
    if not file_bytes:
        raise ValueError("No bytes received for ingestion.")

    # PDF temporary save karna read karne ke liye
    temp_path = f"temp_{thread_id}.pdf"
    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(docs)

        # Vector store generate karna aur disk par write karna
        vector_store = FAISS.from_documents(chunks, embeddings)
        db_path = _get_thread_vector_path(thread_id)
        vector_store.save_local(db_path)

        # Metadata handle karne ke liye (Aap isko SQLite database mein bhi log kar sakte hain aur better reliability ke liye)
        metadata = {
            "filename": filename or "Unknown PDF",
            "documents": len(docs),
            "chunks": len(chunks),
        }
        return metadata

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# -------------------
# 3. Tools Implementation
# -------------------
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """Perform a basic arithmetic operation on two numbers. Supported operations: add, sub, mul, div"""
    try:
        if operation == "add": result = first_num + second_num
        elif operation == "sub": result = first_num - second_num
        elif operation == "mul": result = first_num * second_num
        elif operation == "div":
            if second_num == 0: return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else: return {"error": f"Unsupported operation '{operation}'"}
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_stock_price(symbol: str) -> dict:
    """Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA')."""
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    try:
        r = requests.get(url)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

@tool
def rag_tool(query: str, config: RunnableConfig) -> dict:
    """
    Retrieve relevant information from the uploaded PDF for this chat thread.
    LLM don't need to pass thread_id, it is automatically fetched contextually.
    """
    # Active thread_id direct config parameters se fetch hoga bina LLM dependency ke
    thread_id = config.get("configurable", {}).get("thread_id")
    
    retriever = _get_retriever_for_thread(thread_id)
    if retriever is None:
        return {
            "error": "No document indexed for this chat. Please instruct the user to upload a PDF first.",
            "query": query,
        }

    result = retriever.invoke(query)
    context = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        "query": query,
        "context": context,
        "metadata": metadata
    }


tools = [search_tool, get_stock_price, calculator, rag_tool]
llm_with_tools = llm.bind_tools(tools)

# -------------------
# 4. State & Graph
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState, config: RunnableConfig = None):
    system_message = SystemMessage(
        content=(
            "You are an advanced helpful AI Assistant. For questions related to documents, "
            "trigger the `rag_tool` directly. You do not need to invent or supply a thread_id parameter. "
            "Use web search, stock price API, or calculator tools whenever required to handle analytical tasks."
        )
    )
    messages = [system_message, *state["messages"]]
    response = llm_with_tools.invoke(messages, config=config)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# Checkpointer Setup
conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 5. Helpers & Persistence API getters
# -------------------
def retrieve_all_threads():
    all_threads = set()
    try:
        for checkpoint in checkpointer.list(None):
            tid = checkpoint.config["configurable"]["thread_id"]
            all_threads.add(tid)
    except Exception:
        pass
    return list(all_threads)

def get_thread_messages(thread_id: str):
    """Fetches full past message history for UI syncing."""
    config = {"configurable": {"thread_id": thread_id}}
    state = chatbot.get_state(config)
    
    formatted_messages = []
    if state and "messages" in state.values:
        for msg in state.values["messages"]:
            # Langchain base message roles transform checking for frontend interface structure
            if msg.type in ["human", "user"]:
                formatted_messages.append({"role": "user", "content": msg.content})
            elif msg.type in ["ai", "assistant"] and msg.content:
                formatted_messages.append({"role": "assistant", "content": msg.content})
    return formatted_messages