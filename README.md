# Suvit AI Voice Agent


## Features

- Full-Duplex Audio: Real-time WebSocket streaming powered by Deepgram.
- Instant Interruptions: Agent stops speaking immediately upon voice activity detection.
- Hardware Mute: Integrated browser-level microphone controls for 100% privacy.
- Knowledge Base RAG: Fast context retrieval utilizing FAISS vector storage.

---

## Setup Sequence

Follow these exact steps in order to successfully build and launch the application.

### 1. Configuration

Create a file named `.env` inside the `backend/` directory and insert your API keys:

```env
DEEPGRAM_API_KEY="your_key_here"
GEMINI_API_KEY="your_key_here"
OPENAI_API_KEY="your_key_here"
SARVAMAI_API_KEY="your_key_here"
```

### 2. Environment Preparation

Navigate to the backend folder, generate your virtual python environment, and install runtime dependencies.

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # On Windows
# source venv/bin/activate # On Linux/macOS
pip install -r requirements.txt
```

### 3. Database Ingestion

You must execute the ingestion builder before starting the application server so the localized search indices are generated.

```bash
# Ensure source documents exist in backend/kb/docs/
python kb/ingest.py
```

Verification: You should see logs confirming "Building FAISS index... Done." and an "index" folder generated.

### 4. Launch Backend

With the indices built, you can now safely start the API server.

```bash
uvicorn main:app --reload --port 8000
```

### 5. Launch Frontend

Open a new terminal window, navigate into the frontend folder, and boot the user interface.

```bash
cd frontend
npm install
npm run dev
```

---

## Technical Stack

- Core: FastAPI (Python 3.13) & React (Vite)
- STT: Deepgram Nova-3 WebSocket
- LLM Intelligence: Google Gemini
- Speech Synthesis: Sarvam.ai Neural TTS
- Vector Storage: FAISS + HuggingFace Embeddings
