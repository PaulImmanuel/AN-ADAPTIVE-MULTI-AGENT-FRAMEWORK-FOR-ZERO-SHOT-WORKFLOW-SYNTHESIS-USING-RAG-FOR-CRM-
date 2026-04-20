import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

function ChatWindow() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'ai', text: 'Hi! I am your Automation Copilot. How can I help you connect your data?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const toggleChat = () => setIsOpen(!isOpen);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/chat', {
        message: userMsg.text
      });

      // Check if response looks like JSON code
      const aiResponse = response.data.response;
      let msgType = 'text';
      let msgContent = aiResponse;

      if (aiResponse.trim().startsWith('{') || aiResponse.includes('"node":')) {
        msgType = 'action'; // It's a workflow!
      }

      const aiMsg = { sender: 'ai', text: msgContent, type: msgType };
      setMessages((prev) => [...prev, aiMsg]);

    } catch (error) {
      console.error("Chat Error:", error);
      setMessages((prev) => [...prev, { sender: 'ai', text: 'Connection error.' }]);
    } finally {
      setIsLoading(false);
    }
  };

// --- IMPROVED Simulation Function ---
  const handleRunWorkflow = (jsonContent, index) => {
    let details = "Workflow";
    
    try {
      // 1. Clean the JSON (Remove markdown ```json and ``` if present)
      const cleanJson = jsonContent.replace(/```json/g, '').replace(/```/g, '').trim();
      
      // 2. Parse
      const parsed = JSON.parse(cleanJson);
      
      // 3. Find the action name (checks for 'node', 'action', or 'tool')
      const actionName = parsed.node || parsed.action || parsed.tool || "Automation";
      details = `${actionName} Action`;
      
    } catch (e) { 
      console.error("JSON Parse Error:", e);
      details = "Complex Workflow"; 
    }

    setMessages((prev) => [...prev, { sender: 'system', text: `⚙️ Executing ${details}...` }]);

    setTimeout(() => {
        setMessages((prev) => [...prev, { sender: 'system', text: `✅ Success! ${details} completed.` }]);
    }, 1500);
  };

  return (
    <div style={styles.wrapper}>
      {isOpen && (
        <div style={styles.window}>
          <div style={styles.header}>
            <span>🤖 Automation Copilot</span>
            <button onClick={toggleChat} style={styles.closeBtn}>×</button>
          </div>
          
          <div style={styles.messagesArea}>
            {messages.map((msg, index) => (
              <div key={index} style={{
                  ...styles.msgBubble, 
                  ...(msg.sender === 'user' ? styles.userMsg : (msg.sender === 'system' ? styles.systemMsg : styles.aiMsg))
              }}>
                {msg.type === 'action' ? (
                    // --- THE ACTION CARD ---
                    <div style={styles.actionCard}>
                        <strong>⚡ Workflow Generated</strong>
                        <pre style={styles.codeBlock}>{msg.text}</pre>
                        <button 
                            style={styles.runBtn}
                            onClick={() => handleRunWorkflow(msg.text, index)}
                        >
                            ▶ Run Automation
                        </button>
                    </div>
                ) : (
                    // Normal Text
                    msg.text
                )}
              </div>
            ))}
            {isLoading && <div style={styles.loading}>Thinking...</div>}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSend} style={styles.inputArea}>
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask to automate..."
              style={styles.input}
            />
            <button type="submit" disabled={isLoading} style={styles.sendBtn}>Send</button>
          </form>
        </div>
      )}
      <button onClick={toggleChat} style={styles.fab}>{isOpen ? 'Close' : '💬 Automate'}</button>
    </div>
  );
}

const styles = {
  wrapper: { position: 'fixed', bottom: '20px', right: '20px', zIndex: 1000, fontFamily: 'Arial, sans-serif' },
  fab: { padding: '15px 20px', borderRadius: '30px', backgroundColor: '#007bff', color: 'white', border: 'none', cursor: 'pointer', fontSize: '16px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' },
  window: { position: 'absolute', bottom: '70px', right: '0', width: '350px', height: '500px', backgroundColor: 'white', borderRadius: '10px', boxShadow: '0 5px 15px rgba(0,0,0,0.2)', display: 'flex', flexDirection: 'column', border: '1px solid #ccc' },
  header: { padding: '10px', backgroundColor: '#007bff', color: 'white', borderTopLeftRadius: '10px', borderTopRightRadius: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  closeBtn: { background: 'none', border: 'none', color: 'white', fontSize: '20px', cursor: 'pointer' },
  messagesArea: { flex: 1, padding: '10px', overflowY: 'auto', backgroundColor: '#f9f9f9', display: 'flex', flexDirection: 'column' },
  msgBubble: { padding: '10px', borderRadius: '8px', margin: '5px 0', maxWidth: '90%', fontSize: '14px', lineHeight: '1.4' },
  userMsg: { alignSelf: 'flex-end', backgroundColor: '#e3f2fd', color: '#333' },
  aiMsg: { alignSelf: 'flex-start', backgroundColor: '#fff', color: '#397537ff',border: '1px solid #eee' },
  systemMsg: { alignSelf: 'center', backgroundColor: '#d4edda', color: '#155724', fontSize: '12px', border: '1px solid #c3e6cb' },
  inputArea: { padding: '10px', borderTop: '1px solid #ccc', display: 'flex' },
  input: { flex: 1, padding: '10px', border: '1px solid #ccc', borderRadius: '4px', marginRight: '5px' },
  sendBtn: { padding: '8px 15px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  loading: { fontSize: '12px', color: '#888', fontStyle: 'italic', marginTop: '5px', alignSelf: 'flex-start' },
  // Action Card Styles
  actionCard: { display: 'flex', flexDirection: 'column', gap: '8px' },
  codeBlock: { backgroundColor: '#f1f1f1', padding: '5px', borderRadius: '4px', fontSize: '11px', overflowX: 'auto', border: '1px solid #ddd', margin: '0' },
  runBtn: { padding: '8px', backgroundColor: '#6f42c1', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center' }
};

export default ChatWindow;