import Message from "./Message";

function ChatBox({ messages }) {

  return (

    <div className="chat-box">

      {messages.map((msg, index) => (

        <Message
          key={index}
          role={msg.role}
          content={msg.content}
        />

      ))}

    </div>
  );
}

export default ChatBox;