import React, { useState, useEffect } from 'react';
import axios from 'axios';

const symptomQuestions = [
    "Please describe your symptoms.",
    "How long have you been experiencing these symptoms?",
    "Do you have any allergies?",
    "Are you currently taking any medications?",
    "What is your age?",
];

function Chat() {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [userResponses, setUserResponses] = useState({});

    useEffect(() => {
        // Start the conversation with the first question
        if (currentQuestionIndex < symptomQuestions.length) {
            setMessages((prev) => [
                ...prev, 
                { text: symptomQuestions[currentQuestionIndex], sender: 'bot' }
            ]);
        }
    }, [currentQuestionIndex]);

    const handleSend = async (e) => {
        e.preventDefault();
        const userMessage = input;
        setMessages((prev) => [
            ...prev, 
            { text: userMessage, sender: 'user' }
        ]);
        setUserResponses((prev) => ({ ...prev, [currentQuestionIndex]: userMessage }));

        // Clear input field
        setInput('');

        // Proceed to the next question or send data to the backend
        if (currentQuestionIndex < symptomQuestions.length - 1) {
            setCurrentQuestionIndex((prev) => prev + 1);
        } else {
            await sendToBackend();
        }
    };

    const sendToBackend = async () => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/chat', {
                symptoms: userResponses,
            });
            const botResponse = response.data.response;
            setMessages((prev) => [
                ...prev, 
                { text: botResponse, sender: 'bot' }
            ]);
            resetConversation();
        } catch (error) {
            console.error("Error sending data to backend:", error);
            setMessages((prev) => [
                ...prev, 
                { text: "Sorry, there was an error. Please try again later.", sender: 'bot' }
            ]);
        }
    };

    const resetConversation = () => {
        setCurrentQuestionIndex(0);
        setUserResponses({});
    };

    return (
        <div className="chat-container">
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index} className={msg.sender}>
                        {msg.text}
                    </div>
                ))}
            </div>
            <form onSubmit={handleSend}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your response..."
                    required
                />
                <button type="submit">Send</button>
            </form>
        </div>
    );
}

export default Chat;
