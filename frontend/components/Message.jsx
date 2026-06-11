function Message({ role, content }) {

  return (

    <div className={role === "user"
      ? "user-message"
      : "bot-message"}>

      {content}

    </div>

  );
}

export default Message;