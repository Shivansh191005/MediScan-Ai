import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";
import ReactMarkdown from "react-markdown";

function App() {
  const [message, setMessage] = useState("");
  const [mode, setMode] = useState("chat");
  const [chat, setChat] = useState([]);
  const [file, setFile] = useState(null);
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const chatBottomRef = useRef(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat, loading]);

  // ── SEND CHAT MESSAGE ──────────────────────────────────────
  const sendMessage = async () => {
    if (message.trim() === "") return;
    setChat(prev => [...prev, { sender: "user", text: message }]);
    const url = mode === "analyze"
      ? "http://localhost:8000/analyze"
      : "http://localhost:8000/chat";
    const userMsg = message;
    setMessage("");
    try {
      const res = await axios.post(url, { message: userMsg });
      const botReply = res?.data?.reply !== undefined ? res.data.reply : "No response from server";
      setChat(prev => [...prev, { sender: "bot", text: botReply }]);
    } catch {
      setChat(prev => [...prev, { sender: "bot", text: "Server error." }]);
    }
  };

  // ── UPLOAD PDF ─────────────────────────────────────────────
  const uploadFile = async () => {
    if (!file) { alert("Please select a PDF file first"); return; }
    const formData = new FormData();
    formData.append("file", file);
    try {
      await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setChat(prev => [...prev, { sender: "bot", text: "✓ PDF uploaded successfully. You can now ask questions about the document." }]);
    } catch {
      setChat(prev => [...prev, { sender: "bot", text: "PDF upload failed." }]);
    }
  };

  // ── ANALYZE IMAGE ──────────────────────────────────────────
  const analyzeImage = async () => {
    if (!image) { alert("Please select an image first"); return; }
    const formData = new FormData();
    formData.append("file", image);
    setChat(prev => [...prev, { sender: "user", text: "📤 Uploaded ultrasound image for analysis" }]);
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/predict-image", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      const text = res.data.raw_findings + "\n\n" + res.data.explanation;
      setChat(prev => [...prev, {
        sender: "bot", text,
        image: res.data.image_url,
        pdf: res.data.pdf_url
      }]);
    } catch {
      setChat(prev => [...prev, { sender: "bot", text: "Image analysis failed." }]);
    }
    setLoading(false);
  };

  // ── UI ─────────────────────────────────────────────────────
  return (
    <div className="container">

      {/* HEADER */}
      <div className="header">
        <div className="header-icon">🫀</div>
        <div className="header-text">
          <h1>MediScan AI</h1>
          <p>Diagnostic Intelligence Platform</p>
        </div>
        <div className="status-dot">System Online</div>
      </div>

      {/* UPLOAD PANELS */}
      <div className="panels-row">

        {/* PDF Upload */}
        <div className="card">
          <div className="card-label">Document Ingestion</div>
          <div className="file-row">
            <div className="file-input-wrapper" style={{ flex: 1 }}>
              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setFile(e.target.files[0])}
              />
              <div className="file-input-fake">
                <span>📄</span>
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {file ? file.name : "Select PDF file…"}
                </span>
              </div>
            </div>
            <button className="btn-primary" onClick={uploadFile}>Upload</button>
          </div>
        </div>

        {/* Image Upload */}
        <div className="card">
          <div className="card-label">Ultrasound Scan</div>
          <div className="file-row">
            <div className="file-input-wrapper" style={{ flex: 1 }}>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setImage(e.target.files[0])}
              />
              <div className="file-input-fake">
                <span>🔬</span>
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {image ? image.name : "Select image file…"}
                </span>
              </div>
            </div>
            <button
              className="btn-primary"
              onClick={analyzeImage}
              disabled={loading}
            >
              {loading ? "Scanning…" : "Analyze"}
            </button>
          </div>
        </div>

      </div>

      {/* MODE TABS */}
      <div className="mode-tabs">
        <button
          className={`mode-tab${mode === "chat" ? " active" : ""}`}
          onClick={() => setMode("chat")}
        >
          <span>💬</span> Document Chat
        </button>
        <button
          className={`mode-tab${mode === "analyze" ? " active" : ""}`}
          onClick={() => setMode("analyze")}
        >
          <span>🧬</span> Medical Analysis
        </button>
      </div>

      {/* CHAT BOX */}
      <div className="chatbox-wrapper">
        <div className="chatbox-header">
          <span className="chatbox-title">Conversation Log</span>
          <div className="chatbox-dots">
            <span /><span /><span />
          </div>
        </div>

        <div className="chatbox">
          {chat.length === 0 && !loading && (
            <div className="chat-empty">
              <div className="chat-empty-icon">🩻</div>
              <span>Upload a document or scan to begin analysis</span>
            </div>
          )}

          {chat.map((c, i) => (
            <div key={i} className={c.sender}>
              {c.sender === "bot" ? (
                <>
                  <ReactMarkdown>{c.text}</ReactMarkdown>
                  {c.image && (
                    <img src={`http://localhost:8000${c.image}`} alt="scan result" className="scanImage" />
                  )}
                  {c.pdf && (
                    <div className="pdf-link">
                      <a href={`http://localhost:8000${c.pdf}`} target="_blank" rel="noopener noreferrer">
                        <button>⬇ Download Full Report (PDF)</button>
                      </a>
                    </div>
                  )}
                </>
              ) : (
                c.text
              )}
            </div>
          ))}

          {loading && (
            <div className="bot" style={{ alignSelf: 'flex-start' }}>
              <div className="loading-row">
                <div className="spinner" />
                <span>Analyzing scan data…</span>
              </div>
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>
      </div>

      {/* INPUT */}
      <div className="inputArea">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={mode === "analyze" ? "Ask about medical findings…" : "Ask about the document…"}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button className="btn-primary" onClick={sendMessage}>Send →</button>
      </div>

    </div>
  );
}

export default App;