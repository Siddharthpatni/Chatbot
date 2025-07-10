import React, { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("chat");
  const [triviaStatus, setTriviaStatus] = useState({
    active: false,
    score: 0,
    total: 0,
    currentQuestion: null
  });
  const [showQuestionForm, setShowQuestionForm] = useState(false);
  const [showRemoveQuestionForm, setShowRemoveQuestionForm] = useState(false);
  const [newQuestion, setNewQuestion] = useState("");
  const [newAnswer, setNewAnswer] = useState("");
  const [questionToRemove, setQuestionToRemove] = useState("");
  const [questionList, setQuestionList] = useState([]);
  const messagesEndRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");

  const getCurrentTimestamp = () => {
    const now = new Date();
    return now.toLocaleString();
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    setMessages([{
      sender: "bot",
      text: "Hello! I'm your Service Chatbot. How can I help you today?",
      isTrivia: false,
      tab: "chat",
      timestamp: getCurrentTimestamp()
    }]);
    fetchQuestionList();
  }, []);

  const fetchQuestionList = async () => {
    try {
      const res = await fetch("http://localhost:5040/api/question/list");
      const data = await res.json();
      if (data.questions) {
        setQuestionList(data.questions);
      }
    } catch (err) {
      console.error("Failed to fetch questions:", err);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) {
      setError("Please enter a message");
      return;
    }

    const userMessage = {
      sender: "user",
      text: input,
      isTrivia: triviaStatus.active && activeTab === "trivia",
      tab: activeTab,
      timestamp: getCurrentTimestamp()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setError("");
    setIsLoading(true);

    try {
      let response;
      
      if (triviaStatus.active && activeTab === "trivia") {
        const res = await fetch("http://localhost:5040/api/trivia/answer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ answer: input })
        });
        
        if (!res.ok) throw new Error("Failed to process trivia answer");
        const data = await res.json();
        
        setTriviaStatus(prev => ({
          ...prev,
          score: data.score,
          total: data.total,
          currentQuestion: data.next_question || null
        }));
        
        // Create response message
        response = {
          sender: "bot",
          text: data.result === "correct" ? "✅ Correct!" : `❌ Incorrect. The correct answer was: ${data.correct_answer}`,
          isTrivia: true,
          tab: "trivia",
          timestamp: getCurrentTimestamp()
        };
        
        // Add response to messages
        setMessages(prev => [...prev, response]);
        
        // Handle next question or game end
        if (data.next_question) {
          setMessages(prev => [...prev, {
            sender: "bot",
            text: formatTriviaQuestion(data.next_question),
            isTrivia: true,
            tab: "trivia",
            timestamp: getCurrentTimestamp()
          }]);
        } else if (data.final_result) {
          const percentage = (data.final_result.score / data.final_result.total * 100).toFixed(1);
          setMessages(prev => [...prev, {
            sender: "bot",
            text: `🎉 Game Over! Final score: ${data.final_result.score}/${data.final_result.total} (${percentage}%) - ${data.final_result.message}`,
            isTrivia: true,
            tab: "trivia",
            timestamp: getCurrentTimestamp()
          }]);
          setTriviaStatus(prev => ({ ...prev, active: false }));
        }
      } else {
        const res = await fetch("http://localhost:5040/api/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: input })
        });
        
        if (!res.ok) throw new Error("Failed to get response");
        const data = await res.json();
        
        response = {
          sender: "bot",
          text: data.response,
          isTrivia: false,
          tab: activeTab,
          timestamp: getCurrentTimestamp()
        };
        
        setMessages(prev => [...prev, response]);
        
        if (data.trivia_active !== undefined) {
          setTriviaStatus(prev => ({ ...prev, active: data.trivia_active }));
        }
      }
    } catch (err) {
      console.error("Error:", err);
      setError(err.message);
      setMessages(prev => [...prev, {
        sender: "bot",
        text: "Sorry, I encountered an error. Please try again.",
        isTrivia: false,
        tab: activeTab,
        timestamp: getCurrentTimestamp()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTriviaQuestion = (question) => {
    if (!question) return "";
    return `Question ${question.question_number}/${question.total_questions}:\n${question.question}\n\nA) ${question.options[0]}\nB) ${question.options[1]}\nC) ${question.options[2]}\nD) ${question.options[3]}\n\nType A, B, C, or D to answer.`;
  };

  const startTrivia = async (numQuestions = 5) => {
    setIsLoading(true);
    setError("");
    
    try {
      const res = await fetch("http://localhost:5040/api/trivia/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ num_questions: numQuestions }),
      });
      
      if (!res.ok) throw new Error("Failed to start trivia");
      const data = await res.json();
      
      setTriviaStatus({
        active: data.game_active,
        score: data.score,
        total: data.total,
        currentQuestion: data.current_question
      });
      
      setMessages(prev => [...prev, {
        sender: "bot",
        text: `🎯 Trivia Game Started! (${numQuestions} questions)\nType A, B, C, or D to answer each question.`,
        isTrivia: true,
        tab: "trivia",
        timestamp: getCurrentTimestamp()
      }, {
        sender: "bot",
        text: formatTriviaQuestion(data.current_question),
        isTrivia: true,
        tab: "trivia",
        timestamp: getCurrentTimestamp()
      }]);
      
      // Switch to trivia tab if not already there
      setActiveTab("trivia");
    } catch (err) {
      console.error("Error:", err);
      setError(err.message);
      setMessages(prev => [...prev, {
        sender: "bot",
        text: "Failed to start trivia game. Please try again.",
        isTrivia: false,
        tab: "trivia",
        timestamp: getCurrentTimestamp()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const endTrivia = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:5040/api/trivia/end", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.error || "Failed to end trivia");
      
      setTriviaStatus({
        active: false,
        score: 0,
        total: 0,
        currentQuestion: null
      });
      
      setMessages(prev => [...prev, {
        sender: "bot",
        text: `Trivia game ended. Final score: ${data.final_score.score}/${data.final_score.total} (${data.final_score.percentage}%) - ${data.final_score.message}`,
        isTrivia: false,
        tab: "trivia",
        timestamp: getCurrentTimestamp()
      }]);
    } catch (err) {
      console.error("Error:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !isLoading) {
      if (activeTab === "trivia" && triviaStatus.active) {
        handleSend();
      } else if (activeTab === "chat") {
        handleSend();
      }
    }
  };

  const addNewQuestion = async () => {
    if (!newQuestion.trim() || !newAnswer.trim()) {
      setError("Please provide both question and answer");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:5040/api/question/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          question: newQuestion,
          answer: newAnswer
        }),
      });

      if (!res.ok) throw new Error("Failed to add question");
      const data = await res.json();

      setMessages(prev => [...prev, {
        sender: "bot",
        text: `Question added successfully: "${newQuestion}"`,
        isTrivia: false,
        tab: "manage",
        timestamp: getCurrentTimestamp()
      }]);
      setNewQuestion("");
      setNewAnswer("");
      setShowQuestionForm(false);
      fetchQuestionList();
    } catch (err) {
      console.error("Error:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const removeQuestion = async () => {
    if (!questionToRemove.trim()) {
      setError("Please select a question to remove");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:5040/api/question/remove", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          question: questionToRemove
        }),
      });

      if (!res.ok) throw new Error("Failed to remove question");
      const data = await res.json();

      setMessages(prev => [...prev, {
        sender: "bot",
        text: `Question removed successfully: "${questionToRemove}"`,
        isTrivia: false,
        tab: "manage",
        timestamp: getCurrentTimestamp()
      }]);
      setQuestionToRemove("");
      setShowRemoveQuestionForm(false);
      fetchQuestionList();
    } catch (err) {
      console.error("Error:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setUploadStatus("");
    }
  };

  const uploadFile = async () => {
    if (!selectedFile) {
      setError("Please select a file first");
      return;
    }

    setIsLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch("http://localhost:5040/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.error || "Failed to upload file");
      }

      setUploadStatus(data.message);
      setMessages(prev => [...prev, {
        sender: "bot",
        text: data.message,
        isTrivia: false,
        tab: "manage",
        timestamp: getCurrentTimestamp()
      }]);
      setSelectedFile(null);
      fetchQuestionList();
    } catch (err) {
      console.error("Error:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([{
      sender: "bot",
      text: "Chat cleared. How can I help you?",
      isTrivia: false,
      tab: activeTab,
      timestamp: getCurrentTimestamp()
    }]);
  };

  // Filter messages based on active tab
  const filteredMessages = messages
    .filter(msg => msg && msg.tab) // Ensure message exists and has tab property
    .filter(msg => msg.tab === activeTab);

  return (
    <div className="App">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>Service Chatbot</h1>
        </div>
        <div className="tabs">
          <button 
            className={activeTab === "chat" ? "active" : ""}
            onClick={() => setActiveTab("chat")}
          >
            Chat
          </button>
          <button 
            className={activeTab === "trivia" ? "active" : ""}
            onClick={() => setActiveTab("trivia")}
          >
            Trivia
          </button>
          <button 
            className={activeTab === "manage" ? "active" : ""}
            onClick={() => setActiveTab("manage")}
          >
            Manage
          </button>
          <button 
            className={activeTab === "help" ? "active" : ""}
            onClick={() => setActiveTab("help")}
          >
            Help
          </button>
        </div>
      </nav>

      <div className="chat-container">
        {activeTab === "chat" && (
          <>
            <div className="messages">
              {filteredMessages.map((msg, index) => (
                <div key={index} className={`message ${msg.sender}`}>
                  <div className="message-content">
                    {msg.text.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                    <div className="message-timestamp">
                      {msg.timestamp}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            <div className="input-area">
              <div className="quick-actions">
                <button onClick={() => startTrivia(5)} disabled={isLoading || triviaStatus.active}>
                  Start Trivia
                </button>
                <button onClick={clearChat} disabled={isLoading}>
                  Clear Chat
                </button>
              </div>
              <div className="input-group">
                <input
                  type="text"
                  placeholder="Type your message..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                />
                <button onClick={handleSend} disabled={isLoading}>
                  {isLoading ? <div className="spinner"></div> : "Send"}
                </button>
              </div>
            </div>
          </>
        )}

        {activeTab === "trivia" && (
          <div className="trivia-tab">
            <h2>Trivia Game</h2>
            <p>Test your knowledge about university services!</p>
            
            <div className="messages">
              {filteredMessages.map((msg, index) => (
                <div key={index} className={`message ${msg.sender}`}>
                  <div className="message-content">
                    {msg.text.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                    <div className="message-timestamp">
                      {msg.timestamp}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {triviaStatus.active ? (
              <>
                <div className="trivia-info">
                  <div className="score-display">
                    <span>Score: </span>
                    <strong>{triviaStatus.score}/{triviaStatus.total}</strong>
                  </div>
                  <button onClick={endTrivia} disabled={isLoading}>
                    End Trivia
                  </button>
                </div>
                
                <div className="input-area">
                  <div className="input-group">
                    <input
                      type="text"
                      placeholder="Type A, B, C, or D..."
                      value={input}
                      onChange={(e) => setInput(e.target.value.toUpperCase())}
                      onKeyPress={handleKeyPress}
                      disabled={isLoading}
                    />
                    <button onClick={handleSend} disabled={isLoading}>
                      {isLoading ? <div className="spinner"></div> : "Submit"}
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="trivia-options">
                  <button onClick={() => startTrivia(5)} disabled={isLoading}>
                    Quick Game (5 Qs)
                  </button>
                  <button onClick={() => startTrivia(10)} disabled={isLoading}>
                    Standard Game (10 Qs)
                  </button>
                  <button onClick={() => startTrivia(15)} disabled={isLoading}>
                    Full Game (15 Qs)
                  </button>
                </div>
                <div className="trivia-rules">
                  <h3>How to Play:</h3>
                  <ul>
                    <li>Answer questions about university services</li>
                    <li>Type A, B, C, or D to select your answer</li>
                    <li>Get instant feedback on your answers</li>
                    <li>See your final score at the end</li>
                  </ul>
                </div>
              </>
            )}
          </div>
        )}

        {activeTab === "manage" && (
          <div className="manage-tab">
            <h2>Knowledge Base Management</h2>
            
            <div className="messages">
              {filteredMessages.map((msg, index) => (
                <div key={index} className={`message ${msg.sender}`}>
                  <div className="message-content">
                    {msg.text.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                    <div className="message-timestamp">
                      {msg.timestamp}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="management-options">
              <div className="file-upload-section">
                <h3>Upload Questions (CSV)</h3>
                <div className="upload-area">
                  <input 
                    type="file" 
                    accept=".csv"
                    onChange={handleFileChange}
                    disabled={isLoading}
                  />
                  <button 
                    onClick={uploadFile} 
                    disabled={isLoading || !selectedFile}
                  >
                    {isLoading ? "Uploading..." : "Upload File"}
                  </button>
                  {selectedFile && (
                    <div className="file-info">
                      Selected: {selectedFile.name}
                    </div>
                  )}
                  {uploadStatus && <div className="upload-status">{uploadStatus}</div>}
                </div>
              </div>

              <div className="divider"></div>

              <div className="question-management-section">
                <div className="add-question-section">
                  <button 
                    onClick={() => {
                      setShowQuestionForm(!showQuestionForm);
                      setShowRemoveQuestionForm(false);
                    }}
                    className="toggle-form-btn"
                  >
                    {showQuestionForm ? "Hide Add Form" : "Add New Question"}
                  </button>
                  
                  {showQuestionForm && (
                    <div className="question-form">
                      <div className="form-group">
                        <label>Question:</label>
                        <input
                          type="text"
                          value={newQuestion}
                          onChange={(e) => setNewQuestion(e.target.value)}
                          placeholder="Enter the question"
                        />
                      </div>
                      <div className="form-group">
                        <label>Answer:</label>
                        <textarea
                          value={newAnswer}
                          onChange={(e) => setNewAnswer(e.target.value)}
                          placeholder="Enter the answer"
                          rows="3"
                        />
                      </div>
                      <button onClick={addNewQuestion} disabled={isLoading}>
                        {isLoading ? "Adding..." : "Add Question"}
                      </button>
                    </div>
                  )}
                </div>

                <div className="remove-question-section">
                  <button 
                    onClick={() => {
                      setShowRemoveQuestionForm(!showRemoveQuestionForm);
                      setShowQuestionForm(false);
                    }}
                    className="toggle-form-btn"
                  >
                    {showRemoveQuestionForm ? "Hide Remove Form" : "Remove Question"}
                  </button>
                  
                  {showRemoveQuestionForm && (
                    <div className="remove-form">
                      <div className="form-group">
                        <label>Select Question to Remove:</label>
                        <select
                          value={questionToRemove}
                          onChange={(e) => setQuestionToRemove(e.target.value)}
                        >
                          <option value="">Select a question</option>
                          {questionList.map((q, index) => (
                            <option key={index} value={q}>{q}</option>
                          ))}
                        </select>
                      </div>
                      <button onClick={removeQuestion} disabled={isLoading || !questionToRemove}>
                        {isLoading ? "Removing..." : "Remove Question"}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "help" && (
          <div className="help-tab">
            <h2>Chatbot Help</h2>
            <div className="help-sections">
              <div className="help-section">
                <h3>Features:</h3>
                <ul>
                  <li><strong>General Questions:</strong> Ask about university services</li>
                  <li><strong>Trivia Game:</strong> Test your knowledge with interactive quizzes</li>
                  <li><strong>Knowledge Management:</strong> Add, remove questions and upload question files</li>
                </ul>
              </div>
              <div className="help-section">
                <h3>How to Use:</h3>
                <ul>
                  <li><strong>Chat Tab:</strong> For general questions and conversation</li>
                  <li><strong>Trivia Tab:</strong> Start a new trivia game or continue an active one</li>
                  <li><strong>Manage Tab:</strong> Add/remove questions or upload CSV files with questions</li>
                </ul>
              </div>
              <div className="help-section">
                <h3>File Format:</h3>
                <p>CSV files should have these columns:</p>
                <ul>
                  <li><strong>question:</strong> The question text</li>
                  <li><strong>answer1:</strong> The correct answer</li>
                  <li><strong>answer2, answer3, answer4:</strong> Optional additional answers</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
}

export default App;