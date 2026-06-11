import { useState, useEffect } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";

import Sidebar from "./components/Sidebar";
import ChatBox from "./components/ChatBox";
import FileUpload from "./components/FileUpload";

import "./App.css";

function App() {
  const [threadId, setThreadId] = useState(uuidv4());
  const [threads, setThreads] = useState([]);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // 1. Fetch all threads on component mount
  useEffect(() => {
    const fetchThreads = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/threads");
        if (response.data && response.data.threads) {
          setThreads(response.data.threads);
          // Agar database me threads hain, toh pehle thread ko active kar do
          if (response.data.threads.length > 0) {
            setThreadId(response.data.threads[0]);
          }
        }
      } catch (error) {
        console.error("Error fetching threads:", error);
      }
    };
    fetchThreads();
  }, []);

  // 2. Fetch messages whenever the active threadId changes
  useEffect(() => {
    const fetchMessagesForThread = async () => {
      // Backend par ek custom endpoint hona chahiye specific thread ki history nikalne ke liye
      try {
        const response = await axios.get(`http://127.0.0.1:8000/thread/${threadId}/messages`);
        if (response.data && response.data.messages) {
          setMessages(response.data.messages);
        } else {
          setMessages([]);
        }
      } catch (error) {
        // Agar endpoint abhi nahi banaya back-end par, toh clear handle karein
        setMessages([]);
      }
    };

    fetchMessagesForThread();
  }, [threadId]);

  const createNewChat = () => {
    const newId = uuidv4();
    setThreadId(newId);
    setMessages([]);
    setThreads((prev) => [newId, ...prev]);
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/chat",
        null,
        {
          params: {
            message: input,
            thread_id: threadId,
          },
        }
      );

      const botMessage = {
        role: "assistant",
        content: response.data.response,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat Error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong!" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <Sidebar
        threads={threads}
        currentThread={threadId}
        setCurrentThread={setThreadId}
        createNewChat={createNewChat}
      />

      <div className="main-content">
        <h1>AI PDF Chatbot</h1>
        
        <FileUpload threadId={threadId} />
        <ChatBox messages={messages} />

        <div className="input-section">
          <input
            type="text"
            placeholder="Ask anything..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()} // Enter key press support
            disabled={loading}
          />
          <button onClick={sendMessage} disabled={loading}>
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;