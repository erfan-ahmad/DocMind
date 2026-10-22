# 🧠 DocMind

> **Intelligent Document Management & Retrieval-Augmented Generation (RAG) Platform**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-6.1+-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/react-19+-61dafb.svg)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/tailwindcss-v4-38bdf8.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**DocMind** is an enterprise-grade document intelligence platform that allows users to upload, categorize, and semantically query their documents. Leveraging local **Sentence Transformers**, **LangChain**, and **OCR pipelines**, DocMind enables fast semantic search and contextual question answering (RAG) with precise citations and source transparency.

---

## ✨ Key Features

- 🔐 **Secure Multi-Tenant Architecture:** User isolation at database and vector retriever levels with JWT authentication.
- 📁 **Document & Category Management:** Hierarchical categorization, metadata tagging, and document lifecycle control.
- 📄 **Multimodal Ingestion & OCR:** Automatic text extraction from PDFs and scanned documents via `pytesseract` and `pdf2image` with Persian/Arabic script normalization.
- ⚡ **RAG Semantic Search:** Chunk-level vector embeddings with cosine similarity scoring, configurable top-$k$ retrieval, and source excerpts.
- 🎨 **Modern Responsive UI:** Complete Persian (RTL) frontend built with **React**, **TypeScript**, **Tailwind CSS**, and **Vazirmatn** typography.
- 📖 **Interactive API Documentation:** Full OpenAPI 3.0 schema and Swagger/Redoc UI powered by `drf-spectacular`.

---

## 🛠️ Architecture & Tech Stack

### Backend
- **Framework:** Python, Django 6+, Django REST Framework (DRF)
- **Authentication:** SimpleJWT (Access & Refresh tokens)
- **AI & NLP:** `sentence-transformers`, `torch` (CPU/GPU-ready), `langchain`
- **Text & OCR:** `pypdf`, `pdf2image`, `pytesseract`, `arabic-reshaper`, `python-bidi`, `parsivar`
- **Database:** SQLite (default/dev), PostgreSQL / pgvector ready

### Frontend
- **Framework:** React 19, TypeScript, Vite
- **Styling:** Tailwind CSS v4, RTL Layout, Lucide-style SVG icons
- **State & HTTP:** Axios client with automated JWT interceptors and refresh handlers

---

## 🚀 Getting Started

### Prerequisites

- **Python:** `3.10+`
- **Node.js:** `18+` & `npm`
- **Tesseract OCR & Poppler:** (Required for PDF and image OCR processing)

---

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/erfan-ahmad/DocMind.git
cd DocMind/backend

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Run database migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```
The backend API will be available at: `http://127.0.0.1:8000/api/`

---

### 2. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
The frontend UI will be available at: `http://localhost:5173/`

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/accounts/register/` | Register new user account | ❌ |
| `POST` | `/api/accounts/login/` | Obtain JWT token pair | ❌ |
| `POST` | `/api/accounts/token/refresh/` | Refresh expired access token | ❌ |
| `GET` | `/api/accounts/profile/` | Fetch current user profile | ✅ |
| `GET/POST`| `/api/categories/` | List or create categories | ✅ |
| `GET/POST`| `/api/documents/` | List or upload documents (PDF/TXT) | ✅ |
| `POST` | `/api/ask/` | Ask questions with RAG similarity | ✅ |
| `GET` | `/api/schema/swagger-ui/`| Interactive Swagger UI docs | ❌ |

---

## 🤖 RAG Engine Workflow

```
[User Document Upload]
        │
        ▼
[Text Extraction & OCR (pdf2image / pytesseract)]
        │
        ▼
[Persian Normalization & Text Cleaning]
        │
        ▼
[Recursive Chunking (LangChain)]
        │
        ▼
[Vector Embeddings Generation (SentenceTransformer)]
        │
        ▼
[User Query] ──> [Cosine Similarity Search (k nearest chunks)] ──> [Synthesized Answer + Sources]
```

---

## 📁 Project Structure

```
DocMind/
├── backend/                  # Django project root
│   ├── backend/              # Core project settings and routing
│   ├── accounts_app/         # Custom authentication and profiles
│   ├── documents_app/        # Documents, categories & RAG retrieval services
│   └── manage.py
├── frontend/                 # React + Vite + TypeScript application
│   ├── src/
│   │   ├── api/              # Axios client and token interceptors
│   │   ├── components/       # Layout, ProtectedRoute, Navigation
│   │   ├── hooks/            # useAuth context and state hooks
│   │   └── pages/            # Dashboard, Documents, Categories, AI Chat, Auth
│   └── index.html
├── model/                    # Local embedding model cache (ignored in Git)
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
```

---

## 👨‍💻 Author

**Erfan Ahmadi**  
- Backend & AI Developer  
- GitHub: [@erfan-ahmad](https://github.com/erfan-ahmad)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
