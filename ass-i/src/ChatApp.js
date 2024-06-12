// ChatApp.js

import React, { useState } from 'react';
import axios from 'axios';
import './ChatApp.css'; // Import CSS file for styling

const ChatApp = ({ documentId }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');

  const sendMessage = async () => {
    if (inputText.trim() === '') return;
    
    setMessages(prevMessages => [...prevMessages, { text: inputText, sender: 'user' }]);
    setInputText('');

    try {
      const response = await axios.post('http://localhost:8000/ask/', {
        documentId: documentId,
        question: inputText
      });
      const answer = response.data.answer;
      console.log(answer);
      setMessages(prevMessages => [...prevMessages, { text: answer, sender: 'bot' }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prevMessages => [...prevMessages, { text: 'Oops! Something went wrong.', sender: 'bot' }]);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            <div className="username">{message.sender === 'user' ? 'You' : 'Chat'}</div>
            <div className="message-text">{message.text}</div>
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          className="input-box"
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type your question here..."
        />
        <button className="send-button" onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default ChatApp;
