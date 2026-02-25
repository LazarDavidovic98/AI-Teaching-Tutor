# 🧠 AI Teaching Tutor

Fullstack educational web aplikacija koja koristi **RAG** (Retrieval-Augmented Generation), **ChromaDB** vektorsku bazu i **OpenAI-kompatibilan LLM API** za interaktivno tutorovanje iz matematike i mašinskog učenja.

---

## 📁 Struktura projekta

```
AI-Teaching-Tutor/
├── backend/
│   ├── main.py                  # FastAPI ulazna tačka
│   ├── config.py                # Sva podešavanja (.env)
│   ├── database.py              # SQLAlchemy engine + sesija
│   ├── models/
│   │   ├── user.py              # ORM model korisnika
│   │   ├── document.py          # ORM model dokumenta
│   │   └── quiz.py              # ORM model rezultata kviza
│   ├── schemas/
│   │   ├── user.py              # Pydantic šeme za auth
│   │   ├── chat.py              # Pydantic šeme za chat
│   │   └── document.py          # Pydantic šema za dokument
│   ├── rag/
│   │   ├── ingestion.py         # Unos dokumenata u vektorsku bazu
│   │   ├── query.py             # RAG retrieval + generisanje odgovora
│   │   └── embedding_service.py # Abstraction layer za embeddinge
│   ├── routers/
│   │   ├── auth.py              # /api/auth/*
│   │   ├── chat.py              # /api/chat/*
│   │   └── upload.py            # /api/upload/*
│   └── services/
│       └── auth_service.py      # JWT, bcrypt, dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   └── UploadPage.jsx
│   │   ├── components/
│   │   │   └── Layout.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Pokretanje lokalno

### 1. Kloniranje i Python virtualnog okruženja

```bash
cd AI-Teaching-Tutor

# Kreiraj virtualnog okruženje
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Instalacija Python zavisnosti

```bash
pip install -r requirements.txt
```

### 3. Konfiguracija okruženja

```bash
# Kopiraj primjer i uredi ga
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux

# Uredi .env i postavi OPENAI_API_KEY
```

### 4. Pokretanje FastAPI backend-a

```bash
uvicorn backend.main:app --reload --port 8000
```

API dokumentacija dostupna na: http://localhost:8000/docs

### 5. Instalacija i pokretanje React frontend-a

```bash
cd frontend
npm install
npm run dev
```

Aplikacija dostupna na: http://localhost:5173

---

## 🔧 Lokalni LLM (bez OpenAI)

Instaliraj [Ollama](https://ollama.com) i postavi u `.env`:

```env
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama3.2
OPENAI_API_KEY=ollama   # placeholder, Ollama ga ignoruje
```

Za lokalne embeddinge:
```bash
pip install sentence-transformers
```
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## ⚙️ RAG arhitektura

```
Korisnik pita pitanje
        │
        ▼
[Embedding pitanja] ──► ChromaDB Similarity Search
                                │
                    Top-K relevantnih chunk-ova
                                │
                                ▼
              [LLM Prompt = Sistem + Kontekst + Historija + Pitanje]
                                │
                                ▼
                         LLM generira odgovor
                                │
                                ▼
                     Odgovor + Izvori → Korisnik
```

---

## 🛠️ Tehnički stack

| Sloj      | Tehnologija               |
|-----------|---------------------------|
| Backend   | FastAPI, SQLAlchemy        |
| Baza      | SQLite (PostgreSQL opcija) |
| Vektori   | ChromaDB                   |
| LLM       | OpenAI GPT / Ollama        |
| Auth      | JWT (python-jose) + bcrypt |
| Frontend  | React 18, Vite, Tailwind CSS |
| PDF parse | PyMuPDF                    |

---

## 📄 Licenca

MIT – slobodno koristite za portfolio i komercijalne projekte.
