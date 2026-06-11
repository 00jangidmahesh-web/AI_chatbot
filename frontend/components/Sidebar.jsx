function Sidebar({ threads, currentThread, setCurrentThread, createNewChat }) {
  return (
    <div className="sidebar">
      <button className="new-chat-btn" onClick={createNewChat}>
        + New Chat
      </button>
      <hr />
      <div className="thread-list">
        {threads.map((thread) => (
          <button
            key={thread}
            className={`thread-btn ${thread === currentThread ? "active" : ""}`}
            onClick={() => setCurrentThread(thread)}
          >
            💬 {thread.slice(0, 8)}...
          </button>
        ))}
      </div>
    </div>
  );
}

export default Sidebar;