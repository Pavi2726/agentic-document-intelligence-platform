# 🚀 Agentic Document Intelligence Platform

A full-stack AI-powered document intelligence platform with multi-agent RAG system, conversation management, and modern React dashboard.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green)
![React](https://img.shields.io/badge/React-18-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🔐 Authentication
- User registration and login
- Session management with 7-day tokens
- Password hashing (SHA-256)
- Protected routes
- Auto-logout on session expiry

### 📄 Document Management
- Upload documents (PDF, DOCX, TXT)
- Document listing with metadata
- Search and filter documents
- Delete documents
- Chunk-based processing

### 💬 AI Chat Interface
- ChatGPT-style interface
- Streaming responses
- Multi-turn conversations
- Session history
- Context-aware responses
- Markdown rendering

### 🧠 Multi-Agent RAG System
- **Vector Search**: FAISS-based semantic search
- **Knowledge Graph**: Neo4j entity relationships
- **SQL Metadata**: PostgreSQL document metadata
- **Response Synthesis**: Groq LLM integration
- Smart context detection (relevance threshold)

### 🕸️ Knowledge Graph Explorer
- Interactive D3.js visualization
- Auto-generated from documents using Groq
- Zoom, pan, and drag functionality
- Node filtering and search
- Relationship visualization
- Works without Neo4j (fallback mode)

### 📊 Analytics Dashboard
- Real-time metrics monitoring
- API usage charts
- Latency tracking
- Recent activity logs
- System health indicators
- Auto-refresh every 30 seconds

### 💾 Conversation Management
- View all chat sessions
- Search conversations
- Delete sessions
- View full conversation history
- Session metadata display
- JSON file storage (no MongoDB required)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  Login │ Dashboard │ Documents │ Chat │ Graph │ Analytics   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  Auth │ Upload │ Chat │ Query │ Synthesis │ Analytics       │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │  Vector  │  │  Graph   │  │   SQL    │
         │  Store   │  │   RAG    │  │   RAG    │
         │ (FAISS)  │  │ (Neo4j)  │  │(Postgres)│
         └──────────┘  └──────────┘  └──────────┘
                              │
                              ▼
                      ┌──────────────┐
                      │   Groq LLM   │
                      │ (llama-3.3)  │
                      └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- Docker & Docker Compose (for containerized deployment)

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/agentic-document-intelligence-platform.git
   cd agentic-document-intelligence-platform
   ```

2. **Configure Environment**
   ```bash
   cp .env.docker .env
   # Edit .env and add your GROQ_API_KEY
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/agentic-document-intelligence-platform.git
   cd agentic-document-intelligence-platform
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   
   Create `backend/.env`:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password
   POSTGRES_URL=postgresql://postgres:password@localhost:5432/document_intelligence
   REDIS_HOST=localhost
   REDIS_PORT=6379
   MONGO_URI=mongodb://localhost:27017/
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

5. **Start the Application**
   
   **Terminal 1 - Backend:**
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   uvicorn app.main:app --reload --port 8000
   ```
   
   **Terminal 2 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

6. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📦 Technology Stack

### Backend
- **Framework**: FastAPI 0.111.0
- **AI/ML**: 
  - Groq LLM API (llama-3.3-70b-versatile)
  - LangChain 0.3.7
  - Sentence Transformers 3.0.1
- **Vector Store**: FAISS 1.14.2
- **Databases** (Optional):
  - Neo4j 5.21.0 (Knowledge Graph)
  - PostgreSQL (Metadata)
  - Redis 5.0.1 (Session Cache)
  - MongoDB 4.8.0 (Chat History)
- **Document Processing**:
  - PyPDF 4.2.0
  - docx2txt 0.8

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **Charts**: Recharts
- **Graph Viz**: D3.js
- **HTTP Client**: Axios
- **Markdown**: React Markdown
- **Icons**: Lucide React

## 🎯 Key Features Explained

### Smart Response Synthesis
The system intelligently combines results from multiple sources:
- Vector search results (semantic similarity)
- Knowledge graph relationships
- SQL metadata queries
- Relevance threshold (0.3) for context detection
- Fallback to Groq's general knowledge

### Automatic Knowledge Graph
- Extracts entities from documents using Groq
- Processes first 5 chunks per document
- Generates relationships automatically
- Works without Neo4j installation
- Interactive visualization

### Conversation Context
- Stores chat history in JSON files
- No database required
- 7-day session tokens
- Multi-turn conversation support
- Context-aware responses

### Fallback Systems
All features work WITHOUT optional databases:
- **No PostgreSQL**: Uses filesystem for documents
- **No MongoDB**: Uses JSON files for chat history
- **No Redis**: Direct storage without caching
- **No Neo4j**: Generates graph from vector store

## 📚 Documentation

- [Complete Setup Guide](COMPLETE_POSTGRESQL_SETUP.md)
- [PostgreSQL Setup](POSTGRESQL_SETUP.md)
- [Chat History Guide](CHAT_HISTORY_FIXED.md)
- [Knowledge Graph Guide](KNOWLEDGE_GRAPH_IMPROVEMENTS.md)
- [Login System Guide](LOGIN_SYSTEM_GUIDE.md)
- [Startup Guide](STARTUP_GUIDE.md)
- [Quick Reference](POSTGRESQL_QUICK_REFERENCE.txt)

## 🔧 Configuration

### Required
- `GROQ_API_KEY`: Get from https://console.groq.com

### Optional (with fallbacks)
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Knowledge graph
- `POSTGRES_URL`: Document metadata
- `REDIS_HOST`, `REDIS_PORT`: Session caching
- `MONGO_URI`: Chat history persistence

## 🧪 Testing

### Create Test Account
1. Go to http://localhost:3000
2. Click "Sign up"
3. Username: `testuser`
4. Password: `password123`
5. Click "Sign Up" then "Sign In"

### Upload Test Document
1. Go to Documents page
2. Upload a PDF/DOCX/TXT file
3. Wait for processing

### Test Chat
1. Go to Chat page
2. Ask questions about your document
3. Try streaming responses

### Explore Knowledge Graph
1. Go to Knowledge Graph page
2. Click "Refresh" to generate graph
3. Drag nodes, zoom, and explore

## 📊 Project Structure

```
agentic-document-intelligence-platform/
├── backend/
│   ├── app/
│   │   ├── agents/          # Multi-agent system
│   │   ├── api/             # API routes
│   │   ├── auth/            # Authentication
│   │   ├── core/            # Configuration
│   │   ├── db/              # Database clients
│   │   ├── retrievers/      # RAG retrievers
│   │   ├── services/        # Business logic
│   │   └── tools/           # Utilities
│   ├── uploads/             # Uploaded files
│   ├── vector_store/        # FAISS index
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   └── types/           # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── START_ALL.bat            # Windows startup script
└── README.md
```


