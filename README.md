# Suvit AI Voice Agent

A premium, hyper-responsive full-duplex voice assistant engineered for zero-latency support interactions. Featuring cloud-based neural VAD, instant hardware interruptions, dynamic multilingual synthesis, and fully localized knowledge base retrieval.

## ✨ Key Capabilities

- **Continuous Streaming Architecture**: Utilizes full-duplex WebSocket streaming powered by Deepgram for sub-second interactivity
- **Instant Neural Interruptions**: Agent stops speaking *immediately* when you speak, guaranteed via server-side cloud activity detection.
- **Background-Safe Runtime**: Utilizes dedicated CPU thread shielding preventing heavy knowledge lookups from freezing active stream heartbeats.
- **Hardware Mute Override**: Integrates browser-level track lifecycle handlers delivering absolute 0% audio leakage when muted.
- **Localized RAG Vectorstore**: High-speed similarity lookups leveraging optimized FAISS embeddings for accurate information retrieval.

---

## 🚀 Quick Start Guide

### 1. Launch the Backend

Navigate into the backend layer, configure environment keys, and initiate server.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt # Or install necessary packages
uvicorn main:app --reload --port 8000
```

### 2. Knowledge Base Setup (Data Ingestion)

Initialize the local RAG database with your custom domain knowledge.

```bash
# 1. Place your source data (.md files) here:
# backend/kb/docs/

# 2. Run the ingestion pipeline to generate the FAISS index:
cd backend
python kb/ingest.py
```

*Log confirmations: `Building FAISS index... Done. Index saved to .../index/`*

### 3. Launch the Dashboard

Boot the dynamic React dashboard using Vite.

```bash
cd frontend
npm install
npm run dev
```

---

## 🛠 Technical Ecosystem

| Component                   | Solution                                   |
| :-------------------------- | :----------------------------------------- |
| **Core Framework**    | FastAPI (Python) & React (TypeScript)      |
| **Real-Time STT**     | Deepgram Nova-3 Neural WebSocket           |
| **LLM Intelligence**  | Google Gemini 2.5 Flash                    |
| **Translation Logic** | OpenAI Whisper & ChatGPT-4                 |
| **Speech Synthesis**  | Sarvam.ai Neural TTS (Indic Support)       |
| **Knowledge Engine**  | LangChain + HuggingFace Embeddings + FAISS |

## ⚙️ Environment Variables

Required variables in `backend/.env`:

```env
DEEPGRAM_API_KEY="your-key"
GOOGLE_API_KEY="your-key"
OPENAI_API_KEY="your-key"
SARVAMAI_API_KEY="your-key"
```

## 🔒 Privacy & Security

Microphone access is requested solely at the runtime start event and is released instantly upon call termination. Explicit "Mute" commands utilize `MediaStreamTrack.enabled = false` executing absolute hardware silent gating at the edge device level before propagation.
