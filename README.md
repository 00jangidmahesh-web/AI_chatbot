#  AI PDF Chatbot with Agentic RAG

A full-stack AI chatbot built with **ReactJS + FastAPI + LangGraph** that supports PDF-based question answering, multi-tool capabilities, and persistent conversation memory.

##  Features

*  Upload PDF documents and chat with them using Retrieval-Augmented Generation (RAG)
*  Agentic workflows powered by LangGraph
*  Multi-turn conversations with persistent memory using SQLite
*  Web search integration using DuckDuckGo
*  Stock price lookup using Alpha Vantage API
*  Built-in calculator tool
*  FastAPI backend with REST APIs
*  ReactJS frontend with reusable components
*  Thread-based chat sessions
*  Semantic retrieval using OpenAI embeddings and FAISS vector database

---

##  Tech Stack

### Frontend

* ReactJS
* HTML5
* CSS3
* Axios

### Backend

* Python
* FastAPI
* LangGraph
* LangChain

### Vector Store & Memory

* FAISS
* SQLite

### AI & LLM

* OpenAI GPT-4o-mini
* OpenAI Embeddings

### External APIs

* DuckDuckGo Search
* Alpha Vantage Stock API

---

## 📂 Project Structure

```text
AI-PDF-CHATBOT
│
├── backend
│     ├── main.py
│     ├── langgraph_rag_backend.py
│     ├── chatbot.db
│     ├── requirements.txt
│     └── .env
│
├── frontend
│     ├── package.json
│     ├── index.html
│     ├── src
│     │     ├── App.jsx
│     │     ├── App.css
│     │     ├── index.css
│     │     ├── main.jsx
│     │     └── components
│     │            ├── Sidebar.jsx
│     │            ├── ChatBox.jsx
│     │            ├── Message.jsx
│     │            └── FileUpload.jsx
│
└── README.md
```

---

##  Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-PDF-CHATBOT.git

cd AI-PDF-CHATBOT
```

---

## Backend Setup

```bash
cd backend

pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
```

Run FastAPI server:

```bash
uvicorn main:app --reload
```

Backend will run at:

```text
http://127.0.0.1:8000
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend will run at:

```text
http://localhost:5173
```

---

## Available APIs

### Upload PDF

```http
POST /upload
```

Parameters:

* file
* thread_id

---

### Chat

```http
POST /chat
```

Parameters:

```json
{
  "message": "Summarize the document",
  "thread_id": "123"
}
```

---

### Get Threads

```http
GET /threads
```

---

## Supported Tools

### 📄 PDF RAG Tool

Answers questions from uploaded documents.

###  Web Search Tool

Uses DuckDuckGo search.

###  Stock Price Tool

Fetches latest stock prices.

###  Calculator Tool

Performs arithmetic operations.

---

## Example Workflow

1. Create a new chat thread.
2. Upload a PDF.
3. Ask questions about the document.
4. Use web search, stock lookup, or calculator when needed.
5. Continue conversations with persistent memory.

---

## Skills Demonstrated

* Full-Stack Development
* ReactJS
* FastAPI
* REST APIs
* LangGraph
* LangChain
* Agentic RAG
* Vector Databases
* OpenAI APIs
* Prompt Engineering
* Semantic Search
* SQLite Persistence

---

## Future Improvements

* Streaming responses
* Redux state management
* Markdown rendering
* Docker deployment
* Authentication
* Multi-user support
* Dark mode
* Redis caching

---

## Author

**Mahesh Kumar Jangid**

* LinkedIn: https://linkedin.com/in/mahesh-kumar-jangid-22b375306
* GitHub: https://github.com/00jangidmahesh-web
