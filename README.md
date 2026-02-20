# 🧠 MediScan AI  
### Full-Stack AI-Powered Medical Diagnostic Platform  

---

## 🖼 Project Preview

<!-- Add real screenshots after deployment -->
Breast Ultrasound → YOLOv8 Detection → AI Explanation → Automated PDF Report

---

## 🚀 Live Demo

🌐 **Frontend:** *(Add after deployment)*  
🔗 **Backend API:** *(Add after deployment)*  

---

## 🏆 GitHub Badges

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Computer%20Vision-red)
![Groq LLaMA3](https://img.shields.io/badge/Groq-LLaMA3-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

# 📌 Overview

**MediScan AI** is a production-style full-stack AI healthcare platform that integrates:

- 🩺 YOLOv8 for breast ultrasound lesion detection  
- 🧠 Groq LLaMA 3 for AI-powered medical explanation  
- 📄 RAG-based document Q&A system  
- 📑 Automated PDF diagnostic report generation  
- ⚛️ React + FastAPI scalable architecture  

This project simulates a real-world AI-assisted diagnostic workflow used in modern health-tech platforms.

---

# 🏗 System Architecture

```
User (React Frontend)
        │
        ▼
FastAPI Backend
        │
        ├── YOLOv8 → Lesion Detection
        ├── Groq LLaMA 3 → Explanation Generation
        ├── RAG Engine → Document Q&A
        └── ReportLab → PDF Report Generation
```

---

# ✨ Core Features

## 🔍 Ultrasound Lesion Detection
- Upload breast ultrasound image  
- YOLOv8 detects lesions  
- Bounding box annotated output  
- Confidence score reporting  

## 🧠 AI Medical Explanation
- LLaMA 3 via Groq API  
- Patient-friendly interpretation  
- Suggested next steps  
- Structured reasoning  

## 📄 Document Q&A (RAG)
- Upload medical PDFs  
- Semantic search via vector database  
- Context-aware answers  
- LangChain + ChromaDB integration  

## 📑 Automated PDF Report Generation
- Professional clinical layout  
- Detection summary  
- AI explanation  
- Embedded annotated scan  
- Downloadable report  

---

# 🛠 Tech Stack

## Backend
- FastAPI  
- Ultralytics YOLOv8  
- Groq (LLaMA 3)  
- LangChain  
- ChromaDB  
- ReportLab  
- OpenCV  
- Pydantic  

## Frontend
- React  
- Axios  
- React Markdown  
- Responsive UI  

---

# 📂 Project Structure

```
mediscan-ai/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models/
│   │   └── main.py
│   ├── static/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
└── README.md
```

---

# ⚙️ Local Setup Guide

## 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/mediscan-ai.git
cd mediscan-ai
```

---

## 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # Mac/Linux

pip install -r requirements.txt
```

### ▶ Run Backend

```bash
uvicorn app.main:app --reload
```

Backend runs at:
```
http://localhost:8000
```

---

## 3️⃣ Frontend Setup

Open new terminal:

```bash
cd frontend
npm install
npm start
```

Frontend runs at:
```
http://localhost:3000
```

---

# 🔐 Environment Variables

Create file:
```
backend/.env
```

Add:
```
GROQ_API_KEY=your_api_key_here
```

⚠ Do NOT push `.env` to GitHub.

---

# 🌍 Deployment Guide

## 🚀 Backend → Render

Start Command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

Add Environment Variable:
```
GROQ_API_KEY=your_api_key_here
```

---

## 🚀 Frontend → Vercel

1. Import GitHub repository  
2. Select `frontend` folder  
3. Deploy  

After deployment, update frontend API base URL.

---

# 🎯 Why This Project Stands Out

✔ End-to-End ML deployment  
✔ Production-style FastAPI architecture  
✔ Computer Vision + LLM integration  
✔ RAG pipeline implementation  
✔ Automated PDF report generation  
✔ Modular backend structure  
✔ Internship-ready & portfolio-level  

This demonstrates real-world AI system engineering, not just model training.

---

# 📈 Future Improvements

- Docker containerization  
- CI/CD pipeline  
- Authentication system  
- Role-based dashboards  
- Model performance analytics  
- Cloud storage integration  

---

# 👨‍💻 Author

**Shivansh Arora**  
Machine Learning & Full-Stack AI Developer  

---

# 📜 License

MIT License  

---

# ⭐ If You Like This Project

Give it a ⭐ on GitHub and connect for collaboration 🚀
