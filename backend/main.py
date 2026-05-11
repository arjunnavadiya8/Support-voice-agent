# # # # import os
# # # # import json
# # # # import base64
# # # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # # # from fastapi.middleware.cors import CORSMiddleware
# # # # from dotenv import load_dotenv
# # # # from agent.graph import agent_graph
# # # # from agent.state import VoiceState

# # # # load_dotenv()

# # # # app = FastAPI()
# # # # app.add_middleware(
# # # #     CORSMiddleware,
# # # #     allow_origins=["http://localhost:5173"],
# # # #     allow_methods=["*"],
# # # #     allow_headers=["*"],
# # # # )


# # # # @app.websocket("/ws/voice")
# # # # async def voice_endpoint(ws: WebSocket):
# # # #     await ws.accept()
# # # #     try:
# # # #         while True:
# # # #             # Receive audio as base64-encoded JSON
# # # #             raw = await ws.receive_text()
# # # #             data = json.loads(raw)
# # # #             audio_bytes = base64.b64decode(data["audio"])

# # # #             # Send status update
# # # #             await ws.send_json({"type": "status", "message": "Transcribing..."})

# # # #             state = VoiceState(audio_bytes=audio_bytes)
# # # #             result: VoiceState = await agent_graph.ainvoke(state)

# # # #             if result.error and not result.audio_response:
# # # #                 await ws.send_json({"type": "error", "message": result.error})
# # # #                 continue

# # # #             # Send transcript + answer text first (for UI display)
# # # #             await ws.send_json(
# # # #                 {
# # # #                     "type": "transcript",
# # # #                     "user": result.transcript,
# # # #                     "language": result.detected_language,
# # # #                     "answer": result.answer_text,
# # # #                 }
# # # #             )

# # # #             # Send audio as base64
# # # #             audio_b64 = base64.b64encode(result.audio_response).decode()
# # # #             await ws.send_json({"type": "audio", "data": audio_b64})

# # # #     except WebSocketDisconnect:
# # # #         pass


# # # import os
# # # import json
# # # import base64
# # # from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
# # # from fastapi.middleware.cors import CORSMiddleware
# # # from fastapi.responses import HTMLResponse
# # # from dotenv import load_dotenv
# # # load_dotenv()

# # # from agents.graph import agent_graph
# # # from agents.state import VoiceState
# # # from services.deepgram_stt import transcribe
# # # from services.gemini_translate import translate_to_english, generate_answer
# # # from kb.retriever import retrieve

# # # app = FastAPI(title="Suvit Voice Agent", version="1.0.0")

# # # app.add_middleware(
# # #     CORSMiddleware,
# # #     allow_origins=["*"],
# # #     allow_methods=["*"],
# # #     allow_headers=["*"],
# # # )


# # # # ─── Health check ────────────────────────────────────────────────────────────


# # # @app.get("/health")
# # # async def health():
# # #     checks = {}

# # #     # Check FAISS index
# # #     try:
# # #         from kb.retriever import get_vectorstore

# # #         get_vectorstore()
# # #         checks["faiss_index"] = "ok"
# # #     except Exception as e:
# # #         checks["faiss_index"] = f"error: {e}"

# # #     # Check env keys present
# # #     checks["deepgram_key"] = "ok" if os.environ.get("DEEPGRAM_API_KEY") else "missing"
# # #     checks["gemini_key"] = "ok" if os.environ.get("GEMINI_API_KEY") else "missing"

# # #     all_ok = all(v == "ok" for v in checks.values())
# # #     return {"status": "ok" if all_ok else "degraded", "checks": checks}


# # # # ─── REST: test STT only ─────────────────────────────────────────────────────


# # # @app.post("/transcribe")
# # # async def transcribe_audio(file: UploadFile = File(...)):
# # #     """Upload a .webm/.wav/.mp3 file and get back transcript + detected language."""
# # #     audio_bytes = await file.read()
# # #     transcript, lang = await transcribe(audio_bytes)
# # #     return {"transcript": transcript, "detected_language": lang}


# # # # ─── REST: test RAG only ─────────────────────────────────────────────────────


# # # @app.get("/retrieve")
# # # async def retrieve_chunks(q: str, k: int = 3):
# # #     """Test the FAISS retriever with a plain English query."""
# # #     chunks = retrieve(q, k=k)
# # #     return {"query": q, "chunks": chunks}


# # # # ─── REST: test full pipeline (text in, text out — no audio) ─────────────────


# # # @app.post("/ask")
# # # async def ask_text(body: dict):
# # #     """
# # #     Test the full pipeline with text input (skip STT/TTS).
# # #     Body: { "question": "...", "language": "en" | "hi" | "gu" }
# # #     """
# # #     question = body.get("question", "")
# # #     language = body.get("language", "en")

# # #     english_q = await translate_to_english(question, language)
# # #     chunks = retrieve(english_q)
# # #     answer = await generate_answer(english_q, chunks, language)

# # #     return {
# # #         "question": question,
# # #         "language": language,
# # #         "english_query": english_q,
# # #         "retrieved_chunks": chunks,
# # #         "answer": answer,
# # #     }


# # # @app.post("/voice_to_voice")
# # # async def voice_to_voice(file: UploadFile = File(...)):
# # #     """
# # #     Given an audio file (STT), transcribes, retrieves answer, generates a voice
# # #     response in original language via TTS, and returns direct MP3 bytes.
# # #     """
# # #     from fastapi import Response
# # #     from services.deepgram_stt import transcribe
# # #     from services.gemini_translate import translate_to_english, generate_answer, detect_language
# # #     from kb.retriever import retrieve
# # #     from services.tts_service import synthesize_single

# # #     import urllib.parse
# # #     audio_bytes = await file.read()
# # #     transcript, _ = await transcribe(audio_bytes)
    
# # #     if not transcript or not transcript.strip():
# # #         print("[V2V] Empty transcript detected.")
# # #         audio_out = await synthesize_single("I didn't hear anything. Please try again.", "en")
# # #         return Response(
# # #             content=audio_out, 
# # #             media_type="audio/mp3",
# # #             headers={
# # #                 "X-Transcript": urllib.parse.quote("Empty transcript received"),
# # #                 "X-Language": "en"
# # #             }
# # #         )

# # #     lang = await detect_language(transcript)

# # #     print(f"[V2V] Spoken Transcript: {transcript}")
# # #     print(f"[V2V] Detected Language: {lang}")

# # #     english_q = await translate_to_english(transcript, lang)
# # #     print(f"[V2V] English Translation: {english_q}")

# # #     chunks = retrieve(english_q)
# # #     print(f"[V2V] Retrieved {len(chunks)} chunks.")

# # #     answer = await generate_answer(english_q, chunks, lang)
# # #     print(f"[V2V] Answer generated: {answer}")

# # #     audio_out = await synthesize_single(answer, lang)
# # #     return Response(
# # #         content=audio_out, 
# # #         media_type="audio/mp3",
# # #         headers={
# # #             "X-Transcript": urllib.parse.quote(transcript),
# # #             "X-Language": lang
# # #         }
# # #     )


# # # @app.post("/ask_voice")
# # # async def ask_voice(body: dict):
# # #     """
# # #     Given a text question, retrieves answer and returns directly as an MP3 audio file.
# # #     Body: { "question": "...", "language": "en" | "hi" | "gu" }
# # #     """
# # #     from fastapi import Response
# # #     from services.tts_service import synthesize_single

# # #     question = body.get("question", "")
# # #     language = body.get("language", "en")

# # #     english_q = await translate_to_english(question, language)
# # #     chunks = retrieve(english_q)
# # #     answer = await generate_answer(english_q, chunks, language)

# # #     audio_bytes = await synthesize_single(answer, language)
# # #     return Response(content=audio_bytes, media_type="audio/mp3")


# # # # ─── WebSocket: full voice pipeline ──────────────────────────────────────────


# # # @app.websocket("/ws/voice")
# # # async def voice_endpoint(ws: WebSocket):
# # #     await ws.accept()
# # #     from services.gemini_translate import translate_to_english, generate_answer_stream
# # #     from services.edge_tts_service import synthesize_stream
# # #     from kb.retriever import retrieve
# # #     from services.deepgram_stt import transcribe

# # #     try:
# # #         from services.gemini_translate import translate_to_english, generate_answer_stream, detect_language
# # #         from services.edge_tts_service import synthesize_stream
# # #         from kb.retriever import retrieve
# # #         from services.deepgram_stt import transcribe
# # #         import asyncio
# # #         import json
# # #         import base64

# # #         audio_chunks = []

# # #         while True:
# # #             raw = await ws.receive_text()
# # #             data = json.loads(raw)

# # #             # Support legacy or current payload
# # #             if "type" not in data and "audio" in data:
# # #                 audio_bytes = base64.b64decode(data["audio"])
# # #                 await ws.send_json({"type": "status", "message": "Transcribing..."})
# # #                 transcript, lang = await transcribe(audio_bytes)
# # #                 if not transcript:
# # #                     await ws.send_json({"type": "error", "message": "No speech detected."})
# # #                     continue
# # #                 await ws.send_json({"type": "status", "message": "Thinking..."})
# # #                 english_query = await translate_to_english(transcript, lang)
# # #                 chunks = retrieve(english_query)
# # #                 await ws.send_json({
# # #                     "type": "transcript",
# # #                     "user": transcript,
# # #                     "language": lang,
# # #                     "english_query": english_query,
# # #                     "answer": "[Streaming response...]",
# # #                     "chunks_used": len(chunks),
# # #                 })
# # #                 text_stream = generate_answer_stream(english_query, chunks, lang)
# # #                 await ws.send_json({"type": "audio_start"})
# # #                 async for audio_chunk in synthesize_stream(text_stream, lang):
# # #                     audio_b64 = base64.b64encode(audio_chunk).decode()
# # #                     await ws.send_json({"type": "audio_chunk", "data": audio_b64})
# # #                 await ws.send_json({"type": "audio_end"})
# # #                 continue

# # #             msg_type = data.get("type")
# # #             if msg_type == "audio_chunk":
# # #                 audio_bytes = base64.b64decode(data["audio"])
# # #                 audio_chunks.append(audio_bytes)
                
# # #             elif msg_type == "audio_end":
# # #                 audio_bytes = b"".join(audio_chunks)
# # #                 audio_chunks = []
                
# # #                 if not audio_bytes:
# # #                     await ws.send_json({"type": "error", "message": "No speech detected. Please try again."})
# # #                     continue
                    
# # #                 await ws.send_json({"type": "status", "message": "Transcribing..."})
                
# # #                 transcript, lang = await transcribe(audio_bytes)
                
# # #                 if not transcript:
# # #                     await ws.send_json({"type": "error", "message": "No speech detected. Please try again."})
# # #                     continue
                    
# # #                 await ws.send_json({"type": "status", "message": "Thinking..."})
                
# # #                 lang = await detect_language(transcript)
# # #                 english_query = await translate_to_english(transcript, lang)
# # #                 chunks = retrieve(english_query)
                
# # #                 await ws.send_json({
# # #                     "type": "transcript",
# # #                     "user": transcript,
# # #                     "language": lang,
# # #                     "english_query": english_query,
# # #                     "answer": "[Streaming response...]",
# # #                     "chunks_used": len(chunks),
# # #                 })
                
# # #                 text_stream = generate_answer_stream(english_query, chunks, lang)
# # #                 await ws.send_json({"type": "audio_start"})
                
# # #                 async for audio_chunk in synthesize_stream(text_stream, lang):
# # #                     audio_b64 = base64.b64encode(audio_chunk).decode()
# # #                     await ws.send_json({"type": "audio_chunk", "data": audio_b64})
                
# # #                 await ws.send_json({"type": "audio_end"})

# # #     except WebSocketDisconnect:
# # #         pass
# # #     except Exception as e:
# # #         import traceback
# # #         traceback.print_exc()
# # #         try:
# # #             await ws.send_json({"type": "error", "message": str(e)})
# # #         except:
# # #             pass


# # # # ─── Browser test page ───────────────────────────────────────────────────────


# # # @app.get("/test", response_class=HTMLResponse)
# # # async def test_page():
# # #     return HTMLResponse(TEST_PAGE_HTML)


# # # TEST_PAGE_HTML = """
# # # <!DOCTYPE html>
# # # <html lang="en">
# # # <head>
# # # <meta charset="UTF-8">
# # # <title>Suvit Voice Agent — Test</title>
# # # <style>
# # #   * { box-sizing: border-box; margin: 0; padding: 0; }
# # #   body { font-family: system-ui, sans-serif; background: #f5f5f0; color: #1a1a18; padding: 2rem; }
# # #   h1 { font-size: 1.3rem; font-weight: 500; margin-bottom: 0.25rem; }
# # #   .subtitle { font-size: 0.85rem; color: #666; margin-bottom: 2rem; }

# # #   .card { background: #fff; border: 0.5px solid #ddd; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; }
# # #   .card h2 { font-size: 0.9rem; font-weight: 500; color: #444; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.04em; }

# # #   label { font-size: 0.85rem; color: #555; display: block; margin-bottom: 4px; }
# # #   input[type=text], textarea, select {
# # #     width: 100%; padding: 8px 10px; border: 0.5px solid #ccc;
# # #     border-radius: 8px; font-size: 0.9rem; font-family: inherit;
# # #     background: #fafaf8; color: #1a1a18; margin-bottom: 12px;
# # #   }
# # #   textarea { min-height: 80px; resize: vertical; }
# # #   button {
# # #     padding: 8px 18px; border-radius: 8px; border: 0.5px solid #bbb;
# # #     background: #fff; font-size: 0.875rem; cursor: pointer; font-family: inherit;
# # #     transition: background 0.15s;
# # #   }
# # #   button:hover { background: #f0efeb; }
# # #   button:disabled { opacity: 0.5; cursor: not-allowed; }
# # #   button.primary { background: #378ADD; color: #fff; border-color: #185FA5; }
# # #   button.primary:hover { background: #2e78cc; }
# # #   button.danger { background: #D85A30; color: #fff; border-color: #993C1D; }

# # #   #mic-btn { width: 72px; height: 72px; border-radius: 50%; font-size: 1.6rem; border: none; }
# # #   .mic-row { display: flex; align-items: center; gap: 16px; margin-bottom: 1rem; }
# # #   .mic-status { font-size: 0.85rem; color: #666; }

# # #   .log { background: #f9f8f5; border: 0.5px solid #e0e0d8; border-radius: 8px;
# # #     padding: 12px; font-family: monospace; font-size: 0.8rem; min-height: 80px;
# # #     max-height: 260px; overflow-y: auto; white-space: pre-wrap; color: #333; }

# # #   .badge { display: inline-block; font-size: 0.75rem; padding: 2px 8px;
# # #     border-radius: 20px; margin-left: 8px; }
# # #   .badge-en { background: #E6F1FB; color: #0C447C; }
# # #   .badge-hi { background: #EAF3DE; color: #27500A; }
# # #   .badge-gu { background: #FAEEDA; color: #633806; }

# # #   .tabs { display: flex; gap: 8px; margin-bottom: 1rem; }
# # #   .tab { padding: 6px 14px; border-radius: 8px; border: 0.5px solid #ccc;
# # #     font-size: 0.85rem; cursor: pointer; background: #fff; }
# # #   .tab.active { background: #1a1a18; color: #fff; border-color: #1a1a18; }

# # #   .section { display: none; }
# # #   .section.active { display: block; }

# # #   audio { width: 100%; margin-top: 10px; }
# # #   .chunk { background: #f0efeb; border-left: 3px solid #378ADD;
# # #     padding: 8px 10px; border-radius: 0 6px 6px 0; margin-bottom: 8px;
# # #     font-size: 0.82rem; line-height: 1.5; }
# # # </style>
# # # </head>
# # # <body>

# # # <h1>Suvit voice agent — test console</h1>
# # # <p class="subtitle">FastAPI dev tools · <a href="/docs" target="_blank">Swagger UI</a> · <a href="/health" target="_blank">Health check</a></p>

# # # <div class="tabs">
# # #   <button class="tab active" onclick="switchTab('voice')">Voice (WebSocket)</button>
# # #   <button class="tab" onclick="switchTab('text')">Text only (/ask)</button>
# # #   <button class="tab" onclick="switchTab('ask_voice')">Text to Voice (/ask_voice)</button>
# # #   <button class="tab" onclick="switchTab('voice_to_voice')">Voice to Voice (/voice_to_voice)</button>
# # #   <button class="tab" onclick="switchTab('rag')">RAG retriever</button>
# # #   <button class="tab" onclick="switchTab('stt')">STT only</button>
# # # </div>

# # # <!-- ── VOICE TAB ─────────────────────────────────────────────── -->
# # # <div id="tab-voice" class="section active">
# # #   <div class="card">
# # #     <h2>Voice pipeline (full end-to-end)</h2>
# # #     <div class="mic-row">
# # #       <button id="mic-btn" class="primary" onclick="toggleRec()">🎤</button>
# # #       <span class="mic-status" id="mic-status">Click to record</span>
# # #     </div>
# # #     <audio id="audio-out" controls style="display:none"></audio>
# # #     <div style="margin-top:12px">
# # #       <label>Pipeline log</label>
# # #       <div class="log" id="voice-log">Waiting for recording...</div>
# # #     </div>
# # #   </div>
# # # </div>

# # # <!-- ── TEXT TAB ──────────────────────────────────────────────── -->
# # # <div id="tab-text" class="section">
# # #   <div class="card">
# # #     <h2>Text → answer (no audio)</h2>
# # #     <label>Question</label>
# # #     <textarea id="text-q" placeholder="e.g. How do I import a bank statement?"></textarea>
# # #     <label>Language</label>
# # #     <select id="text-lang">
# # #       <option value="en">English</option>
# # #       <option value="hi">Hindi</option>
# # #       <option value="gu">Gujarati</option>
# # #     </select>
# # #     <button class="primary" onclick="askText()">Send</button>
# # #     <div style="margin-top:12px">
# # #       <label>Response</label>
# # #       <div class="log" id="text-log">—</div>
# # #     </div>
# # #   </div>
# # # </div>

# # # <!-- ── ASK VOICE TAB ────────────────────────────────────────── -->
# # # <div id="tab-ask_voice" class="section">
# # #   <div class="card">
# # #     <h2>Text → voice answer (/ask_voice)</h2>
# # #     <label>Question</label>
# # #     <textarea id="voice-q" placeholder="e.g. How do I import a bank statement?"></textarea>
# # #     <label>Language</label>
# # #     <select id="voice-lang">
# # #       <option value="en">English</option>
# # #       <option value="hi">Hindi</option>
# # #       <option value="gu">Gujarati</option>
# # #     </select>
# # #     <button class="primary" onclick="askVoice()">Speak</button>
# # #     <div style="margin-top:12px">
# # #       <audio id="ask-voice-out" controls style="display:none; margin-bottom:12px"></audio>
# # #       <div class="log" id="voice-test-log">—</div>
# # #     </div>
# # #   </div>
# # # </div>

# # # <!-- ── VOICE TO VOICE TAB ────────────────────────────────────── -->
# # # <div id="tab-voice_to_voice" class="section">
# # #   <div class="card">
# # #     <h2>Voice → voice answer (/voice_to_voice)</h2>
# # #     <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 12px;">
# # #       <button id="v2v-mic-btn" class="primary" onmousedown="startV2VRec()" onmouseup="stopV2VRec()"
# # #               ontouchstart="startV2VRec()" ontouchend="stopV2VRec()">🎤</button>
# # #       <span id="v2v-mic-status">Hold to record and ask</span>
# # #     </div>
# # #     <label>Or upload audio file (.webm / .mp3 / .wav / .m4a)</label>
# # #     <input type="file" id="v2v-file" accept="audio/*" style="margin-bottom:12px">
# # #     <button class="primary" onclick="testVoiceToVoice()">Send Audio</button>
# # #     <div style="margin-top:12px">
# # #       <audio id="v2v-audio-out" controls style="display:none; margin-bottom:12px"></audio>
# # #       <div class="log" id="v2v-log">—</div>
# # #     </div>
# # #   </div>
# # # </div>

# # # <!-- ── RAG TAB ───────────────────────────────────────────────── -->
# # # <div id="tab-rag" class="section">
# # #   <div class="card">
# # #     <h2>RAG retriever test</h2>
# # #     <label>Query (English)</label>
# # #     <input type="text" id="rag-q" placeholder="e.g. bank statement failed status">
# # #     <label>Top-K results</label>
# # #     <select id="rag-k">
# # #       <option>3</option><option>5</option><option>2</option><option>1</option>
# # #     </select>
# # #     <button class="primary" onclick="testRag()">Retrieve</button>
# # #     <div style="margin-top:12px" id="rag-results"></div>
# # #   </div>
# # # </div>

# # # <!-- ── STT TAB ───────────────────────────────────────────────── -->
# # # <div id="tab-stt" class="section">
# # #   <div class="card">
# # #     <h2>STT only — upload audio file</h2>
# # #     <label>Audio file (.webm / .mp3 / .wav)</label>
# # #     <input type="file" id="stt-file" accept="audio/*" style="margin-bottom:12px">
# # #     <button class="primary" onclick="testStt()">Transcribe</button>
# # #     <div style="margin-top:12px">
# # #       <label>Result</label>
# # #       <div class="log" id="stt-log">—</div>
# # #     </div>
# # #   </div>
# # # </div>

# # # <script>
# # # // ── Tab switching ────────────────────────────────────────────
# # # function switchTab(name) {
# # #   document.querySelectorAll('.tab').forEach((t,i) => {
# # #     const tabs = ['voice','text','ask_voice','voice_to_voice','rag','stt'];
# # #     t.classList.toggle('active', tabs[i] === name);
# # #   });
# # #   document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
# # #   document.getElementById('tab-' + name).classList.add('active');
# # # }

# # # // ── Voice WebSocket ──────────────────────────────────────────
# # # let ws = null;
# # # let mediaRecorder = null;
# # # let chunks = [];

# # # function getWs() {
# # #   if (ws && ws.readyState === WebSocket.OPEN) return ws;
# # #   const proto = location.protocol === 'https:' ? 'wss' : 'ws';
# # #   ws = new WebSocket(proto + '://' + location.host + '/ws/voice');
# # #   ws.onmessage = handleWsMessage;
# # #   ws.onerror = () => voiceLog('WebSocket error — is the server running?');
# # #   return ws;
# # # }

# # # let audioQueue = [];
# # # let mediaSource = null;
# # # let sourceBuffer = null;

# # # function handleWsMessage(e) {
# # #   const msg = JSON.parse(e.data);
# # #   if (msg.type === 'status') {
# # #     voiceLog('⏳ ' + msg.message);
# # #     document.getElementById('mic-status').textContent = msg.message;
# # #   } else if (msg.type === 'transcript') {
# # #     voiceLog('');
# # #     voiceLog('USER  ' + msg.user);
# # #     voiceLog('LANG  ' + msg.language + ' → English: "' + msg.english_query + '"');
# # #     voiceLog('KB    ' + msg.chunks_used + ' chunks retrieved');
# # #     voiceLog('AGENT ' + msg.answer);
# # #   } else if (msg.type === 'audio_start') {
# # #     audioQueue = [];
# # #     mediaSource = new MediaSource();
# # #     const audio = document.getElementById('audio-out');
# # #     audio.src = URL.createObjectURL(mediaSource);
# # #     audio.style.display = 'block';
# # #     audio.play();
# # #     mediaSource.addEventListener('sourceopen', () => {
# # #       sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
# # #       sourceBuffer.addEventListener('updateend', () => {
# # #         if (audioQueue.length > 0 && !sourceBuffer.updating) {
# # #           sourceBuffer.appendBuffer(audioQueue.shift());
# # #         }
# # #       });
# # #     });
# # #     document.getElementById('mic-status').textContent = 'Speaking...';
# # #   } else if (msg.type === 'audio_chunk') {
# # #     const bytes = Uint8Array.from(atob(msg.data), c => c.charCodeAt(0));
# # #     if (sourceBuffer && !sourceBuffer.updating) {
# # #       sourceBuffer.appendBuffer(bytes.buffer);
# # #     } else {
# # #       audioQueue.push(bytes.buffer);
# # #     }
# # #   } else if (msg.type === 'audio_end') {
# # #     document.getElementById('mic-status').textContent = 'Hold to record';
# # #   } else if (msg.type === 'error') {
# # #     voiceLog('ERROR ' + msg.message);
# # #     document.getElementById('mic-status').textContent = 'Error — see log';
# # #   }
# # # }

# # # let isRecording = false;

# # # async function toggleRec() {
# # #   if (!isRecording) {
# # #     isRecording = true;
# # #     await startRec();
# # #   } else {
# # #     isRecording = false;
# # #     stopRec();
# # #   }
# # # }

# # # async function startRec() {
# # #   const ws = getWs();
# # #   if (ws.readyState === WebSocket.CONNECTING) {
# # #     ws.addEventListener('open', () => startRecRecording());
# # #   } else {
# # #     startRecRecording();
# # #   }
# # # }

# # # async function startRecRecording() {
# # #   const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
# # #   mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
# # #   mediaRecorder.ondataavailable = async (e) => { 
# # #     if (e.data.size > 0 && ws && ws.readyState === WebSocket.OPEN) {
# # #       const buf = await e.data.arrayBuffer();
# # #       const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
# # #       ws.send(JSON.stringify({ type: 'audio_chunk', audio: b64 }));
# # #     }
# # #   };
# # #   mediaRecorder.onstop = () => {
# # #     if (ws && ws.readyState === WebSocket.OPEN) {
# # #       ws.send(JSON.stringify({ type: 'audio_end' }));
# # #     }
# # #     stream.getTracks().forEach(t => t.stop());
# # #   };
# # #   mediaRecorder.start(250);
# # #   document.getElementById('mic-btn').textContent = '⏹';
# # #   document.getElementById('mic-btn').classList.add('danger');
# # #   document.getElementById('mic-btn').classList.remove('primary');
# # #   document.getElementById('mic-status').textContent = 'Recording (click again to answer)...';
# # # }

# # # function stopRec() {
# # #   if (mediaRecorder && mediaRecorder.state === 'recording') {
# # #     mediaRecorder.stop();
# # #     isRecording = false;
# # #     document.getElementById('mic-btn').textContent = '🎤';
# # #     document.getElementById('mic-btn').classList.add('primary');
# # #     document.getElementById('mic-btn').classList.remove('danger');
# # #     document.getElementById('mic-status').textContent = 'Processing...';
# # #   }
# # # }

# # # function voiceLog(msg) {
# # #   const el = document.getElementById('voice-log');
# # #   el.textContent = (el.textContent === 'Waiting for recording...' ? '' : el.textContent)
# # #     + (msg ? msg + '\\n' : '\\n');
# # #   el.scrollTop = el.scrollHeight;
# # # }

# # # // ── Text /ask ────────────────────────────────────────────────
# # # async function askText() {
# # #   const q = document.getElementById('text-q').value.trim();
# # #   const lang = document.getElementById('text-lang').value;
# # #   if (!q) return;
# # #   document.getElementById('text-log').textContent = 'Calling /ask ...';
# # #   try {
# # #     const res = await fetch('/ask', {
# # #       method: 'POST',
# # #       headers: { 'Content-Type': 'application/json' },
# # #       body: JSON.stringify({ question: q, language: lang }),
# # #     });
# # #     const data = await res.json();
# # #     const out = [
# # #       'ENGLISH QUERY: ' + data.english_query,
# # #       '',
# # #       'CHUNKS RETRIEVED: ' + data.retrieved_chunks.length,
# # #       data.retrieved_chunks.map((c,i) => `[${i+1}] ${c.slice(0,120)}...`).join('\\n'),
# # #       '',
# # #       'ANSWER (' + data.language + '):',
# # #       data.answer,
# # #     ].join('\\n');
# # #     document.getElementById('text-log').textContent = out;
# # #   } catch(e) {
# # #     document.getElementById('text-log').textContent = 'Error: ' + e.message;
# # #   }
# # # }

# # # async function askVoice() {
# # #   const q = document.getElementById('voice-q').value.trim();
# # #   const lang = document.getElementById('voice-lang').value;
# # #   if (!q) return;
# # #   document.getElementById('voice-test-log').textContent = 'Generating speech...';
# # #   try {
# # #     const res = await fetch('/ask_voice', {
# # #       method: 'POST',
# # #       headers: { 'Content-Type': 'application/json' },
# # #       body: JSON.stringify({ question: q, language: lang }),
# # #     });
# # #     if (!res.ok) {
# # #       const txt = await res.text();
# # #       throw new Error(txt);
# # #     }
# # #     const blob = await res.blob();
# # #     const url = URL.createObjectURL(blob);
# # #     const audio = document.getElementById('ask-voice-out');
# # #     audio.src = url;
# # #     audio.style.display = 'block';
# # #     audio.play();
# # #     document.getElementById('voice-test-log').textContent = 'Playing audio...';
# # #   } catch(e) {
# # #     document.getElementById('voice-test-log').textContent = 'Error: ' + e.message;
# # #   }
# # # }

# # # let v2vRecorder = null;
# # # let v2vChunks = [];

# # # async function startV2VRec() {
# # #   const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
# # #   v2vRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
# # #   v2vChunks = [];
# # #   v2vRecorder.ondataavailable = e => { if (e.data.size > 0) v2vChunks.push(e.data); };
# # #   v2vRecorder.onstop = async () => {
# # #     await new Promise(r => setTimeout(r, 150));
# # #     const blob = new Blob(v2vChunks, { type: 'audio/webm' });
# # #     document.getElementById('v2v-log').textContent = 'Processing recorded audio...';
# # #     const form = new FormData();
# # #     form.append('file', blob, 'recorded.webm');
# # #     try {
# # #       const res = await fetch('/voice_to_voice', { method: 'POST', body: form });
# # #       if (!res.ok) {
# # #         const txt = await res.text();
# # #         throw new Error(txt);
# # #       }
# # #       const raw_transcript = res.headers.get('X-Transcript') || '';
# # #       const transcript = decodeURIComponent(raw_transcript);
# # #       const lang = res.headers.get('X-Language') || '';
      
# # #       const resBlob = await res.blob();
# # #       const url = URL.createObjectURL(resBlob);
# # #       const audio = document.getElementById('v2v-audio-out');
# # #       audio.src = url;
# # #       audio.style.display = 'block';
# # #       audio.play();
      
# # #       document.getElementById('v2v-log').textContent = 
# # #         `TRANSCRIPT DETECTED: ${transcript}\nLANGUAGE: ${lang}\nPlaying answer...`;
# # #     } catch(e) {
# # #       document.getElementById('v2v-log').textContent = 'Error: ' + e.message;
# # #     }
# # #     stream.getTracks().forEach(t => t.stop());
# # #   };
# # #   v2vRecorder.start(250);
# # #   document.getElementById('v2v-mic-btn').textContent = '⏹';
# # #   document.getElementById('v2v-mic-btn').classList.add('danger');
# # #   document.getElementById('v2v-mic-btn').classList.remove('primary');
# # #   document.getElementById('v2v-mic-status').textContent = 'Recording...';
# # # }

# # # function stopV2VRec() {
# # #   if (v2vRecorder && v2vRecorder.state === 'recording') {
# # #     v2vRecorder.stop();
# # #     document.getElementById('v2v-mic-btn').textContent = '🎤';
# # #     document.getElementById('v2v-mic-btn').classList.add('primary');
# # #     document.getElementById('v2v-mic-btn').classList.remove('danger');
# # #     document.getElementById('v2v-mic-status').textContent = 'Processing...';
# # #   }
# # # }

# # # async function testVoiceToVoice() {
# # #   const file = document.getElementById('v2v-file').files[0];
# # #   if (!file) return;
# # #   document.getElementById('v2v-log').textContent = 'Processing voice request...';
# # #   const form = new FormData();
# # #   form.append('file', file);
# # #   try {
# # #     const res = await fetch('/voice_to_voice', { method: 'POST', body: form });
# # #     if (!res.ok) {
# # #       const txt = await res.text();
# # #       throw new Error(txt);
# # #     }
# # #     const raw_transcript = res.headers.get('X-Transcript') || '';
# # #     const transcript = decodeURIComponent(raw_transcript);
# # #     const lang = res.headers.get('X-Language') || '';
    
# # #     const blob = await res.blob();
# # #     const url = URL.createObjectURL(blob);
# # #     const audio = document.getElementById('v2v-audio-out');
# # #     audio.src = url;
# # #     audio.style.display = 'block';
# # #     audio.play();
    
# # #     document.getElementById('v2v-log').textContent = 
# # #       'TRANSCRIPT DETECTED: ' + transcript + '\\nLANGUAGE: ' + lang + '\\nPlaying answer...';
# # #   } catch(e) {
# # #     document.getElementById('v2v-log').textContent = 'Error: ' + e.message;
# # #   }
# # # }

# # # // ── RAG retriever ────────────────────────────────────────────
# # # async function testRag() {
# # #   const q = document.getElementById('rag-q').value.trim();
# # #   const k = document.getElementById('rag-k').value;
# # #   if (!q) return;
# # #   document.getElementById('rag-results').innerHTML = 'Retrieving...';
# # #   try {
# # #     const res = await fetch('/retrieve?q=' + encodeURIComponent(q) + '&k=' + k);
# # #     const data = await res.json();
# # #     const html = data.chunks.map((c, i) => `<div class="chunk"><strong>#${i+1}</strong><br>${c}</div>`).join('');
# # #     document.getElementById('rag-results').innerHTML = html || '<em>No results</em>';
# # #   } catch(e) {
# # #     document.getElementById('rag-results').innerHTML = 'Error: ' + e.message;
# # #   }
# # # }

# # # // ── STT file upload ──────────────────────────────────────────
# # # async function testStt() {
# # #   const file = document.getElementById('stt-file').files[0];
# # #   if (!file) return;
# # #   document.getElementById('stt-log').textContent = 'Transcribing...';
# # #   const form = new FormData();
# # #   form.append('file', file);
# # #   try {
# # #     const res = await fetch('/transcribe', { method: 'POST', body: form });
# # #     const data = await res.json();
# # #     document.getElementById('stt-log').textContent =
# # #       'TRANSCRIPT: ' + data.transcript + '\\nLANGUAGE:   ' + data.detected_language;
# # #   } catch(e) {
# # #     document.getElementById('stt-log').textContent = 'Error: ' + e.message;
# # #   }
# # # }
# # # </script>
# # # </body>
# # # </html>
# # # """































# """
# main.py — Suvit Voice Agent
# ────────────────────────────
# FastAPI server exposing:

#   GET  /health              — liveness + dependency check
#   GET  /test                — browser test console (HTML)
#   POST /transcribe          — STT only (file upload)
#   GET  /retrieve            — RAG retriever test (text query)
#   POST /ask                 — text in → text out (no audio)
#   POST /ask_voice           — text in → MP3 out
#   POST /voice_to_voice      — audio file in → MP3 out
#   WS   /ws/voice            — full streaming voice pipeline

# Services:
#   STT         : Deepgram nova-3  (language=multi → en/hi/gu)
#   Translation : OpenAI GPT-4o-mini (primary) → Gemini 2.5 Flash (fallback)
#   Generation  : Gemini 2.5 Flash (primary)   → OpenAI GPT-4o-mini (fallback)
#   TTS         : Sarvam Bulbul v3 (primary)   → edge-tts (fallback)
# """

# import os
# import json
# import base64
# import urllib.parse

# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Response
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse
# from dotenv import load_dotenv

# load_dotenv()

# from agents.graph import agent_graph
# from agents.state import VoiceState
# from services.deepgram_stt import transcribe
# from services.sarvam_tts import synthesize, synthesize_stream
# from services.gemini_translate import (
#     translate_to_english,
#     generate_answer,
# )
# from services.realtime_voice import RealtimeVoiceSession
# from services.voice_pipeline import run_voice_pipeline
# from kb.retriever import retrieve
# from livekit import api

# app = FastAPI(title="Suvit Voice Agent", version="2.0.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ─── Health ──────────────────────────────────────────────────────────────────

# @app.get("/health")
# async def health():
#     checks: dict = {}

#     try:
#         from kb.retriever import get_vectorstore
#         get_vectorstore()
#         checks["faiss_index"] = "ok"
#     except Exception as e:
#         checks["faiss_index"] = f"error: {e}"

#     checks["deepgram_key"]  = "ok" if os.environ.get("DEEPGRAM_API_KEY")  else "missing"
#     checks["openai_key"]    = "ok" if os.environ.get("OPENAI_API_KEY")    else "missing"
#     checks["gemini_key"]    = "ok" if os.environ.get("GOOGLE_API_KEY")    else "missing"
#     checks["sarvam_key"]    = "ok" if os.environ.get("SARVAMAI_API_KEY")  else "missing (edge-tts fallback active)"

#     all_ok = all("error" not in v and "missing" not in v for v in checks.values()
#                  if "fallback" not in v)
#     return {"status": "ok" if all_ok else "degraded", "checks": checks}


# # ─── LiveKit Token ──────────────────────────────────────────────────────────

# @app.get("/api/token")
# async def get_token(room: str, participant: str = "user"):
#     """
#     Generate an access token for a LiveKit room.
#     Query params:
#         room        : name of the room to join (required)
#         participant : identity of the user (defaults to 'user')
#     """
#     token = (
#         api.AccessToken(
#             os.environ.get("LIVEKIT_API_KEY"),
#             os.environ.get("LIVEKIT_API_SECRET")
#         )
#         .with_identity(participant)
#         .with_grants(
#             api.VideoGrants(
#                 room_join=True,
#                 room=room,
#             )
#         )
#         .to_jwt()
#     )
#     return {"token": token}


# # ─── STT test ────────────────────────────────────────────────────────────────

# @app.post("/transcribe")
# async def transcribe_audio(file: UploadFile = File(...)):
#     """Upload any audio file → get transcript + detected language."""
#     audio_bytes = await file.read()
#     transcript, lang = await transcribe(audio_bytes)
#     return {"transcript": transcript, "detected_language": lang}


# # ─── RAG test ────────────────────────────────────────────────────────────────

# @app.get("/retrieve")
# async def retrieve_chunks(q: str, k: int = 3):
#     """Test FAISS retriever with a plain English query."""
#     chunks = retrieve(q, k=k)
#     return {"query": q, "chunks": chunks}


# # ─── Text → text ─────────────────────────────────────────────────────────────

# @app.post("/ask")
# async def ask_text(body: dict):
#     """
#     Full pipeline without audio.
#     Body: { "question": "...", "language": "en" | "hi" | "gu" }
#     """
#     question = body.get("question", "")
#     language = body.get("language", "en")

#     english_q = await translate_to_english(question, language)
#     chunks    = retrieve(english_q)
#     answer    = await generate_answer(english_q, chunks, language)

#     return {
#         "question":         question,
#         "language":         language,
#         "english_query":    english_q,
#         "retrieved_chunks": chunks,
#         "answer":           answer,
#     }


# # ─── Text → voice ────────────────────────────────────────────────────────────

# @app.post("/ask_voice")
# async def ask_voice(body: dict):
#     """
#     Text question → MP3 audio response.
#     Body: { "question": "...", "language": "en" | "hi" | "gu" }
#     """
#     question = body.get("question", "")
#     language = body.get("language", "en")

#     english_q   = await translate_to_english(question, language)
#     chunks      = retrieve(english_q)
#     answer      = await generate_answer(english_q, chunks, language)
#     audio_bytes = await synthesize(answer, language)

#     return Response(content=audio_bytes, media_type="audio/mpeg")


# # ─── Voice file → voice ───────────────────────────────────────────────────────

# @app.post("/voice_to_voice")
# async def voice_to_voice(file: UploadFile = File(...)):
#     """
#     Upload audio → get back MP3 audio answer in the user's language.

#     Response headers:
#         X-Transcript : URL-encoded transcript
#         X-Language   : detected language code (en / hi / gu)
#     """
#     audio_bytes = await file.read()

#     try:
#         result = await run_voice_pipeline(audio_bytes, k=5, mime_type=file.content_type)
#     except Exception as e:
#         print(f"[V2V] STT failed: {e}")
#         # Fallback: return a spoken error message instead of crashing
#         try:
#             audio_out = await synthesize(
#                 "Sorry, I couldn't process your audio. The speech service is temporarily unavailable. Please try again.", "en"
#             )
#             return Response(
#                 content=audio_out,
#                 media_type="audio/mpeg",
#                 headers={
#                     "X-Transcript": urllib.parse.quote("STT error"),
#                     "X-Language":   "en",
#                 },
#             )
#         except Exception:
#             return Response(
#                 content=b"",
#                 media_type="audio/mpeg",
#                 headers={"X-Transcript": "STT+TTS error", "X-Language": "en"},
#             )

#     print(
#         f"[V2V] transcript='{result.transcript}' | lang={result.input_language} | "
#         f"english_query='{result.english_query}' | chunks={len(result.retrieved_chunks)}"
#     )

#     return Response(
#         content=result.audio_bytes,
#         media_type="audio/mpeg",
#         headers={
#             "X-Transcript": urllib.parse.quote(result.transcript),
#             "X-Language": result.input_language,
#         },
#     )


# # ─── WebSocket: full streaming voice pipeline ─────────────────────────────────

# @app.websocket("/ws/voice")
# async def voice_endpoint(ws: WebSocket):
#     """
#     WebSocket voice pipeline with streaming TTS.

#     Client message types (JSON):
#         { "type": "audio_chunk", "audio": "<base64>" }  — send while recording
#         { "type": "audio_end" }                          — signals end of recording

#     Server message types (JSON):
#         { "type": "status",      "message": "..." }
#         { "type": "transcript",  "user": "...", "language": "...",
#                                  "english_query": "...", "chunks_used": N }
#         { "type": "audio_start" }
#         { "type": "audio_chunk", "data": "<base64>" }    — streaming TTS audio
#         { "type": "audio_end" }
#         { "type": "error",       "message": "..." }
#     """
#     await ws.accept()
#     session = RealtimeVoiceSession(ws)
#     audio_chunks: list[bytes] = []

#     try:
#         await session.start()

#         while True:
#             message = await ws.receive()

#             if message.get("bytes") is not None:
#                 await session.process_audio_chunk(message["bytes"])
#                 continue

#             text_payload = message.get("text")
#             if text_payload is None:
#                 continue

#             data = json.loads(text_payload)
#             msg_type = data.get("type")

#             if msg_type == "interrupt":
#                 await session.interrupt()
#                 continue

#             if msg_type == "ping":
#                 await ws.send_json({"type": "pong"})
#                 continue

#             # ── Accumulate audio chunks ──────────────────────────────────────
#             if msg_type == "audio_chunk":
#                 audio_chunks.append(base64.b64decode(data["audio"]))
#                 continue

#             # ── End of audio — run full pipeline ────────────────────────────
#             if msg_type == "audio_end":
#                 audio_bytes  = b"".join(audio_chunks)
#                 audio_chunks = []

#                 if not audio_bytes:
#                     await ws.send_json({"type": "error", "message": "No audio received."})
#                     continue

#                 await ws.send_json({"type": "status", "message": "Transcribing..."})
#                 await ws.send_json({"type": "status", "message": "Thinking..."})
#                 try:
#                     result = await run_voice_pipeline(audio_bytes, k=5)
#                 except Exception as e:
#                     await ws.send_json({"type": "error", "message": str(e)})
#                     continue

#                 await ws.send_json({
#                     "type": "transcript",
#                     "user": result.transcript,
#                     "language": result.input_language,
#                     "english_query": result.english_query,
#                     "chunks_used": len(result.retrieved_chunks),
#                 })

#                 await ws.send_json({"type": "audio_start"})
#                 audio_b64 = base64.b64encode(result.audio_bytes).decode()
#                 await ws.send_json({"type": "audio_chunk", "data": audio_b64})
#                 await ws.send_json({"type": "audio_end"})
#                 continue

#             # ── Legacy payload: { "audio": "<base64>" } (single-shot) ────────
#             if "audio" in data and msg_type is None:
#                 await ws.send_json({"type": "status", "message": "Transcribing..."})
#                 await ws.send_json({"type": "status", "message": "Thinking..."})
#                 audio_bytes = base64.b64decode(data["audio"])
#                 mime_type = data.get("mime")
#                 try:
#                     result = await run_voice_pipeline(audio_bytes, k=5, mime_type=mime_type)
#                 except Exception as e:
#                     await ws.send_json({"type": "error", "message": str(e)})
#                     continue

#                 await ws.send_json({
#                     "type": "transcript",
#                     "user": result.transcript,
#                     "language": result.input_language,
#                     "english_query": result.english_query,
#                     "chunks_used": len(result.retrieved_chunks),
#                 })

#                 await ws.send_json({"type": "audio_start"})
#                 audio_b64 = base64.b64encode(result.audio_bytes).decode()
#                 await ws.send_json({"type": "audio_chunk", "data": audio_b64})
#                 await ws.send_json({"type": "audio_end"})

#     except WebSocketDisconnect:
#         await session.close()
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         try:
#             await ws.send_json({"type": "error", "message": str(e)})
#         except Exception:
#             pass
#         await session.close()


# # ─── Browser test page ────────────────────────────────────────────────────────

# @app.get("/test", response_class=HTMLResponse)
# async def test_page():
#     return HTMLResponse(TEST_PAGE_HTML)


# TEST_PAGE_HTML = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
# <meta charset="UTF-8">
# <title>Suvit Voice Agent — Test</title>
# <style>
#   * { box-sizing: border-box; margin: 0; padding: 0; }
#   body { font-family: system-ui, sans-serif; background: #f5f5f0; color: #1a1a18; padding: 2rem; }
#   h1 { font-size: 1.3rem; font-weight: 500; margin-bottom: 0.25rem; }
#   .subtitle { font-size: 0.85rem; color: #666; margin-bottom: 2rem; }

#   .card { background: #fff; border: 0.5px solid #ddd; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; }
#   .card h2 { font-size: 0.9rem; font-weight: 500; color: #444; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.04em; }

#   label { font-size: 0.85rem; color: #555; display: block; margin-bottom: 4px; }
#   input[type=text], textarea, select {
#     width: 100%; padding: 8px 10px; border: 0.5px solid #ccc;
#     border-radius: 8px; font-size: 0.9rem; font-family: inherit;
#     background: #fafaf8; color: #1a1a18; margin-bottom: 12px;
#   }
#   textarea { min-height: 80px; resize: vertical; }
#   button {
#     padding: 8px 18px; border-radius: 8px; border: 0.5px solid #bbb;
#     background: #fff; font-size: 0.875rem; cursor: pointer; font-family: inherit;
#   }
#   button:hover { background: #f0efeb; }
#   button.primary { background: #378ADD; color: #fff; border-color: #185FA5; }
#   button.primary:hover { background: #2e78cc; }
#   button.danger { background: #D85A30; color: #fff; border-color: #993C1D; }

#   #mic-btn { width: 72px; height: 72px; border-radius: 50%; font-size: 1.6rem; border: none; }
#   .mic-row { display: flex; align-items: center; gap: 16px; margin-bottom: 1rem; }
#   .mic-status { font-size: 0.85rem; color: #666; }

#   .log { background: #f9f8f5; border: 0.5px solid #e0e0d8; border-radius: 8px;
#     padding: 12px; font-family: monospace; font-size: 0.8rem; min-height: 80px;
#     max-height: 260px; overflow-y: auto; white-space: pre-wrap; color: #333; }

#   .tabs { display: flex; gap: 8px; margin-bottom: 1rem; flex-wrap: wrap; }
#   .tab { padding: 6px 14px; border-radius: 8px; border: 0.5px solid #ccc;
#     font-size: 0.85rem; cursor: pointer; background: #fff; }
#   .tab.active { background: #1a1a18; color: #fff; border-color: #1a1a18; }

#   .section { display: none; }
#   .section.active { display: block; }
#   audio { width: 100%; margin-top: 10px; }
#   .chunk { background: #f0efeb; border-left: 3px solid #378ADD;
#     padding: 8px 10px; border-radius: 0 6px 6px 0; margin-bottom: 8px;
#     font-size: 0.82rem; line-height: 1.5; }
#   .badge { display: inline-block; font-size: 0.75rem; padding: 2px 8px;
#     border-radius: 20px; margin-left: 6px; font-weight: 500; }
#   .badge-en { background: #E6F1FB; color: #0C447C; }
#   .badge-hi { background: #EAF3DE; color: #27500A; }
#   .badge-gu { background: #FAEEDA; color: #633806; }
# </style>
# </head>
# <body>

# <h1>Suvit voice agent <span style="font-weight:400;color:#888">v2</span></h1>
# <p class="subtitle">
#   STT: Deepgram nova-3 &nbsp;·&nbsp;
#   TTS: Sarvam Bulbul v3 &nbsp;·&nbsp;
#   LLM: Gemini 2.5 Flash / GPT-4o-mini &nbsp;·&nbsp;
#   <a href="/docs" target="_blank">Swagger</a> &nbsp;·&nbsp;
#   <a href="/health" target="_blank">Health</a>
# </p>

# <div class="tabs">
#   <button class="tab active" onclick="switchTab('voice')">🎤 Voice (WS)</button>
#   <button class="tab" onclick="switchTab('v2v')">🔄 Voice-to-Voice (REST)</button>
#   <button class="tab" onclick="switchTab('text')">💬 Text only</button>
#   <button class="tab" onclick="switchTab('ask_voice')">🔊 Text to Voice</button>
#   <button class="tab" onclick="switchTab('rag')">📚 RAG test</button>
#   <button class="tab" onclick="switchTab('stt')">🎧 STT only</button>
# </div>

# <!-- VOICE WebSocket -->
# <div id="tab-voice" class="section active">
#   <div class="card">
#     <h2>Full streaming pipeline — WebSocket</h2>
#     <div class="mic-row">
#       <button id="mic-btn" class="primary"
#         onmousedown="startRec()" onmouseup="stopRec()"
#         ontouchstart="startRec()" ontouchend="stopRec()">🎤</button>
#       <span class="mic-status" id="mic-status">Hold to record</span>
#     </div>
#     <audio id="audio-out" controls style="display:none"></audio>
#     <div style="margin-top:12px">
#       <label>Log</label>
#       <div class="log" id="voice-log">Waiting...</div>
#     </div>
#   </div>
# </div>

# <!-- VOICE TO VOICE REST -->
# <div id="tab-v2v" class="section">
#   <div class="card">
#     <h2>Voice to voice — REST /voice_to_voice</h2>
#     <div style="display:flex;gap:10px;align-items:center;margin-bottom:12px">
#       <button id="v2v-mic-btn" class="primary"
#         onmousedown="startV2VRec()" onmouseup="stopV2VRec()"
#         ontouchstart="startV2VRec()" ontouchend="stopV2VRec()">🎤</button>
#       <span id="v2v-mic-status">Hold to record</span>
#     </div>
#     <label>Or upload audio file</label>
#     <input type="file" id="v2v-file" accept="audio/*" style="margin-bottom:12px">
#     <button class="primary" onclick="testVoiceToVoice()">Send File</button>
#     <audio id="v2v-audio-out" controls style="display:none;margin-top:10px"></audio>
#     <div style="margin-top:12px"><div class="log" id="v2v-log">—</div></div>
#   </div>
# </div>

# <!-- TEXT -->
# <div id="tab-text" class="section">
#   <div class="card">
#     <h2>Text → answer</h2>
#     <label>Question</label>
#     <textarea id="text-q" placeholder="e.g. How do I upload a bank statement?"></textarea>
#     <label>Language</label>
#     <select id="text-lang">
#       <option value="en">English</option>
#       <option value="hi">Hindi</option>
#       <option value="gu">Gujarati</option>
#     </select>
#     <button class="primary" onclick="askText()">Send</button>
#     <div style="margin-top:12px"><div class="log" id="text-log">—</div></div>
#   </div>
# </div>

# <!-- TEXT TO VOICE -->
# <div id="tab-ask_voice" class="section">
#   <div class="card">
#     <h2>Text → voice answer</h2>
#     <label>Question</label>
#     <textarea id="voice-q" placeholder="e.g. How do I upload a bank statement?"></textarea>
#     <label>Language</label>
#     <select id="voice-lang">
#       <option value="en">English</option>
#       <option value="hi">Hindi</option>
#       <option value="gu">Gujarati</option>
#     </select>
#     <button class="primary" onclick="askVoice()">Speak</button>
#     <audio id="ask-voice-out" controls style="display:none;margin-top:10px"></audio>
#     <div style="margin-top:12px"><div class="log" id="voice-test-log">—</div></div>
#   </div>
# </div>

# <!-- RAG -->
# <div id="tab-rag" class="section">
#   <div class="card">
#     <h2>RAG retriever</h2>
#     <label>Query (English)</label>
#     <input type="text" id="rag-q" placeholder="e.g. bank statement failed status">
#     <label>Top-K</label>
#     <select id="rag-k"><option>3</option><option>5</option><option>2</option><option>1</option></select>
#     <button class="primary" onclick="testRag()">Retrieve</button>
#     <div style="margin-top:12px" id="rag-results"></div>
#   </div>
# </div>

# <!-- STT -->
# <div id="tab-stt" class="section">
#   <div class="card">
#     <h2>STT only — Deepgram nova-3</h2>
#     <div style="display:flex;gap:10px;align-items:center;margin-bottom:15px">
#       <button id="stt-mic-btn" class="primary" onclick="toggleSTTRec()">🎤 Record from Mic</button>
#       <span id="stt-mic-status" style="font-size:0.85rem;color:#666">Ready</span>
#     </div>
#     <hr style="border:0;border-top:1px solid #eee;margin:15px 0">
#     <label>Or upload audio file (.webm / .mp3 / .wav)</label>
#     <input type="file" id="stt-file" accept="audio/*" style="margin-bottom:12px">
#     <button class="primary" onclick="testStt()">Transcribe File</button>
#     <div style="margin-top:12px"><div class="log" id="stt-log">—</div></div>
#   </div>
# </div>

# <script>
# // ── Tabs ──────────────────────────────────────────────────────
# const TAB_NAMES = ['voice','v2v','text','ask_voice','rag','stt'];
# function switchTab(name) {
#   document.querySelectorAll('.tab').forEach((t,i) => t.classList.toggle('active', TAB_NAMES[i]===name));
#   document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
#   document.getElementById('tab-'+name).classList.add('active');
# }

# // ── WebSocket voice ───────────────────────────────────────────
# let ws=null, mediaRecorder=null;
# let audioQueue=[], sourceBuffer=null, mediaSource=null;

# function getWs() {
#   if (ws && ws.readyState===WebSocket.OPEN) return ws;
#   const proto = location.protocol==='https:' ? 'wss' : 'ws';
#   ws = new WebSocket(proto+'://'+location.host+'/ws/voice');
#   ws.onmessage = handleWsMsg;
#   ws.onerror   = () => voiceLog('WebSocket error — is the server running?');
#   return ws;
# }

# function handleWsMsg(e) {
#   const msg = JSON.parse(e.data);
#   if (msg.type==='status') {
#     voiceLog('⏳ '+msg.message);
#     document.getElementById('mic-status').textContent = msg.message;
#   } else if (msg.type==='transcript') {
#     const langBadge = `<span class="badge badge-${msg.language}">${msg.language.toUpperCase()}</span>`;
#     voiceLog('');
#     voiceLog('USER  '+msg.user);
#     voiceLog('LANG  '+msg.language+' → '+msg.english_query);
#     voiceLog('KB    '+msg.chunks_used+' chunks');
#   } else if (msg.type==='audio_start') {
#     document.getElementById('mic-status').textContent = 'Speaking...';
#   } else if (msg.type==='audio_chunk') {
#     const audio = document.getElementById('audio-out');
#     // The backend single-shot legacy mode sends full WAV audio in one chunk
#     audio.src = "data:audio/wav;base64," + msg.data;
#     audio.style.display = 'block';
#     audio.play();
#   } else if (msg.type==='audio_end') {
#     document.getElementById('mic-status').textContent = 'Hold to record';
#   } else if (msg.type==='error') {
#     voiceLog('ERROR '+msg.message);
#     document.getElementById('mic-status').textContent = 'Error — see log';
#   }
# }

# async function startRec() {
#   const w = getWs();
#   const go = async () => {
#     const stream = await navigator.mediaDevices.getUserMedia({audio:true});
#     mediaRecorder = new MediaRecorder(stream, {mimeType:'audio/webm'});
#     const recordedChunks = [];
#     mediaRecorder.ondataavailable = async (e) => {
#       if (e.data.size>0) recordedChunks.push(e.data);
#     };
#     mediaRecorder.onstop = async () => {
#       if (ws && ws.readyState===WebSocket.OPEN) {
#         const blob = new Blob(recordedChunks, {type:'audio/webm'});
#         const buf = await blob.arrayBuffer();
#         const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
#         // Send one complete WebM file per turn to avoid corrupt chunk joins.
#         ws.send(JSON.stringify({audio:b64, mime:(mediaRecorder.mimeType || 'audio/webm')}));
#       }
#       stream.getTracks().forEach(t=>t.stop());
#     };
#     mediaRecorder.start();
#     document.getElementById('mic-btn').textContent='⏹';
#     document.getElementById('mic-btn').classList.replace('primary','danger');
#     document.getElementById('mic-status').textContent='Recording...';
#   };
#   if (w.readyState===WebSocket.CONNECTING) w.addEventListener('open', go);
#   else go();
# }

# function stopRec() {
#   if (mediaRecorder && mediaRecorder.state==='recording') {
#     mediaRecorder.stop();
#     document.getElementById('mic-btn').textContent='🎤';
#     document.getElementById('mic-btn').classList.replace('danger','primary');
#     document.getElementById('mic-status').textContent='Processing...';
#   }
# }

# function voiceLog(msg) {
#   const el = document.getElementById('voice-log');
#   if (el.textContent==='Waiting...') el.textContent='';
#   el.textContent += (msg||'') + '\\n';
#   el.scrollTop = el.scrollHeight;
# }

# // ── V2V recorder ─────────────────────────────────────────────
# let v2vRecorder=null, v2vChunks=[];

# async function startV2VRec() {
#   const stream = await navigator.mediaDevices.getUserMedia({audio:true});
#   v2vRecorder = new MediaRecorder(stream, {mimeType:'audio/webm'});
#   v2vChunks=[];
#   v2vRecorder.ondataavailable = e => { if(e.data.size>0) v2vChunks.push(e.data); };
#   v2vRecorder.onstop = async () => {
#     const blob = new Blob(v2vChunks, {type:'audio/webm'});
#     document.getElementById('v2v-log').textContent='Processing...';
#     const form = new FormData();
#     form.append('file', blob, 'recorded.webm');
#     await submitV2V(form);
#     stream.getTracks().forEach(t=>t.stop());
#   };
#   v2vRecorder.start();
#   document.getElementById('v2v-mic-btn').textContent='⏹';
#   document.getElementById('v2v-mic-btn').classList.replace('primary','danger');
#   document.getElementById('v2v-mic-status').textContent='Recording...';
# }

# function stopV2VRec() {
#   if (v2vRecorder && v2vRecorder.state==='recording') {
#     v2vRecorder.stop();
#     document.getElementById('v2v-mic-btn').textContent='🎤';
#     document.getElementById('v2v-mic-btn').classList.replace('danger','primary');
#     document.getElementById('v2v-mic-status').textContent='Processing...';
#   }
# }

# async function testVoiceToVoice() {
#   const file = document.getElementById('v2v-file').files[0];
#   if (!file) return;
#   document.getElementById('v2v-log').textContent='Processing...';
#   const form = new FormData();
#   form.append('file', file);
#   await submitV2V(form);
# }

# async function submitV2V(form) {
#   try {
#     const res = await fetch('/voice_to_voice', {method:'POST', body:form});
#     if (!res.ok) throw new Error(await res.text());
#     const transcript = decodeURIComponent(res.headers.get('X-Transcript')||'');
#     const lang       = res.headers.get('X-Language')||'';
#     const blob       = await res.blob();
#     const audio      = document.getElementById('v2v-audio-out');
#     audio.src = URL.createObjectURL(blob);
#     audio.style.display='block';
#     audio.play();
#     document.getElementById('v2v-log').textContent =
#       'TRANSCRIPT: '+transcript+'\\nLANGUAGE:   '+lang+'\\nPlaying...';
#   } catch(e) {
#     document.getElementById('v2v-log').textContent='Error: '+e.message;
#   }
# }

# // ── Text /ask ─────────────────────────────────────────────────
# async function askText() {
#   const q    = document.getElementById('text-q').value.trim();
#   const lang = document.getElementById('text-lang').value;
#   if (!q) return;
#   document.getElementById('text-log').textContent='Calling /ask...';
#   try {
#     const res  = await fetch('/ask', {method:'POST', headers:{'Content-Type':'application/json'},
#       body:JSON.stringify({question:q, language:lang})});
#     const data = await res.json();
#     document.getElementById('text-log').textContent =
#       'ENGLISH QUERY: '+data.english_query+'\\n\\n'+
#       'CHUNKS: '+data.retrieved_chunks.length+'\\n'+
#       data.retrieved_chunks.map((c,i)=>`[${i+1}] ${c.slice(0,100)}...`).join('\\n')+
#       '\\n\\nANSWER:\\n'+data.answer;
#   } catch(e) { document.getElementById('text-log').textContent='Error: '+e.message; }
# }

# // ── Text to voice ─────────────────────────────────────────────
# async function askVoice() {
#   const q    = document.getElementById('voice-q').value.trim();
#   const lang = document.getElementById('voice-lang').value;
#   if (!q) return;
#   document.getElementById('voice-test-log').textContent='Generating...';
#   try {
#     const res = await fetch('/ask_voice', {method:'POST', headers:{'Content-Type':'application/json'},
#       body:JSON.stringify({question:q, language:lang})});
#     if (!res.ok) throw new Error(await res.text());
#     const blob  = await res.blob();
#     const audio = document.getElementById('ask-voice-out');
#     audio.src = URL.createObjectURL(blob);
#     audio.style.display='block';
#     audio.play();
#     document.getElementById('voice-test-log').textContent='Playing...';
#   } catch(e) { document.getElementById('voice-test-log').textContent='Error: '+e.message; }
# }

# // ── RAG ───────────────────────────────────────────────────────
# async function testRag() {
#   const q = document.getElementById('rag-q').value.trim();
#   const k = document.getElementById('rag-k').value;
#   if (!q) return;
#   document.getElementById('rag-results').innerHTML='Retrieving...';
#   try {
#     const res  = await fetch('/retrieve?q='+encodeURIComponent(q)+'&k='+k);
#     const data = await res.json();
#     document.getElementById('rag-results').innerHTML =
#       data.chunks.map((c,i)=>`<div class="chunk"><strong>#${i+1}</strong><br>${c}</div>`).join('') || '<em>No results</em>';
#   } catch(e) { document.getElementById('rag-results').innerHTML='Error: '+e.message; }
# }

# // ── STT ───────────────────────────────────────────────────────
# let sttRecorder = null, sttChunks = [];
# async function toggleSTTRec() {
#   const btn = document.getElementById('stt-mic-btn');
#   const status = document.getElementById('stt-mic-status');
  
#   if (sttRecorder && sttRecorder.state === 'recording') {
#     sttRecorder.stop();
#     btn.textContent = '🎤 Record from Mic';
#     btn.classList.replace('danger', 'primary');
#     status.textContent = 'Transcribing...';
#   } else {
#     try {
#       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
#       sttRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
#       sttChunks = [];
#       sttRecorder.ondataavailable = e => { if (e.data.size > 0) sttChunks.push(e.data); };
#       sttRecorder.onstop = async () => {
#         const blob = new Blob(sttChunks, { type: 'audio/webm' });
#         const form = new FormData();
#         form.append('file', blob, 'recorded.webm');
#         document.getElementById('stt-log').textContent = 'Transcribing recorded audio...';
#         try {
#           const res = await fetch('/transcribe', { method: 'POST', body: form });
#           const data = await res.json();
#           document.getElementById('stt-log').textContent =
#             'TRANSCRIPT: ' + data.transcript + '\\nLANGUAGE:   ' + data.detected_language;
#           status.textContent = 'Ready';
#         } catch(e) {
#           document.getElementById('stt-log').textContent = 'Error: ' + e.message;
#           status.textContent = 'Error';
#         }
#         stream.getTracks().forEach(t => t.stop());
#       };
#       sttRecorder.start();
#       btn.textContent = '⏹ Stop Recording';
#       btn.classList.replace('primary', 'danger');
#       status.textContent = 'Recording...';
#     } catch(err) {
#       document.getElementById('stt-log').textContent = 'Error accessing microphone: ' + err.message;
#     }
#   }
# }

# async function testStt() {
#   const file = document.getElementById('stt-file').files[0];
#   if (!file) return;
#   document.getElementById('stt-log').textContent='Transcribing...';
#   const form = new FormData();
#   form.append('file', file);
#   try {
#     const res  = await fetch('/transcribe', {method:'POST', body:form});
#     const data = await res.json();
#     document.getElementById('stt-log').textContent =
#       'TRANSCRIPT: '+data.transcript+'\\nLANGUAGE:   '+data.detected_language;
#   } catch(e) { document.getElementById('stt-log').textContent='Error: '+e.message; }
# }
# </script>
# </body>
# </html>
# """















# """
# main.py — Suvit Voice Agent  (full-duplex real-time phone-call mode)
# ═══════════════════════════════════════════════════════════════════════
# Architecture:
#   ┌─ Browser ─────────────────────────────────────────────────────────┐
#   │  AudioWorklet (mic) ──raw Int16 binary──► WebSocket               │
#   │  WebSocket ◄──raw Int16 binary──────────── TTS audio              │
#   │  AudioContext scheduler → gapless, interruptible playback         │
#   └───────────────────────────────────────────────────────────────────┘
#   ┌─ Server ──────────────────────────────────────────────────────────┐
#   │  WS receive_bytes() ──► Deepgram STT ──► Translate ──► RAG        │
#   │  Gemini/OpenAI LLM ──► Sarvam TTS ──► binary audio frames        │
#   └───────────────────────────────────────────────────────────────────┘

# WebSocket protocol (mixed binary + JSON text):
#   CLIENT → SERVER:
#     binary frame              = raw Int16 LE PCM, 16 kHz, mono (mic audio)
#     JSON { type:"call_start", language:"en"|"hi"|"gu" }
#     JSON { type:"vad_end" }   = client VAD detected end-of-speech
#     JSON { type:"interrupt" } = user spoke while agent was speaking
#     JSON { type:"call_end" }  = user clicked stop

#   SERVER → CLIENT:
#     JSON { type:"call_accepted" }
#     JSON { type:"status",     message }
#     JSON { type:"transcript", user, language, english }
#     JSON { type:"tts_start" }
#     binary frame              = raw Int16 LE PCM, 22050 Hz, mono (TTS audio)
#     JSON { type:"tts_end" }
#     JSON { type:"clear_queue" }   = interrupt TTS immediately
#     JSON { type:"call_ended", message }
#     JSON { type:"error",      message }
# """

# import os, json, asyncio, struct
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse, JSONResponse
# from dotenv import load_dotenv

# load_dotenv()

# from agents.state import ConversationTurn
# from services.deepgram_stt import transcribe
# from services.sarvam_tts import synthesize_pcm_stream, synthesize
# from services.gemini_translate import (
#     translate_to_english, detect_language,
#     generate_answer, generate_answer_stream, GREETINGS,
# )
# from kb.retriever import retrieve

# app = FastAPI(title="Suvit Voice Agent", version="4.0.0")
# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# # ─── Health ───────────────────────────────────────────────────────────────────

# @app.get("/health")
# async def health():
#     checks = {}
#     try:
#         from kb.retriever import get_vectorstore; get_vectorstore()
#         checks["faiss_index"] = "ok"
#     except Exception as e:
#         checks["faiss_index"] = f"error: {e}"
#     checks["deepgram"] = "ok" if os.environ.get("DEEPGRAM_API_KEY") else "MISSING"
#     checks["openai"]   = "ok" if os.environ.get("OPENAI_API_KEY")   else "MISSING"
#     checks["gemini"]   = "ok" if os.environ.get("GOOGLE_API_KEY")   else "MISSING"
#     checks["sarvam"]   = "ok" if os.environ.get("SARVAMAI_API_KEY") else "missing — edge-tts fallback active"
#     ok = all("MISSING" not in v and "error" not in v for v in checks.values())
#     return JSONResponse({"status": "ok" if ok else "degraded", "checks": checks})


# @app.post("/transcribe")
# async def transcribe_file(file: UploadFile = File(...)):
#     audio = await file.read()
#     t, lang = await transcribe(audio)
#     return {"transcript": t, "detected_language": lang}


# @app.get("/retrieve")
# async def retrieve_api(q: str, k: int = 3):
#     return {"query": q, "chunks": retrieve(q, k=k)}


# # ─── WebSocket — full-duplex call ─────────────────────────────────────────────

# @app.websocket("/ws/call")
# async def call_ws(ws: WebSocket):
#     await ws.accept()

#     # ── per-session state ──────────────────────────────────────────────────
#     history:      list[ConversationTurn] = []
#     current_lang: str   = "en"
#     call_active:  bool  = False
#     agent_speaking: bool = False

#     # accumulate mic PCM chunks between vad_end events
#     mic_buffer: list[bytes] = []

#     # running TTS task (so we can cancel it on interrupt)
#     tts_task: asyncio.Task | None = None

#     # ── helpers ────────────────────────────────────────────────────────────

#     async def send_json(obj: dict):
#         try:
#             await ws.send_json(obj)
#         except Exception:
#             pass

#     async def send_bytes(data: bytes):
#         try:
#             await ws.send_bytes(data)
#         except Exception:
#             pass

#     async def abort_tts():
#         nonlocal tts_task, agent_speaking
#         if tts_task and not tts_task.done():
#             tts_task.cancel()
#             try:
#                 await tts_task
#             except asyncio.CancelledError:
#                 pass
#         agent_speaking = False
#         await send_json({"type": "clear_queue"})

#     async def _stream_tts(text: str, lang: str):
#         """
#         Synthesize text → stream raw Int16 PCM binary frames to client.
#         Sentence-level streaming: first audio arrives in ~400ms.
#         Each frame is a raw binary blob the client schedules via AudioContext.
#         """
#         nonlocal agent_speaking
#         agent_speaking = True
#         await send_json({"type": "tts_start"})
#         try:
#             print(f"\n[WS] Starting TTS stream for: '{text[:50]}...'")
#             async for pcm_chunk in synthesize_pcm_stream(text, lang):
#                 if tts_task and tts_task.cancelled():
#                     break
#                 await send_bytes(pcm_chunk)
#                 print("*", end="", flush=True)
#                 await asyncio.sleep(0)   # yield to event loop so interrupts land
#             print("\n[WS] TTS stream finished.")
#             await send_json({"type": "tts_end"})
#         except asyncio.CancelledError:
#             await send_json({"type": "tts_end"})
#             raise
#         finally:
#             agent_speaking = False

#     async def speak(text: str, lang: str):
#         nonlocal tts_task
#         tts_task = asyncio.create_task(_stream_tts(text, lang))
#         try:
#             await tts_task
#         except asyncio.CancelledError:
#             pass

#     async def run_pipeline(audio_bytes: bytes):
#         """Full STT → translate → RAG → LLM → TTS pipeline for one user turn."""
#         # 1. STT
#         await send_json({"type": "status", "message": "Transcribing…"})
#         try:
#             transcript, lang_stt = await transcribe(audio_bytes)
#         except Exception as e:
#             await send_json({"type": "error", "message": f"STT error: {e}"})
#             return
#         transcript = transcript.strip()
#         if not transcript:
#             # If nothing was transcribed, just silently ignore it (likely background noise).
#             await send_json({"type": "status", "message": "Listening…"})
#             return

#         # 2. Language refinement
#         try:
#             lang = await detect_language(transcript)
#         except Exception:
#             lang = lang_stt
#         nonlocal current_lang
#         current_lang = lang

#         # 3. Translate → English
#         await send_json({"type": "status", "message": "Thinking…"})
#         english_q = await translate_to_english(transcript, lang)

#         # 4. RAG
#         chunks = retrieve(english_q)
#         await send_json({"type": "transcript", "user": transcript,
#                          "language": lang, "english": english_q, "chunks": len(chunks)})

#         # 5. Generate answer
#         answer = await generate_answer(
#             query_english=english_q,
#             context_chunks=chunks,
#             response_language=lang,
#             history=history,
#         )

#         # 6. Update history
#         history.append(ConversationTurn(role="user",      text=transcript, language=lang))
#         history.append(ConversationTurn(role="assistant", text=answer,     language=lang))
#         del history[:-10]   # keep last 5 exchanges

#         # 7. Speak
#         await send_json({"type": "agent_text", "text": answer, "language": lang})
#         await speak(answer, lang)

#     # ── message loop ───────────────────────────────────────────────────────
#     try:
#         while True:
#             msg = await ws.receive()

#             # ── binary frame = raw PCM from AudioWorklet ─────────────────
#             if "bytes" in msg and msg["bytes"]:
#                 if call_active:
#                     mic_buffer.append(msg["bytes"])
#                     # Print a tiny dot to indicate PCM receiving without spamming newlines
#                     print(".", end="", flush=True)
#                 continue

#             # ── JSON control message ─────────────────────────────────────
#             if "text" not in msg or not msg["text"]:
#                 continue
#             data     = json.loads(msg["text"])
#             msg_type = data.get("type")

#             if msg_type == "call_start":
#                 print("\n[WS] call_start received")
#                 current_lang = data.get("language", "en")
#                 call_active  = True
#                 history      = []
#                 mic_buffer   = []
#                 await send_json({"type": "call_accepted"})
#                 # Greet immediately — no LLM needed
#                 greeting = GREETINGS.get(current_lang, GREETINGS["en"])
#                 history.append(ConversationTurn(role="assistant", text=greeting, language=current_lang))
#                 await send_json({"type": "agent_text", "text": greeting, "language": current_lang})
#                 await speak(greeting, current_lang)
#                 await send_json({"type": "status", "message": "Listening…"})

#             elif msg_type == "vad_end":
#                 print(f"\n[WS] vad_end received. Buffered {len(mic_buffer)} PCM chunks.")
#                 # Client VAD declared end-of-speech
#                 if not mic_buffer:
#                     continue
#                 audio_bytes = b"".join(mic_buffer)
#                 mic_buffer  = []
#                 # Run pipeline concurrently so we can still receive interrupts
#                 asyncio.create_task(run_pipeline(audio_bytes))

#             elif msg_type == "interrupt":
#                 print("\n[WS] INTERRUPT received from client! Clearing buffer and aborting TTS.")
#                 mic_buffer = []
#                 await abort_tts()
#                 await send_json({"type": "status", "message": "Listening…"})

#             elif msg_type == "call_end":
#                 call_active = False
#                 await abort_tts()
#                 bye = {"en": "Goodbye! Have a great day.",
#                        "hi": "Theek hai! Dhanyavaad. Aapka din accha rahe.",
#                        "gu": "Saru che! Aabhaar. Tamaro divas saras rahe."}.get(current_lang, "Goodbye!")
#                 await speak(bye, current_lang)
#                 await send_json({"type": "call_ended", "message": bye})
#                 break

#     except WebSocketDisconnect:
#         pass
#     except Exception as e:
#         import traceback; traceback.print_exc()
#         try:
#             await send_json({"type": "error", "message": str(e)})
#         except Exception:
#             pass


# # ─── /ws/voice — legacy WebSocket for React frontend ─────────────────────────

# @app.websocket("/ws/voice")
# async def voice_ws_legacy(ws: WebSocket):
#     """
#     Legacy WebSocket endpoint for the React frontend.

#     The React frontend (useVoiceAgent.ts) sends raw binary PCM frames
#     continuously while recording. When the user stops, it closes the
#     connection. We buffer all PCM, then on disconnect or silence we
#     process the full pipeline.

#     This endpoint bridges the old /ws/voice protocol to the new pipeline.
#     """
#     await ws.accept()

#     import base64

#     history:   list[ConversationTurn] = []
#     lang:      str = "en"
#     mic_buffer: list[bytes] = []

#     # VAD state for detecting end-of-speech in streaming PCM
#     silence_frames = 0
#     speech_detected = False
#     SILENCE_LIMIT = 30  # ~30 chunks of silence = ~2s depending on chunk size

#     async def send(obj: dict):
#         try: await ws.send_json(obj)
#         except Exception: pass

#     async def send_bin(data: bytes):
#         try: await ws.send_bytes(data)
#         except Exception: pass

#     async def run_turn(audio_bytes: bytes):
#         nonlocal lang

#         # 1. STT
#         await send({"type": "state", "state": "thinking"})
#         try:
#             transcript, lang_stt = await transcribe(audio_bytes)
#         except Exception as e:
#             await send({"type": "error", "message": f"STT error: {e}"})
#             await send({"type": "state", "state": "listening"})
#             return
#         transcript = transcript.strip()
#         if not transcript:
#             await send({"type": "error", "message": "Didn't catch that — please try again."})
#             await send({"type": "state", "state": "listening"})
#             return

#         # 2. Language
#         try:
#             lang = await detect_language(transcript)
#         except Exception:
#             lang = lang_stt

#         # 3. Translate
#         english_q = await translate_to_english(transcript, lang)

#         # 4. RAG
#         chunks = retrieve(english_q)

#         await send({
#             "type": "transcript",
#             "user": transcript,
#             "language": lang,
#             "english_query": english_q,
#             "chunks_used": len(chunks),
#         })

#         # 5. Generate
#         answer = await generate_answer(
#             query_english=english_q,
#             context_chunks=chunks,
#             response_language=lang,
#             history=history,
#         )

#         # 6. History
#         history.append(ConversationTurn(role="user", text=transcript, language=lang))
#         history.append(ConversationTurn(role="assistant", text=answer, language=lang))
#         del history[:-10]

#         await send({"type": "assistant_end", "text": answer, "language": lang})

#         # 7. TTS → send binary PCM
#         await send({"type": "state", "state": "speaking"})
#         try:
#             async for pcm_chunk in synthesize_pcm_stream(answer, lang):
#                 await send_bin(pcm_chunk)
#         except Exception as e:
#             print(f"[ws/voice] TTS error: {e}")

#         await send({"type": "state", "state": "listening"})

#     try:
#         while True:
#             msg = await ws.receive()

#             # Binary = raw PCM from AudioWorklet
#             if "bytes" in msg and msg["bytes"]:
#                 chunk = msg["bytes"]
#                 mic_buffer.append(chunk)

#                 # Simple energy-based VAD on server side
#                 import struct
#                 if len(chunk) >= 2:
#                     samples = struct.unpack(f'<{len(chunk)//2}h', chunk)
#                     rms = (sum(s*s for s in samples) / len(samples)) ** 0.5
#                     if rms > 500:
#                         speech_detected = True
#                         silence_frames = 0
#                     elif speech_detected:
#                         silence_frames += 1
#                         if silence_frames >= SILENCE_LIMIT:
#                             # End of speech detected — process turn
#                             audio_bytes = b"".join(mic_buffer)
#                             mic_buffer = []
#                             speech_detected = False
#                             silence_frames = 0
#                             await run_turn(audio_bytes)
#                 continue

#             # JSON text messages (if any)
#             if "text" in msg and msg["text"]:
#                 data = json.loads(msg["text"])
#                 msg_type = data.get("type")
#                 if msg_type == "interrupt":
#                     mic_buffer = []
#                     await send({"type": "clear_queue"})
#                     await send({"type": "state", "state": "listening"})

#     except WebSocketDisconnect:
#         pass
#     except Exception as e:
#         import traceback; traceback.print_exc()


# # ─── UI ───────────────────────────────────────────────────────────────────────

# @app.get("/test", response_class=HTMLResponse)
# async def test_page():
#     return HTMLResponse(CALL_UI)

# @app.get("/", response_class=HTMLResponse)
# async def index():
#     return HTMLResponse(CALL_UI)


# # ══════════════════════════════════════════════════════════════════════════════
# #  CALL_UI  — single-file full-duplex voice call page
# #  Architecture:
# #   • AudioWorklet (inline Blob)  → raw Int16 PCM → WebSocket binary frames
# #   • WebSocket binary frames     → AudioContext scheduler (gapless playback)
# #   • Energy VAD on worklet thread → vad_end JSON message
# #   • clear_queue → AudioContext.close() + new AudioContext (instant silence)
# # ══════════════════════════════════════════════════════════════════════════════

# CALL_UI = r"""<!DOCTYPE html>
# <html lang="en">
# <head>
# <meta charset="UTF-8">
# <meta name="viewport" content="width=device-width,initial-scale=1">
# <title>Suvit — Voice Support</title>
# <style>
# *{box-sizing:border-box;margin:0;padding:0}
# :root{
#   --bg:#0f0f0f;--surface:#1a1a1a;--surface2:#242424;
#   --border:#2e2e2e;--text:#f0f0f0;--muted:#888;
#   --accent:#3b82f6;--danger:#ef4444;--success:#22c55e;
#   --user:#1e3a5f;--agent:#1e2d1e;
# }
# html,body{height:100%;font-family:system-ui,sans-serif;background:var(--bg);color:var(--text)}
# body{display:flex;align-items:center;justify-content:center;padding:1rem}

# /* ── Card ── */
# .card{
#   width:100%;max-width:440px;
#   background:var(--surface);border:1px solid var(--border);border-radius:24px;
#   display:flex;flex-direction:column;overflow:hidden;
#   box-shadow:0 8px 40px rgba(0,0,0,.6);
# }

# /* ── Header ── */
# .hdr{
#   padding:1.1rem 1.4rem;border-bottom:1px solid var(--border);
#   display:flex;align-items:center;gap:12px;
# }
# .avatar{
#   width:42px;height:42px;border-radius:50%;background:var(--accent);
#   display:flex;align-items:center;justify-content:center;font-size:1.1rem;
#   font-weight:600;flex-shrink:0;letter-spacing:-.5px;
# }
# .hdr-info{flex:1}
# .hdr-name{font-size:.95rem;font-weight:500}
# .hdr-status{display:flex;align-items:center;gap:6px;margin-top:3px}
# .dot{width:7px;height:7px;border-radius:50%;background:var(--border);transition:background .3s}
# .dot.idle{}
# .dot.listen{background:var(--success);animation:blink 1.8s ease-in-out infinite}
# .dot.think{background:#f59e0b;animation:blink 1s ease-in-out infinite}
# .dot.speak{background:var(--accent);animation:blink .8s ease-in-out infinite}
# @keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
# .hdr-status span{font-size:.75rem;color:var(--muted)}

# /* ── Lang selector ── */
# .lang-row{display:flex;gap:6px;padding:.7rem 1.4rem;border-bottom:1px solid var(--border)}
# .lb{
#   padding:3px 13px;border-radius:20px;border:1px solid var(--border);
#   background:transparent;color:var(--muted);font-size:.78rem;cursor:pointer;transition:all .15s;
# }
# .lb.on{background:var(--accent);color:#fff;border-color:var(--accent)}

# /* ── Log ── */
# .log{
#   flex:1;min-height:280px;max-height:360px;overflow-y:auto;
#   padding:1rem 1.2rem;display:flex;flex-direction:column;gap:.55rem;
# }
# .log::-webkit-scrollbar{width:4px}
# .log::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}

# .bbl{
#   max-width:82%;padding:.5rem .9rem;border-radius:16px;
#   font-size:.86rem;line-height:1.6;animation:rise .18s ease;
# }
# @keyframes rise{from{opacity:0;transform:translateY(5px)}}
# .bbl.user{align-self:flex-end;background:var(--user);border-bottom-right-radius:4px}
# .bbl.agent{align-self:flex-start;background:var(--agent);border-bottom-left-radius:4px}
# .bbl.system{align-self:center;font-size:.72rem;color:var(--muted);background:none;padding:2px 0}
# .ltag{
#   font-size:.65rem;font-weight:600;padding:1px 5px;border-radius:8px;
#   margin-right:4px;vertical-align:middle;
# }
# .en{background:#1e3a5f;color:#7cb9f8}
# .hi{background:#1e2d1e;color:#86efac}
# .gu{background:#2d2010;color:#fcd34d}

# .empty{
#   flex:1;display:flex;flex-direction:column;align-items:center;
#   justify-content:center;gap:.5rem;color:var(--muted);font-size:.85rem;text-align:center;
# }

# /* ── Viz ── */
# .viz{
#   height:56px;padding:0 1.2rem;border-top:1px solid var(--border);
#   display:flex;align-items:center;
# }
# canvas{width:100%;height:40px}

# /* ── Controls ── */
# .ctrls{
#   padding:.9rem 1.4rem 1.1rem;border-top:1px solid var(--border);
#   display:flex;align-items:center;justify-content:space-between;
# }
# .vol{display:flex;align-items:center;gap:6px;font-size:.8rem;color:var(--muted)}
# input[type=range]{width:72px;accent-color:var(--accent)}
# .call-btn{
#   width:64px;height:64px;border-radius:50%;border:none;cursor:pointer;
#   font-size:1.5rem;display:flex;align-items:center;justify-content:center;
#   transition:all .2s;
#   background:var(--accent);color:#fff;
#   box-shadow:0 0 0 0 rgba(59,130,246,.5);
# }
# .call-btn.ringing{animation:ring 1.5s ease-in-out infinite}
# @keyframes ring{0%,100%{box-shadow:0 0 0 0 rgba(59,130,246,.5)}70%{box-shadow:0 0 0 16px rgba(59,130,246,0)}}
# .call-btn.active{background:var(--danger);box-shadow:0 0 0 0 rgba(239,68,68,.5)}
# .call-btn.active.ringing{animation:ring-red 1.5s ease-in-out infinite}
# @keyframes ring-red{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.5)}70%{box-shadow:0 0 0 16px rgba(239,68,68,0)}}
# .side-info{width:90px;font-size:.72rem;color:var(--muted);text-align:right;line-height:1.6}
# </style>
# </head>
# <body>
# <div class="card">
#   <div class="hdr">
#     <div class="avatar">S</div>
#     <div class="hdr-info">
#       <div class="hdr-name">Suvit Support</div>
#       <div class="hdr-status"><div class="dot idle" id="dot"></div><span id="stxt">Ready</span></div>
#     </div>
#     <a href="/health" target="_blank" style="font-size:.7rem;color:var(--muted);text-decoration:none;opacity:.6">⚙</a>
#   </div>

#   <div class="lang-row">
#     <button class="lb on" data-l="en" onclick="setLang('en')">English</button>
#     <button class="lb"    data-l="hi" onclick="setLang('hi')">Hindi</button>
#     <button class="lb"    data-l="gu" onclick="setLang('gu')">Gujarati</button>
#   </div>

#   <div class="log" id="log">
#     <div class="empty" id="empty">
#       <div style="font-size:2rem">📞</div>
#       <div>Press the call button to start</div>
#       <div style="font-size:.72rem;margin-top:.2rem">Supports English · Hindi · Gujarati</div>
#     </div>
#   </div>

#   <div class="viz"><canvas id="cv" width="400" height="40"></canvas></div>

#   <div class="ctrls">
#     <div class="vol">🔈<input type="range" id="vol" min="0" max="2" step=".05" value="1" oninput="gainNode&&(gainNode.gain.value=+this.value)">🔊</div>
#     <button class="call-btn" id="cbtn" onclick="toggleCall()" title="Start / End call">📞</button>
#     <div class="side-info" id="sinfo"></div>
#   </div>
# </div>

# <script>
# /* ═══════════════════════════════════════════════════════════════════════════
#    AudioWorklet processor code — injected via Blob URL so no external file needed.

#    Responsibilities:
#      1. Downsample Float32 mic audio (48/44.1 kHz) → Int16 @ 16 kHz
#      2. Energy-based VAD:
#         - speech_frames counter ↑ when RMS > SPEECH_THRESHOLD
#         - silence_frames counter ↑ when RMS < SILENCE_THRESHOLD
#         - After SILENCE_FRAMES consecutive silent frames → post "vad_end"
#      3. Post every PCM chunk as transferable ArrayBuffer to main thread
#    ═══════════════════════════════════════════════════════════════════════════ */
# const WORKLET_CODE = `
# class MicProcessor extends AudioWorkletProcessor {
#   constructor(opts){
#     super();
#     this._targetSR = opts.processorOptions.targetSR || 16000;
#     this._ratio    = sampleRate / this._targetSR;    // e.g. 48000/16000 = 3
#     this._buf      = [];
#     // VAD config
#     this._SPEECH_THRESH  = 0.02;
#     this._SILENCE_THRESH = 0.01;
#     this._SPEECH_FRAMES  = 4;    // frames before we call it speech
#     this._SILENCE_FRAMES = 40;   // ~800 ms silence @ 128 samples/frame, 16kHz target
#     this._speechCount    = 0;
#     this._silenceCount   = 0;
#     this._inSpeech       = false;
#   }

#   process(inputs){
#     const ch = inputs[0][0];
#     if(!ch) return true;

#     // RMS energy
#     let rms = 0;
#     for(let i=0;i<ch.length;i++) rms += ch[i]*ch[i];
#     rms = Math.sqrt(rms/ch.length);

#     // VAD state machine
#     if(rms > this._SPEECH_THRESH){
#       this._speechCount++;
#       this._silenceCount = 0;
#       if(this._speechCount >= this._SPEECH_FRAMES && !this._inSpeech){
#         this._inSpeech = true;
#         this.port.postMessage({type:'vad_start'});
#       }
#     } else if(rms < this._SILENCE_THRESH && this._inSpeech){
#       this._silenceCount++;
#       this._speechCount = 0;
#       if(this._silenceCount >= this._SILENCE_FRAMES){
#         this._inSpeech   = false;
#         this._silenceCount = 0;
#         this.port.postMessage({type:'vad_end'});
#       }
#     } else {
#       this._speechCount = 0;
#     }

#     // Downsample: simple decimation (good enough for speech)
#     const step = this._ratio;
#     for(let i=0;i<ch.length;i+=step){
#       this._buf.push(ch[Math.round(i)]);
#     }

#     // Emit 4096-sample chunks
#     while(this._buf.length >= 4096){
#       const slice  = this._buf.splice(0, 4096);
#       const int16  = new Int16Array(4096);
#       for(let i=0;i<4096;i++) int16[i] = Math.max(-32768, Math.min(32767, slice[i]*32767));
#       this.port.postMessage({type:'pcm', buf: int16.buffer}, [int16.buffer]);
#     }
#     return true;
#   }
# }
# registerProcessor('mic-proc', MicProcessor);
# `;

# /* ═══════════════════════════════════════════════════════════════════════════
#    Main thread state
#    ═══════════════════════════════════════════════════════════════════════════ */
# let ws          = null;
# let callActive  = false;
# let agentSpeaking = false;
# let currentLang = 'en';

# // AudioContext for mic capture (16 kHz)
# let micCtx      = null;
# let workletNode = null;
# let micStream   = null;
# let analyserNode= null;

# // AudioContext for TTS playback (22050 Hz — Sarvam output)
# let playCtx     = null;
# let gainNode    = null;
# const TTS_SR    = 22050;       // must match server output
# let nextPlayAt  = 0;           // gapless scheduling cursor

# // Waveform
# const cv  = document.getElementById('cv');
# const cx  = cv.getContext('2d');
# let rafId = null;

# /* ── Language ── */
# function setLang(l){
#   currentLang = l;
#   document.querySelectorAll('.lb').forEach(b=>b.classList.toggle('on', b.dataset.l===l));
# }

# /* ── Status ── */
# function setStatus(txt, mode='idle'){
#   document.getElementById('stxt').textContent = txt;
#   document.getElementById('dot').className = 'dot '+mode;
# }

# /* ── Conversation log ── */
# function log(role, text, lang){
#   const el = document.getElementById('log');
#   const em = document.getElementById('empty');
#   if(em) em.remove();
#   const d = document.createElement('div');
#   d.className = 'bbl '+role;
#   const tag = lang ? `<span class="ltag ${lang}">${lang.toUpperCase()}</span>` : '';
#   d.innerHTML = role==='user' ? tag+text : text+(lang?tag:'');
#   el.appendChild(d);
#   el.scrollTop = el.scrollHeight;
# }
# function sysLog(txt){
#   const el = document.getElementById('log');
#   const d  = document.createElement('div');
#   d.className = 'bbl system';
#   d.textContent = txt;
#   el.appendChild(d);
#   el.scrollTop = el.scrollHeight;
# }

# /* ══════════════════════════════════════════════════════════════════════════
#    AUDIO PLAYBACK — AudioContext gapless scheduler
#    Receives raw Int16 PCM binary frames from server.
#    Converts each frame to Float32, creates AudioBuffer, schedules it
#    back-to-back via nextPlayAt cursor.
#    ══════════════════════════════════════════════════════════════════════════ */
# function ensurePlayCtx(){
#   if(playCtx && playCtx.state !== 'closed') return;
#   playCtx  = new AudioContext({sampleRate: TTS_SR});
#   gainNode = playCtx.createGain();
#   gainNode.gain.value = +document.getElementById('vol').value;
#   gainNode.connect(playCtx.destination);
#   nextPlayAt = 0;
# }

# function scheduleAudioChunk(arrayBuffer){
#   if(!playCtx || playCtx.state === 'closed') return;
#   const int16   = new Int16Array(arrayBuffer);
#   const float32 = new Float32Array(int16.length);
#   for(let i=0;i<int16.length;i++) float32[i] = int16[i] / 32768;

#   const buf = playCtx.createBuffer(1, float32.length, TTS_SR);
#   buf.copyToChannel(float32, 0);

#   const src = playCtx.createBufferSource();
#   src.buffer = buf;
#   src.connect(gainNode);

#   const now  = playCtx.currentTime;
#   const when = Math.max(now, nextPlayAt);
#   src.start(when);
#   nextPlayAt = when + buf.duration;
# }

# function clearAudioQueue(){
#   /* Instant silence: close the AudioContext, rebuild it. */
#   if(playCtx && playCtx.state !== 'closed'){
#     playCtx.close().catch(()=>{});
#   }
#   playCtx    = null;
#   gainNode   = null;
#   nextPlayAt = 0;
#   agentSpeaking = false;
# }

# /* ══════════════════════════════════════════════════════════════════════════
#    WAVEFORM — reads from mic analyser
#    ══════════════════════════════════════════════════════════════════════════ */
# function startWave(){
#   const buf = new Uint8Array(analyserNode ? analyserNode.fftSize : 256);
#   function draw(){
#     rafId = requestAnimationFrame(draw);
#     if(analyserNode) analyserNode.getByteTimeDomainData(buf);
#     cx.clearRect(0,0,cv.width,cv.height);
#     cx.beginPath();
#     const sl = cv.width/buf.length;
#     let x=0;
#     for(let i=0;i<buf.length;i++){
#       const y = ((buf[i]/128)-1)*(cv.height/2)+cv.height/2;
#       i===0?cx.moveTo(x,y):cx.lineTo(x,y);
#       x+=sl;
#     }
#     cx.strokeStyle = agentSpeaking ? '#3b82f6' : '#22c55e';
#     cx.lineWidth   = 1.5;
#     cx.stroke();
#   }
#   draw();
# }
# function stopWave(){
#   if(rafId) cancelAnimationFrame(rafId);
#   cx.clearRect(0,0,cv.width,cv.height);
# }

# /* ══════════════════════════════════════════════════════════════════════════
#    WEBSOCKET
#    ══════════════════════════════════════════════════════════════════════════ */
# function connectWS(){
#   const proto = location.protocol==='https:'?'wss':'ws';
#   ws = new WebSocket(`${proto}://${location.host}/ws/call`);
#   ws.binaryType = 'arraybuffer';

#   ws.onopen = () => {
#     ws.send(JSON.stringify({type:'call_start', language:currentLang}));
#   };

#   ws.onmessage = e => {
#     // ── binary frame = TTS PCM audio ─────────────────────────────────
#     if(e.data instanceof ArrayBuffer){
#       if(!agentSpeaking) return;   // might arrive after clear_queue
#       ensurePlayCtx();
#       scheduleAudioChunk(e.data);
#       return;
#     }

#     // ── JSON control message ─────────────────────────────────────────
#     const msg = JSON.parse(e.data);

#     if(msg.type==='call_accepted'){
#       setStatus('Connected', 'listen');
#       return;
#     }
#     if(msg.type==='status'){
#       const modeMap = {
#         'Transcribing…':'think','Thinking…':'think',
#         'Listening…':'listen','Processing…':'think',
#       };
#       setStatus(msg.message, modeMap[msg.message]||'listen');
#       return;
#     }
#     if(msg.type==='transcript'){
#       log('user', msg.user, msg.language);
#       document.getElementById('sinfo').textContent =
#         `${msg.chunks} chunks\n${msg.english!==msg.user?'→ '+msg.english.slice(0,40)+'…':''}`;
#       return;
#     }
#     if(msg.type==='agent_text'){
#       log('agent', msg.text, msg.language);
#       return;
#     }
#     if(msg.type==='tts_start'){
#       agentSpeaking = true;
#       ensurePlayCtx();
#       setStatus('Speaking…', 'speak');
#       return;
#     }
#     if(msg.type==='tts_end'){
#       agentSpeaking = false;
#       if(callActive) setStatus('Listening…', 'listen');
#       return;
#     }
#     if(msg.type==='clear_queue'){
#       clearAudioQueue();
#       if(callActive) setStatus('Listening…', 'listen');
#       return;
#     }
#     if(msg.type==='call_ended'){
#       log('agent', msg.message, currentLang);
#       endCall(false);
#       return;
#     }
#     if(msg.type==='error'){
#       sysLog('⚠ '+msg.message);
#       setStatus('Listening…','listen');
#       return;
#     }
#   };

#   ws.onerror = () => sysLog('WebSocket error — is the server running?');
#   ws.onclose = () => { if(callActive) endCall(false); };
# }

# /* ══════════════════════════════════════════════════════════════════════════
#    MICROPHONE + AudioWorklet capture
#    ══════════════════════════════════════════════════════════════════════════ */
# async function startMic(){
#   micStream = await navigator.mediaDevices.getUserMedia({
#     audio:{echoCancellation:true, noiseSuppression:true, sampleRate:48000}
#   });

#   // 48kHz context for mic — worklet downsamples to 16kHz internally
#   micCtx = new AudioContext({sampleRate:48000});

#   // Inject worklet from Blob URL (no external file needed)
#   const blob    = new Blob([WORKLET_CODE], {type:'application/javascript'});
#   const blobURL = URL.createObjectURL(blob);
#   await micCtx.audioWorklet.addModule(blobURL);
#   URL.revokeObjectURL(blobURL);

#   const src = micCtx.createMediaStreamSource(micStream);

#   // Analyser for waveform visualisation
#   analyserNode = micCtx.createAnalyser();
#   analyserNode.fftSize = 256;
#   src.connect(analyserNode);

#   // AudioWorklet for PCM capture + VAD
#   workletNode = new AudioWorkletNode(micCtx, 'mic-proc', {
#     processorOptions: {targetSR: 16000}
#   });
#   src.connect(workletNode);

#   workletNode.port.onmessage = e => {
#     const {type, buf} = e.data;

#     if(type==='pcm' && ws && ws.readyState===WebSocket.OPEN && callActive){
#       ws.send(buf);   // raw binary frame — zero copies
#     }

#     // Interruption detection: if agent is speaking and we actually detect speech start (vad_start), then interrupt!
#     if(type==='vad_start' && ws && ws.readyState===WebSocket.OPEN && callActive){
#       if(agentSpeaking){
#         ws.send(JSON.stringify({type:'interrupt'}));
#         clearAudioQueue();
#         setStatus('Listening…','listen');
#       }
#     }

#     if(type==='vad_end' && ws && ws.readyState===WebSocket.OPEN && callActive && !agentSpeaking){
#       ws.send(JSON.stringify({type:'vad_end'}));
#       setStatus('Processing…','think');
#     }
#   };

#   startWave();
# }

# function stopMic(){
#   if(workletNode){ workletNode.disconnect(); workletNode=null; }
#   if(micCtx){ micCtx.close().catch(()=>{}); micCtx=null; }
#   if(micStream){ micStream.getTracks().forEach(t=>t.stop()); micStream=null; }
#   analyserNode=null;
#   stopWave();
# }

# /* ══════════════════════════════════════════════════════════════════════════
#    CALL CONTROL
#    ══════════════════════════════════════════════════════════════════════════ */
# async function toggleCall(){
#   if(!callActive) await startCall();
#   else            endCall(true);
# }

# async function startCall(){
#   callActive = true;
#   const btn = document.getElementById('cbtn');
#   btn.textContent = '📵';
#   btn.classList.add('active','ringing');
#   document.getElementById('log').innerHTML = '';

#   setStatus('Connecting…','idle');
#   connectWS();
#   await startMic();
# }

# function endCall(sendEnd){
#   callActive    = false;
#   agentSpeaking = false;

#   if(sendEnd && ws && ws.readyState===WebSocket.OPEN)
#     ws.send(JSON.stringify({type:'call_end'}));
#   else if(ws) ws.close();

#   stopMic();
#   clearAudioQueue();

#   const btn = document.getElementById('cbtn');
#   btn.textContent = '📞';
#   btn.classList.remove('active','ringing');
#   setStatus('Call ended','idle');
#   setTimeout(()=>setStatus('Ready','idle'), 2000);
# }
# </script>
# </body>
# </html>"""


























# """
# main.py — Suvit Voice Agent  (Real-Time Streaming Pipeline)
# ═══════════════════════════════════════════════════════════════════════
# Real-Time Architecture (based on state-of-the-art cascaded streaming):

#   Mic → AudioWorklet (48kHz→16kHz PCM)
#       → WebSocket binary frames
#       → Deepgram Live WS (streaming STT, interim in ~150ms)
#       → on_final() callback (utterance boundary)
#       → detect_language (skip LLM if STT hint available)
#       → translate_to_english (skip if English)
#       → RAG retrieve (parallel with translation)
#       → OpenAI streaming LLM (tokens arrive immediately)
#       → Sentence buffer (flush complete sentence to TTS)
#       → Sarvam TTS per sentence (first audio ~200ms after LLM starts)
#       → PCM chunks → WebSocket → AudioContext scheduler → speaker

# Key techniques for low latency:
#   1. Deepgram LIVE WebSocket — interim transcripts every 150ms, no REST round-trip
#   2. Overlap: translation + RAG run in parallel with asyncio.gather()
#   3. LLM token streaming → sentence buffer → TTS fires on first sentence
#   4. TTS per sentence, not full answer — first audio plays while LLM generates rest
#   5. agent_speaking blocks mic forwarding to Deepgram — prevents echo loop
#   6. Interrupt: user speech during agent TTS → cancel TTS task immediately
#   7. No VAD on server — Deepgram's built-in VAD (utterance_end_ms) handles it
# """

# import os, json, asyncio, logging, time
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse, JSONResponse
# from dotenv import load_dotenv

# load_dotenv()

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
#     datefmt="%H:%M:%S",
# )
# log = logging.getLogger("call")

# from agents.state import ConversationTurn
# from services.deepgram_stt import DeepgramStreamingSTT, transcribe
# from services.sarvam_tts import synthesize_pcm_stream
# from services.gemini_translate import (
#     translate_to_english, detect_language,
#     generate_answer_stream, GREETINGS,
# )
# from kb.retriever import retrieve

# app = FastAPI(title="Suvit Voice Agent — Realtime", version="5.0.0")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
# )


# # ── Health ─────────────────────────────────────────────────────────────────────
# @app.get("/health")
# async def health():
#     checks = {}
#     try:
#         from kb.retriever import get_vectorstore; get_vectorstore()
#         checks["faiss_index"] = "ok"
#     except Exception as e:
#         checks["faiss_index"] = f"error: {e}"
#     checks["deepgram"] = "ok" if os.environ.get("DEEPGRAM_API_KEY") else "MISSING"
#     checks["openai"]   = "ok" if os.environ.get("OPENAI_API_KEY")   else "MISSING"
#     checks["gemini"]   = "ok" if os.environ.get("GOOGLE_API_KEY")   else "MISSING"
#     checks["sarvam"]   = "ok" if os.environ.get("SARVAMAI_API_KEY") else "missing (edge-tts fallback)"
#     ok = all("MISSING" not in v and "error" not in v for v in checks.values())
#     return JSONResponse({"status": "ok" if ok else "degraded", "checks": checks})


# @app.post("/transcribe")
# async def transcribe_endpoint(file: UploadFile = File(...)):
#     audio = await file.read()
#     t, lang = await transcribe(audio)
#     return {"transcript": t, "detected_language": lang}


# @app.get("/retrieve")
# async def retrieve_api(q: str, k: int = 3):
#     return {"query": q, "chunks": retrieve(q, k=k)}


# # ══════════════════════════════════════════════════════════════════════════════
# #  WebSocket — full-duplex real-time call
# # ══════════════════════════════════════════════════════════════════════════════

# @app.websocket("/ws/call")
# async def call_ws(ws: WebSocket):
#     await ws.accept()

#     # ── Session state ──────────────────────────────────────────────────────
#     history:        list[ConversationTurn] = []
#     current_lang:   str   = "en"
#     call_active:    bool  = False
#     agent_speaking: bool  = False
#     pipeline_lock         = asyncio.Lock()   # one pipeline at a time

#     tts_task:  asyncio.Task | None = None
#     stt:       DeepgramStreamingSTT | None = None

#     # ── Helpers ────────────────────────────────────────────────────────────

#     async def send_json(obj: dict):
#         try:
#             await ws.send_json(obj)
#         except Exception:
#             pass

#     async def send_bytes(data: bytes):
#         try:
#             await ws.send_bytes(data)
#         except Exception:
#             pass

#     async def abort_tts():
#         nonlocal tts_task, agent_speaking
#         if tts_task and not tts_task.done():
#             tts_task.cancel()
#             try:
#                 await tts_task
#             except asyncio.CancelledError:
#                 pass
#         agent_speaking = False
#         await send_json({"type": "tts_abort"})

#     # ── TTS streaming task ─────────────────────────────────────────────────
#     async def _tts_stream_task(answer: str, lang: str):
#         """
#         Streams TTS sentence-by-sentence using synthesize_pcm_stream.
#         Each sentence is synthesized as it arrives — overlapped with LLM generation.
#         """
#         nonlocal agent_speaking
#         agent_speaking = True
#         await send_json({"type": "tts_start"})
#         try:
#             async for pcm_chunk in synthesize_pcm_stream(answer, lang):
#                 if asyncio.current_task().cancelled():
#                     break
#                 await send_bytes(pcm_chunk)
#                 await asyncio.sleep(0)   # yield to event loop
#             await send_json({"type": "tts_end"})
#         except asyncio.CancelledError:
#             await send_json({"type": "tts_end"})
#             raise
#         finally:
#             agent_speaking = False

#     async def speak(answer: str, lang: str):
#         nonlocal tts_task
#         tts_task = asyncio.create_task(_tts_stream_task(answer, lang))
#         try:
#             await tts_task
#         except asyncio.CancelledError:
#             pass

#     # ── STREAMING pipeline ─────────────────────────────────────────────────
#     async def run_pipeline(transcript: str, stt_lang: str):
#         """
#         Full real-time pipeline:
#           transcript (from Deepgram final) → lang detect + translate + RAG (parallel)
#           → LLM stream → sentence buffer → TTS per sentence

#         The first TTS audio arrives ~400-600 ms after transcript is received.
#         """
#         nonlocal current_lang

#         if agent_speaking:
#             log.info("[PIPELINE] skip — agent speaking")
#             return

#         async with pipeline_lock:
#             t0 = time.perf_counter()
#             log.info("━━━ PIPELINE  transcript=%r  stt_lang=%s ━━━",
#                      transcript[:60], stt_lang)

#             await send_json({"type": "status", "message": "Thinking…"})

#             # ── Step 1+2: language detect + translate  (parallel) ─────────
#             async def _detect():
#                 return await detect_language(transcript, stt_lang_hint=stt_lang)

#             async def _translate(lang: str):
#                 return await translate_to_english(transcript, lang)

#             # Detect first (cheap when hint available), then translate in parallel
#             lang = await _detect()
#             current_lang = lang

#             english_q, chunks = await asyncio.gather(
#                 _translate(lang),
#                 asyncio.to_thread(retrieve, transcript),   # RAG in thread
#             )

#             log.info("[PIPE] detect+translate+rag  %.2f s  lang=%s  chunks=%d",
#                      time.perf_counter() - t0, lang, len(chunks))

#             # Send user bubble to frontend
#             await send_json({
#                 "type":     "transcript",
#                 "user":     transcript,
#                 "language": lang,
#                 "english":  english_q,
#                 "chunks":   len(chunks),
#             })

#             # ── Step 3: LLM streaming → sentence buffer → TTS ─────────────
#             # We collect full answer for history, but speak sentence-by-sentence
#             full_answer_parts: list[str] = []
#             tts_queue: asyncio.Queue[str | None] = asyncio.Queue()

#             async def _llm_to_queue():
#                 """Pull LLM sentences and push to TTS queue."""
#                 try:
#                     async for sentence in generate_answer_stream(
#                         query_english=english_q,
#                         context_chunks=chunks,
#                         response_language=lang,
#                         history=history,
#                     ):
#                         full_answer_parts.append(sentence)
#                         await tts_queue.put(sentence)
#                 finally:
#                     await tts_queue.put(None)   # sentinel

#             async def _queue_to_tts():
#                 """Consume queue and synthesize + stream audio per sentence."""
#                 nonlocal agent_speaking
#                 agent_speaking = True
#                 await send_json({"type": "tts_start"})
#                 first = True
#                 try:
#                     while True:
#                         sentence = await tts_queue.get()
#                         if sentence is None:
#                             break
#                         if asyncio.current_task().cancelled():
#                             break

#                         if first:
#                             first = False
#                             log.info("[TTS] first sentence at %.2f s", time.perf_counter() - t0)

#                         async for pcm in synthesize_pcm_stream(sentence, lang):
#                             if asyncio.current_task().cancelled():
#                                 return
#                             await send_bytes(pcm)
#                             await asyncio.sleep(0)

#                     await send_json({"type": "tts_end"})
#                 except asyncio.CancelledError:
#                     await send_json({"type": "tts_end"})
#                     raise
#                 finally:
#                     agent_speaking = False

#             # Run LLM and TTS concurrently — this is the key overlap
#             nonlocal tts_task
#             llm_task = asyncio.create_task(_llm_to_queue())
#             tts_task = asyncio.create_task(_queue_to_tts())

#             try:
#                 await asyncio.gather(llm_task, tts_task)
#             except asyncio.CancelledError:
#                 llm_task.cancel()
#                 tts_task.cancel()
#                 await asyncio.gather(llm_task, tts_task, return_exceptions=True)

#             # ── Step 4: update history + frontend ─────────────────────────
#             full_answer = " ".join(full_answer_parts).strip()
#             if full_answer:
#                 history.append(ConversationTurn(role="user",      text=transcript, language=lang))
#                 history.append(ConversationTurn(role="assistant", text=full_answer, language=lang))
#                 del history[:-10]   # keep last 5 turns

#                 await send_json({
#                     "type":     "agent_message",
#                     "text":     full_answer,
#                     "language": lang,
#                 })

#             log.info("━━━ PIPELINE DONE  total=%.2f s ━━━", time.perf_counter() - t0)
#             await send_json({"type": "status", "message": "Listening…"})

#     # ── STT callbacks ──────────────────────────────────────────────────────
#     async def on_interim(text: str, lang: str):
#         """Show interim transcript in real-time as user speaks."""
#         if not agent_speaking:
#             await send_json({"type": "interim", "text": text, "language": lang})

#     async def on_final(text: str, lang: str):
#         """Utterance complete — fire pipeline."""
#         if not call_active:
#             return
#         if agent_speaking:
#             # User interrupted agent — abort TTS first
#             log.info("[INTERRUPT] user spoke during agent TTS")
#             await abort_tts()
#             await asyncio.sleep(0.05)

#         if text.strip():
#             asyncio.create_task(run_pipeline(text, lang))

#     # ── Message loop ───────────────────────────────────────────────────────
#     try:
#         while True:
#             msg = await ws.receive()

#             # Binary frame = raw PCM from AudioWorklet → forward to Deepgram Live
#             if "bytes" in msg and msg["bytes"]:
#                 if call_active and stt and stt.is_running():
#                     # Only send to Deepgram when agent is NOT speaking (prevent echo)
#                     if not agent_speaking:
#                         await stt.send(msg["bytes"])
#                 continue

#             if "text" not in msg or not msg["text"]:
#                 continue

#             data     = json.loads(msg["text"])
#             msg_type = data.get("type")

#             # ── call_start ─────────────────────────────────────────────────
#             if msg_type == "call_start":
#                 current_lang = data.get("language", "en")
#                 call_active  = True
#                 history      = []

#                 log.info("━━━ CALL START  lang=%s ━━━", current_lang)
#                 await send_json({"type": "call_accepted"})

#                 # Start Deepgram Live streaming STT
#                 stt = DeepgramStreamingSTT(
#                     on_interim=on_interim,
#                     on_final=on_final,
#                 )
#                 try:
#                     await stt.start()
#                 except Exception as e:
#                     log.error("[STT] failed to connect to Deepgram: %s", e)
#                     await send_json({"type": "error", "message": f"STT init failed: {e}"})
#                     call_active = False
#                     continue

#                 # Greet immediately
#                 greeting = GREETINGS.get(current_lang, GREETINGS["en"])
#                 history.append(ConversationTurn(
#                     role="assistant", text=greeting, language=current_lang
#                 ))
#                 await send_json({
#                     "type": "agent_message", "text": greeting, "language": current_lang
#                 })
#                 await send_json({"type": "status", "message": "Speaking…"})
#                 await speak(greeting, current_lang)
#                 await send_json({"type": "status", "message": "Listening…"})

#             # ── interrupt (explicit from frontend) ─────────────────────────
#             elif msg_type == "interrupt":
#                 if agent_speaking:
#                     log.info("[INTERRUPT] explicit interrupt received")
#                     await abort_tts()
#                     await send_json({"type": "status", "message": "Listening…"})

#             # ── call_end ───────────────────────────────────────────────────
#             elif msg_type == "call_end":
#                 log.info("━━━ CALL END ━━━")
#                 call_active = False

#                 await abort_tts()

#                 if stt:
#                     await stt.stop()
#                     stt = None

#                 bye = {
#                     "en": "Goodbye! Have a great day.",
#                     "hi": "Theek hai! Dhanyavaad. Aapka din accha rahe.",
#                     "gu": "Saru che! Aabhaar. Tamaro divas saras rahe.",
#                 }.get(current_lang, "Goodbye!")

#                 await send_json({"type": "agent_message", "text": bye, "language": current_lang})
#                 await speak(bye, current_lang)
#                 await send_json({"type": "call_ended"})
#                 break

#     except WebSocketDisconnect:
#         log.info("[WS] client disconnected")
#     except Exception as e:
#         import traceback; traceback.print_exc()
#         try:
#             await send_json({"type": "error", "message": str(e)})
#         except Exception:
#             pass
#     finally:
#         if stt:
#             await stt.stop()
#         if tts_task and not tts_task.done():
#             tts_task.cancel()


# # ══════════════════════════════════════════════════════════════════════════════
# #  UI
# # ══════════════════════════════════════════════════════════════════════════════

# @app.get("/", response_class=HTMLResponse)
# async def index():
#     return HTMLResponse(CALL_UI)


# CALL_UI = r"""<!DOCTYPE html>
# <html lang="en">
# <head>
# <meta charset="UTF-8">
# <meta name="viewport" content="width=device-width,initial-scale=1">
# <title>Suvit — Realtime Voice Support</title>
# <style>
# *{box-sizing:border-box;margin:0;padding:0}
# :root{
#   --bg:#0f0f0f;--surface:#1a1a1a;--surface2:#242424;
#   --border:#2a2a2a;--text:#f0f0f0;--muted:#777;
#   --accent:#3b82f6;--danger:#ef4444;--success:#22c55e;--warn:#f59e0b;
# }
# html,body{height:100%;font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text)}
# body{display:flex;align-items:center;justify-content:center;padding:1rem}

# .card{
#   width:100%;max-width:460px;
#   background:var(--surface);border:1px solid var(--border);border-radius:24px;
#   display:flex;flex-direction:column;overflow:hidden;
#   box-shadow:0 12px 60px rgba(0,0,0,.7);
# }

# /* ── Header ── */
# .hdr{padding:1rem 1.4rem;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px}
# .avatar{
#   width:44px;height:44px;border-radius:50%;background:var(--accent);
#   display:flex;align-items:center;justify-content:center;
#   font-size:1.1rem;font-weight:700;flex-shrink:0;letter-spacing:-.5px
# }
# .hdr-info{flex:1;min-width:0}
# .hdr-name{font-size:.95rem;font-weight:600}
# .hdr-status{display:flex;align-items:center;gap:6px;margin-top:3px}
# .dot{width:7px;height:7px;border-radius:50%;background:var(--border);transition:background .3s}
# .dot.listen{background:var(--success);animation:pulse 2s ease-in-out infinite}
# .dot.think{background:var(--warn);animation:pulse 1s ease-in-out infinite}
# .dot.speak{background:var(--accent);animation:pulse .8s ease-in-out infinite}
# @keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
# .hdr-status span{font-size:.73rem;color:var(--muted)}
# .hdr-sub{font-size:.7rem;color:var(--muted);margin-left:auto;flex-shrink:0}

# /* ── Language tabs ── */
# .lang-row{display:flex;gap:6px;padding:.65rem 1.4rem;border-bottom:1px solid var(--border)}
# .lb{
#   padding:3px 14px;border-radius:20px;border:1px solid var(--border);
#   background:transparent;color:var(--muted);font-size:.78rem;cursor:pointer;transition:all .15s
# }
# .lb.on{background:var(--accent);color:#fff;border-color:var(--accent)}

# /* ── Chat log ── */
# .log{
#   flex:1;min-height:260px;max-height:340px;overflow-y:auto;
#   padding:1rem 1.2rem;display:flex;flex-direction:column;gap:.5rem;
# }
# .log::-webkit-scrollbar{width:4px}
# .log::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}

# .bbl{
#   max-width:84%;padding:.5rem .95rem;border-radius:18px;
#   font-size:.86rem;line-height:1.65;animation:rise .15s ease;word-break:break-word;
# }
# @keyframes rise{from{opacity:0;transform:translateY(4px)}}
# .bbl.user{align-self:flex-end;background:#1e3a5f;border-bottom-right-radius:4px}
# .bbl.agent{align-self:flex-start;background:#1e2a1e;border-bottom-left-radius:4px}
# .bbl.system{align-self:center;font-size:.7rem;color:var(--muted);background:none;padding:2px 0}
# .bbl.interim{
#   align-self:flex-end;background:rgba(30,58,95,.5);border:1px dashed #2a4a7f;
#   border-bottom-right-radius:4px;color:#8ab4f8;font-style:italic;
# }
# .ltag{
#   font-size:.63rem;font-weight:700;padding:1px 5px;border-radius:8px;
#   margin-right:4px;vertical-align:middle;letter-spacing:.3px
# }
# .en{background:#1e3a5f;color:#7cb9f8}
# .hi{background:#1e2d1e;color:#86efac}
# .gu{background:#2d2010;color:#fcd34d}

# .empty{
#   flex:1;display:flex;flex-direction:column;align-items:center;
#   justify-content:center;gap:.5rem;color:var(--muted);font-size:.84rem;text-align:center
# }

# /* ── Waveform ── */
# .viz{
#   height:52px;padding:4px 1.2rem;border-top:1px solid var(--border);
#   display:flex;align-items:center;gap:8px
# }
# canvas{flex:1;height:40px}
# .latency{font-size:.65rem;color:var(--muted);white-space:nowrap}

# /* ── Controls ── */
# .ctrls{
#   padding:.85rem 1.4rem 1rem;border-top:1px solid var(--border);
#   display:flex;align-items:center;justify-content:space-between;
# }
# .vol-wrap{display:flex;align-items:center;gap:6px;font-size:.8rem;color:var(--muted)}
# input[type=range]{width:72px;accent-color:var(--accent)}
# .call-btn{
#   width:66px;height:66px;border-radius:50%;border:none;cursor:pointer;
#   font-size:1.6rem;display:flex;align-items:center;justify-content:center;
#   transition:all .2s;background:var(--accent);color:#fff;
#   box-shadow:0 0 0 0 rgba(59,130,246,.4);
# }
# .call-btn:hover{transform:scale(1.05)}
# .call-btn.ring{animation:ring-blue 1.5s ease-in-out infinite}
# @keyframes ring-blue{0%,100%{box-shadow:0 0 0 0 rgba(59,130,246,.4)}70%{box-shadow:0 0 0 18px rgba(59,130,246,0)}}
# .call-btn.active{background:var(--danger)}
# .call-btn.active.ring{animation:ring-red 1.5s ease-in-out infinite}
# @keyframes ring-red{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.4)}70%{box-shadow:0 0 0 18px rgba(239,68,68,0)}}
# .side-info{width:90px;font-size:.7rem;color:var(--muted);text-align:right;line-height:1.7}
# </style>
# </head>
# <body>
# <div class="card">

#   <div class="hdr">
#     <div class="avatar">S</div>
#     <div class="hdr-info">
#       <div class="hdr-name">Suvit Support</div>
#       <div class="hdr-status">
#         <div class="dot" id="dot"></div>
#         <span id="stxt">Ready</span>
#       </div>
#     </div>
#     <div class="hdr-sub" id="ping"></div>
#     <a href="/health" target="_blank" style="font-size:.7rem;color:var(--muted);opacity:.5;text-decoration:none;margin-left:8px">⚙</a>
#   </div>

#   <div class="lang-row">
#     <button class="lb on" data-l="en" onclick="setLang('en')">English</button>
#     <button class="lb"    data-l="hi" onclick="setLang('hi')">Hindi</button>
#     <button class="lb"    data-l="gu" onclick="setLang('gu')">Gujarati</button>
#   </div>

#   <div class="log" id="log">
#     <div class="empty" id="empty">
#       <div style="font-size:2.2rem">🎙️</div>
#       <div>Press call to start</div>
#       <div style="font-size:.72rem;margin-top:4px;line-height:1.6">
#         Real-time · English · Hindi · Gujarati<br>
#         <span style="color:#3b82f6">Deepgram Live → LLM Stream → Sarvam TTS</span>
#       </div>
#     </div>
#   </div>

#   <div class="viz">
#     <canvas id="cv" width="600" height="40"></canvas>
#     <div class="latency" id="latency"></div>
#   </div>

#   <div class="ctrls">
#     <div class="vol-wrap">
#       🔈
#       <input type="range" id="vol" min="0" max="2" step=".05" value="1"
#              oninput="gainNode&&(gainNode.gain.value=+this.value)">
#       🔊
#     </div>
#     <button class="call-btn" id="cbtn" onclick="toggleCall()">📞</button>
#     <div class="side-info" id="sinfo"></div>
#   </div>

# </div>

# <script>
# /* ═══════════════════════════════════════════════════════════════════════════
#    AudioWorklet — inline blob
#    Key tuning vs old version:
#      - Sends PCM chunks every 100ms (not on VAD) so Deepgram Live gets
#        a continuous stream and can return interim results
#      - Server-side Deepgram Live WS handles VAD via utterance_end_ms
#      - INTERRUPT: detect user speech during agent TTS and fire interrupt msg
#    ═══════════════════════════════════════════════════════════════════════════ */
# const WORKLET_CODE = `
# class MicProcessor extends AudioWorkletProcessor {
#   constructor(opts) {
#     super();
#     this._targetSR   = opts.processorOptions.targetSR || 16000;
#     this._ratio      = sampleRate / this._targetSR;
#     this._buf        = [];
#     this._chunkSize  = this._targetSR / 10;  // 100ms chunks

#     // VAD for interrupt detection
#     this._RMS_THRESH     = 0.03;
#     this._SPEECH_FRAMES  = 4;
#     this._speechCount    = 0;
#     this._inSpeech       = false;
#     this._silenceFrames  = 0;
#     this._SILENCE_FRAMES = 25;  // ~500ms silence at 128 samples/20ms
#   }

#   process(inputs) {
#     const ch = inputs[0][0];
#     if (!ch) return true;

#     // Compute RMS for interrupt detection
#     let rms = 0;
#     for (let i = 0; i < ch.length; i++) rms += ch[i] * ch[i];
#     rms = Math.sqrt(rms / ch.length);

#     if (rms > this._RMS_THRESH) {
#       this._speechCount++;
#       this._silenceFrames = 0;
#       if (this._speechCount >= this._SPEECH_FRAMES && !this._inSpeech) {
#         this._inSpeech = true;
#         this.port.postMessage({ type: 'speech_start' });
#       }
#     } else {
#       this._speechCount = 0;
#       if (this._inSpeech) {
#         this._silenceFrames++;
#         if (this._silenceFrames >= this._SILENCE_FRAMES) {
#           this._inSpeech = false;
#           this._silenceFrames = 0;
#           this.port.postMessage({ type: 'speech_end' });
#         }
#       }
#     }

#     // Downsample to target sample rate (simple decimation)
#     for (let i = 0; i < ch.length; i += this._ratio) {
#       this._buf.push(ch[Math.round(i)]);
#     }

#     // Emit fixed-size chunks (100ms) for continuous Deepgram streaming
#     while (this._buf.length >= this._chunkSize) {
#       const slice = this._buf.splice(0, this._chunkSize);
#       const int16 = new Int16Array(this._chunkSize);
#       for (let i = 0; i < this._chunkSize; i++) {
#         int16[i] = Math.max(-32768, Math.min(32767, slice[i] * 32767));
#       }
#       this.port.postMessage({ type: 'pcm', buf: int16.buffer }, [int16.buffer]);
#     }
#     return true;
#   }
# }
# registerProcessor('mic-proc', MicProcessor);
# `;

# /* ═══════════════════════════════════════════════════════════════════════════
#    Main thread state
#    ═══════════════════════════════════════════════════════════════════════════ */
# let ws            = null;
# let callActive    = false;
# let agentSpeaking = false;
# let currentLang   = 'en';

# let micCtx        = null;
# let workletNode   = null;
# let micStream     = null;
# let analyser      = null;

# let playCtx       = null;
# let gainNode      = null;
# const TTS_SR      = 22050;
# let nextPlayAt    = 0;
# let rafId         = null;

# // Latency tracking
# let pipelineStart = 0;

# /* ── Language ── */
# function setLang(l) {
#   currentLang = l;
#   document.querySelectorAll('.lb').forEach(b => b.classList.toggle('on', b.dataset.l === l));
# }

# /* ── Status ── */
# function setStatus(txt, mode = 'idle') {
#   document.getElementById('stxt').textContent = txt;
#   document.getElementById('dot').className = 'dot ' + mode;
# }

# /* ── Log helpers ── */
# let interimBubble = null;

# function addBubble(role, text, lang) {
#   const log = document.getElementById('log');
#   document.getElementById('empty')?.remove();

#   // Remove interim bubble when we get final
#   if (role === 'user' && interimBubble) {
#     interimBubble.remove();
#     interimBubble = null;
#   }

#   const d   = document.createElement('div');
#   d.className = 'bbl ' + role;
#   const tag = lang ? `<span class="ltag ${lang}">${lang.toUpperCase()}</span>` : '';
#   d.innerHTML = role === 'user'
#     ? tag + text
#     : text + (lang ? ' ' + tag : '');
#   log.appendChild(d);
#   log.scrollTop = log.scrollHeight;
# }

# function updateInterim(text, lang) {
#   const log = document.getElementById('log');
#   document.getElementById('empty')?.remove();
#   if (!interimBubble) {
#     interimBubble = document.createElement('div');
#     interimBubble.className = 'bbl interim';
#     log.appendChild(interimBubble);
#   }
#   const tag = lang ? `<span class="ltag ${lang}">${lang.toUpperCase()}</span>` : '';
#   interimBubble.innerHTML = tag + '…' + text;
#   log.scrollTop = log.scrollHeight;
# }

# function sysLog(txt) {
#   const log = document.getElementById('log');
#   const d   = document.createElement('div');
#   d.className = 'bbl system';
#   d.textContent = txt;
#   log.appendChild(d);
#   log.scrollTop = log.scrollHeight;
# }

# /* ═══════════════════════════════════════════════════════════════════════════
#    TTS AUDIO PLAYBACK — gapless AudioContext scheduler
#    ═══════════════════════════════════════════════════════════════════════════ */
# function ensurePlayCtx() {
#   if (playCtx && playCtx.state !== 'closed') return;
#   playCtx  = new AudioContext({ sampleRate: TTS_SR });
#   gainNode = playCtx.createGain();
#   gainNode.gain.value = +document.getElementById('vol').value;
#   gainNode.connect(playCtx.destination);
#   nextPlayAt = 0;
# }

# function scheduleChunk(arrayBuffer) {
#   if (!playCtx || playCtx.state === 'closed') return;
#   const int16   = new Int16Array(arrayBuffer);
#   const float32 = new Float32Array(int16.length);
#   for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768;
#   const buf = playCtx.createBuffer(1, float32.length, TTS_SR);
#   buf.copyToChannel(float32, 0);
#   const src  = playCtx.createBufferSource();
#   src.buffer = buf;
#   src.connect(gainNode);
#   const now  = playCtx.currentTime;
#   const when = Math.max(now, nextPlayAt);
#   src.start(when);
#   nextPlayAt = when + buf.duration;
# }

# function clearPlayback() {
#   if (playCtx && playCtx.state !== 'closed') {
#     playCtx.close().catch(() => {});
#   }
#   playCtx = null; gainNode = null; nextPlayAt = 0;
#   agentSpeaking = false;
# }

# /* ═══════════════════════════════════════════════════════════════════════════
#    WAVEFORM VISUALIZER
#    ═══════════════════════════════════════════════════════════════════════════ */
# function startWave() {
#   const cv  = document.getElementById('cv');
#   const ctx = cv.getContext('2d');
#   const buf = new Uint8Array(analyser ? analyser.fftSize : 256);

#   function draw() {
#     rafId = requestAnimationFrame(draw);
#     if (analyser) analyser.getByteTimeDomainData(buf);
#     ctx.clearRect(0, 0, cv.width, cv.height);
#     ctx.beginPath();
#     const sl = cv.width / buf.length;
#     let x = 0;
#     for (let i = 0; i < buf.length; i++) {
#       const y = ((buf[i] / 128) - 1) * (cv.height / 2) + cv.height / 2;
#       i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
#       x += sl;
#     }
#     ctx.strokeStyle = agentSpeaking ? '#3b82f6' : '#22c55e';
#     ctx.lineWidth   = 1.5;
#     ctx.stroke();
#   }
#   draw();
# }

# function stopWave() {
#   if (rafId) cancelAnimationFrame(rafId);
#   const cv  = document.getElementById('cv');
#   const ctx = cv.getContext('2d');
#   ctx.clearRect(0, 0, cv.width, cv.height);
# }

# /* ═══════════════════════════════════════════════════════════════════════════
#    WEBSOCKET
#    ═══════════════════════════════════════════════════════════════════════════ */
# function connectWS() {
#   const proto = location.protocol === 'https:' ? 'wss' : 'ws';
#   ws = new WebSocket(`${proto}://${location.host}/ws/call`);
#   ws.binaryType = 'arraybuffer';

#   ws.onopen = () => {
#     ws.send(JSON.stringify({ type: 'call_start', language: currentLang }));
#   };

#   ws.onmessage = e => {
#     // Binary = TTS PCM audio chunk
#     if (e.data instanceof ArrayBuffer) {
#       if (!agentSpeaking) return;
#       ensurePlayCtx();
#       scheduleChunk(e.data);
#       return;
#     }

#     const msg = JSON.parse(e.data);

#     switch (msg.type) {

#       case 'call_accepted':
#         setStatus('Connecting…', 'idle');
#         break;

#       case 'status': {
#         const modeMap = {
#           'Thinking…': 'think', 'Transcribing…': 'think',
#           'Listening…': 'listen', 'Speaking…': 'speak', 'Processing…': 'think',
#         };
#         setStatus(msg.message, modeMap[msg.message] || 'idle');
#         break;
#       }

#       case 'interim':
#         // Show live interim transcript while user speaks
#         updateInterim(msg.text, msg.language);
#         break;

#       case 'transcript':
#         // Final transcript — show user bubble, log latency start
#         pipelineStart = Date.now();
#         addBubble('user', msg.user, msg.language);
#         document.getElementById('sinfo').textContent =
#           `${msg.chunks} chunks\n${msg.english !== msg.user ? '→ ' + msg.english.slice(0, 35) : ''}`;
#         break;

#       case 'tts_start':
#         agentSpeaking = true;
#         ensurePlayCtx();
#         setStatus('Speaking…', 'speak');
#         if (pipelineStart) {
#           const ms = Date.now() - pipelineStart;
#           document.getElementById('latency').textContent = `⚡ ${ms}ms`;
#           document.getElementById('ping').textContent = `${ms}ms`;
#         }
#         break;

#       case 'tts_end':
#         agentSpeaking = false;
#         if (callActive) setStatus('Listening…', 'listen');
#         break;

#       case 'tts_abort':
#         clearPlayback();
#         if (callActive) setStatus('Listening…', 'listen');
#         break;

#       case 'agent_message':
#         addBubble('agent', msg.text, msg.language);
#         break;

#       case 'call_ended':
#         endCall(false);
#         break;

#       case 'error':
#         sysLog('⚠ ' + msg.message);
#         setStatus('Listening…', 'listen');
#         break;
#     }
#   };

#   ws.onerror = () => sysLog('Connection error — is the server running?');
#   ws.onclose = () => { if (callActive) endCall(false); };
# }

# /* ═══════════════════════════════════════════════════════════════════════════
#    MICROPHONE — AudioWorklet capture
#    ═══════════════════════════════════════════════════════════════════════════ */
# async function startMic() {
#   micStream = await navigator.mediaDevices.getUserMedia({
#     audio: { echoCancellation: true, noiseSuppression: true, sampleRate: 48000 }
#   });

#   micCtx = new AudioContext({ sampleRate: 48000 });

#   const blob    = new Blob([WORKLET_CODE], { type: 'application/javascript' });
#   const blobURL = URL.createObjectURL(blob);
#   await micCtx.audioWorklet.addModule(blobURL);
#   URL.revokeObjectURL(blobURL);

#   const src = micCtx.createMediaStreamSource(micStream);

#   analyser = micCtx.createAnalyser();
#   analyser.fftSize = 256;
#   src.connect(analyser);

#   workletNode = new AudioWorkletNode(micCtx, 'mic-proc', {
#     processorOptions: { targetSR: 16000 }
#   });
#   src.connect(workletNode);

#   workletNode.port.onmessage = e => {
#     const { type, buf } = e.data;

#     if (type === 'pcm' && ws && ws.readyState === WebSocket.OPEN && callActive) {
#       if (!agentSpeaking) {
#         // Continuous streaming to server — Deepgram Live handles VAD
#         ws.send(buf);
#       }
#     }

#     // Interrupt: user speech detected while agent is playing
#     if (type === 'speech_start' && agentSpeaking && callActive) {
#       ws.send(JSON.stringify({ type: 'interrupt' }));
#       clearPlayback();
#     }
#   };

#   startWave();
# }

# function stopMic() {
#   workletNode?.disconnect(); workletNode = null;
#   micCtx?.close().catch(() => {}); micCtx = null;
#   micStream?.getTracks().forEach(t => t.stop()); micStream = null;
#   analyser = null;
#   stopWave();
# }

# /* ═══════════════════════════════════════════════════════════════════════════
#    CALL CONTROL
#    ═══════════════════════════════════════════════════════════════════════════ */
# async function toggleCall() {
#   if (!callActive) await startCall();
#   else             endCall(true);
# }

# async function startCall() {
#   callActive    = true;
#   agentSpeaking = false;
#   interimBubble = null;
#   document.getElementById('log').innerHTML = '';

#   const btn = document.getElementById('cbtn');
#   btn.textContent = '📵';
#   btn.classList.add('active', 'ring');

#   setStatus('Connecting…', 'idle');
#   connectWS();
#   await startMic();
# }

# function endCall(sendEnd) {
#   callActive    = false;
#   agentSpeaking = false;

#   if (sendEnd && ws?.readyState === WebSocket.OPEN)
#     ws.send(JSON.stringify({ type: 'call_end' }));
#   else
#     ws?.close();

#   stopMic();
#   clearPlayback();

#   const btn = document.getElementById('cbtn');
#   btn.textContent = '📞';
#   btn.classList.remove('active', 'ring');

#   setStatus('Call ended', 'idle');
#   setTimeout(() => setStatus('Ready', 'idle'), 2500);
# }
# </script>
# </body>
# </html>"""











  

"""
main.py — Suvit Voice Agent  v5  (full-duplex phone-call, all bugs fixed)
══════════════════════════════════════════════════════════════════════════
  
Bug fixes vs v4:
  1. PCM buffering paused while agent is speaking — no more pipeline fires
     on garbage audio captured during TTS playback.
  2. Interrupt only sent once per speech burst, not per 4096-sample chunk.
  3. VAD thresholds recalibrated for real microphone levels.
  4. SILENCE_FRAMES computed correctly in terms of 48 kHz AudioContext frames
     (128 samples each) not 16 kHz — was 5× too short before.
  5. JS `addBubble` function renamed from `log` to avoid collision with
     the HTML element id="log" and Math.log.
  6. Agent-speaking guard moved into worklet message handler to prevent
     race condition between tts_start JSON and next PCM binary frame.

WebSocket protocol (unchanged):
  CLIENT → SERVER:
    binary frame              = raw Int16 LE PCM, 16 kHz, mono
    JSON { type:"call_start",  language }
    JSON { type:"vad_end" }   — client VAD silence detected
    JSON { type:"interrupt" } — user spoke over agent
    JSON { type:"call_end" }  — stop button
  SERVER → CLIENT:
    JSON { type:"call_accepted" }
    JSON { type:"status",     message }
    JSON { type:"transcript", user, language, english, chunks }
    JSON { type:"tts_start" }
    binary frame              = raw Int16 LE PCM, 22050 Hz, mono
    JSON { type:"tts_end" }
    JSON { type:"clear_queue" }
    JSON { type:"call_ended", message }
    JSON { type:"error",      message }
"""

import os, json, asyncio, logging, time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("call")

from agents.state import ConversationTurn
from services.deepgram_stt import transcribe, DeepgramStreamingSTT
from services.sarvam_tts import synthesize_pcm_stream, synthesize
from services.gemini_translate import (
    translate_to_english, detect_language,
    generate_answer, GREETINGS,
)
from kb.retriever import retrieve

app = FastAPI(title="Suvit Voice Agent", version="5.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_event():
    async def _bg_load_kb():
        log.info("[BOOT] Loading Knowledge Base in background task...")
        try:
            from kb.retriever import get_vectorstore
            # Perform expensive I/O/Model loading in dedicated background thread
            await asyncio.to_thread(get_vectorstore)
            log.info("[BOOT] Knowledge Base Load Complete.")
        except Exception as e:
            log.error("[BOOT] FAILED to load KB: %s", e)

    # Fire and forget immediately without blocking FastAPIs fast startup
    asyncio.create_task(_bg_load_kb())




# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    checks = {}
    try:
        from kb.retriever import get_vectorstore; get_vectorstore()
        checks["faiss_index"] = "ok"
    except Exception as e:
        checks["faiss_index"] = f"error: {e}"
    checks["deepgram"] = "ok" if os.environ.get("DEEPGRAM_API_KEY") else "MISSING"
    checks["openai"]   = "ok" if os.environ.get("OPENAI_API_KEY")   else "MISSING"
    checks["gemini"]   = "ok" if os.environ.get("GOOGLE_API_KEY")   else "MISSING"
    checks["sarvam"]   = ("ok" if os.environ.get("SARVAMAI_API_KEY")
                          else "missing — edge-tts fallback active")
    ok = all("MISSING" not in v and "error" not in v for v in checks.values())
    return JSONResponse({"status": "ok" if ok else "degraded", "checks": checks})


@app.post("/transcribe")
async def transcribe_file(file: UploadFile = File(...)):
    audio = await file.read()
    t, lang = await transcribe(audio)
    return {"transcript": t, "detected_language": lang}


@app.get("/retrieve")
async def retrieve_api(q: str, k: int = 3):
    return {"query": q, "chunks": retrieve(q, k=k)}


# ── WebSocket: full-duplex voice call ─────────────────────────────────────────

@app.websocket("/ws/call")
async def call_ws(ws: WebSocket):
    await ws.accept()

    history:        list[ConversationTurn] = []
    current_lang:   str  = "en"
    call_active:    bool = False
    agent_speaking: bool = False   # True while server is streaming TTS

    tts_task:    asyncio.Task | None = None
    pipeline_task: asyncio.Task | None = None
    dg_stt:      DeepgramStreamingSTT | None = None

    # ── send helpers ──────────────────────────────────────────────────────────
    async def send_json(obj: dict):
        try:    await ws.send_json(obj)
        except Exception: pass

    async def send_bytes(data: bytes):
        try:    await ws.send_bytes(data)
        except Exception: pass

    # ── Task Cancellation helpers ─────────────────────────────────────────────
    async def abort_pipeline():
        nonlocal tts_task, pipeline_task, agent_speaking
        
        # 1. Kill active LLM/RAG generation
        if pipeline_task and not pipeline_task.done():
            pipeline_task.cancel()
            try:    await pipeline_task
            except asyncio.CancelledError: pass
            
        # 2. Kill active voice stream
        if tts_task and not tts_task.done():
            tts_task.cancel()
            try:    await tts_task
            except asyncio.CancelledError: pass
            
        agent_speaking = False
        await send_json({"type": "clear_queue"})

    async def _stream_tts(text: str, lang: str):
        nonlocal agent_speaking
        agent_speaking = True
        await send_json({"type": "tts_start"})
        try:
            async for chunk in synthesize_pcm_stream(text, lang):
                if tts_task and tts_task.cancelled():
                    break
                await send_bytes(chunk)
                await asyncio.sleep(0)          # yield so interrupts can land
            await send_json({"type": "tts_end"})
        except asyncio.CancelledError:
            await send_json({"type": "tts_end"})
            raise
        finally:
            agent_speaking = False

    async def speak(text: str, lang: str):
        nonlocal tts_task
        tts_task = asyncio.create_task(_stream_tts(text, lang))
        try:    await tts_task
        except asyncio.CancelledError: pass

    # ── STT → translate → RAG → LLM → TTS ───────────────────────────────────
    async def run_pipeline(audio_bytes: bytes | None = None, text_input: str | None = None):
        t0       = time.perf_counter()
        if audio_bytes:
            pcm_secs = len(audio_bytes) / (16_000 * 2)
            log.info("━━━ PIPELINE AUDIO  pcm=%.2fs  bytes=%d ━━━", pcm_secs, len(audio_bytes))
        else:
            log.info("━━━ PIPELINE TEXT   %r ━━━", text_input[:50] if text_input else "")

        # 1. Input Acquisition (STT or Text)
        transcript = ""
        lang_stt = "en"

        if audio_bytes:
            await send_json({"type": "status", "message": "Transcribing…"})
            t1 = time.perf_counter()
            try:
                transcript, lang_stt = await transcribe(audio_bytes)
            except Exception as e:
                log.error("[STT] FAILED: %s", e)
                await send_json({"type": "error", "message": f"STT error: {e}"})
                return
            transcript = transcript.strip()
            log.info("[STT]  %.2fs  lang=%s  %r", time.perf_counter()-t1, lang_stt, transcript[:80])
        elif text_input:
            transcript = text_input.strip()
            # Deepgram stream already provided text_input, skip STT
        else:
            return

        if not transcript:
            # Skip empty strings emitted by background noise
            return

        # 2. Language refinement
        t2 = time.perf_counter()
        try:
            lang = await detect_language(transcript)
        except Exception as e:
            log.warning("[LANG] failed (%s) — using stt lang %s", e, lang_stt)
            lang = lang_stt
        nonlocal current_lang
        current_lang = lang
        log.info("[LANG]  %.2fs  %s → %s", time.perf_counter()-t2, lang_stt, lang)

        # 3. Translate
        await send_json({"type": "status", "message": "Thinking…"})
        t3 = time.perf_counter()
        english_q = await translate_to_english(transcript, lang)
        log.info("[TRANSLATE]  %.2fs  %r → %r",
                 time.perf_counter()-t3, transcript[:50], english_q[:50])

        # 4. RAG
        t4 = time.perf_counter()
        chunks = retrieve(english_q)
        log.info("[RAG]  %.2fs  %d chunks", time.perf_counter()-t4, len(chunks))

        await send_json({"type": "transcript", "user": transcript,
                         "language": lang, "english": english_q, "chunks": len(chunks)})

        # 5. Generate
        t5 = time.perf_counter()
        answer = await generate_answer(
            query_english=english_q,
            context_chunks=chunks,
            response_language=lang,
            history=history,
        )
        log.info("[LLM]  %.2fs  %r", time.perf_counter()-t5, answer[:100])

        # 6. History
        history.append(ConversationTurn(role="user",      text=transcript, language=lang))
        history.append(ConversationTurn(role="assistant", text=answer,     language=lang))
        del history[:-10]

        # Send assistant text response explicitly to client (so frontend can render bubble)
        await send_json({"type": "assistant_end", "text": answer, "language": lang})

        # 7. Speak
        t6 = time.perf_counter()
        log.info("[TTS]  synthesizing…")
        await speak(answer, lang)
        log.info("[TTS]  %.2fs", time.perf_counter()-t6)
        log.info("━━━ DONE  total=%.2fs ━━━", time.perf_counter()-t0)

    # ── Deepgram Stream Handlers ──────────────────────────────────────────────
    async def dg_on_speech_started():
        log.info("[CALLBACK] Cloud VAD detects user speech -> Halting agent")
        await abort_pipeline()
        # Also notify client UI to switch state immediately
        await send_json({"type": "status", "message": "Listening…"})

    async def dg_on_final(text: str, lang: str):
        if not text.strip(): return
        log.info("[CALLBACK] Sentence finalized: %r", text)
        
        # Immediately execute the AI analysis logic using the finalized string
        nonlocal pipeline_task
        await abort_pipeline()
        pipeline_task = asyncio.create_task(run_pipeline(text_input=text))

    async def dg_on_interim(text: str, lang: str):
        # Forward streaming text to frontend immediately for "live typing" UI
        await send_json({"type": "transcript_update", "text": text, "language": lang})

    # Initialize and bind the persistent stream engine
    dg_stt = DeepgramStreamingSTT(
        on_speech_started = dg_on_speech_started,
        on_final          = dg_on_final,
        on_interim        = dg_on_interim
    )

    # ── message loop ──────────────────────────────────────────────────────────
    try:
        while True:
            msg = await ws.receive()

            # ── raw PCM binary frame from AudioWorklet ────────────────────
            if "bytes" in msg and msg["bytes"]:
                # CONTINUOUS STREAM: Feed all bytes directly into Deepgram server-side engine
                if call_active and dg_stt:
                    await dg_stt.send(msg["bytes"])
                continue

            # ── JSON control messages ─────────────────────────────────────
            if "text" not in msg or not msg["text"]:
                continue

            data     = json.loads(msg["text"])
            msg_type = data.get("type")

            # ─────────────────────────────────────────────────────────────
            if msg_type == "call_start":
                current_lang  = data.get("language", "en")
                call_active   = True
                history       = []
                log.info("━━━ CALL STARTED (STREAMING ACTIVE)  lang=%s ━━━", current_lang)
                
                # Boot the backend deepgram websocket
                await dg_stt.start()
                
                await send_json({"type": "call_accepted"})
                greeting = GREETINGS.get(current_lang, GREETINGS["en"])
                log.info("[GREET]  %r", greeting)
                history.append(ConversationTurn(
                    role="assistant", text=greeting, language=current_lang))
                await speak(greeting, current_lang)
                await send_json({"type": "status", "message": "Listening…"})

            # ─────────────────────────────────────────────────────────────
            elif msg_type == "vad_end":
                # LEGACY: Deepgram performs VAD server-side now. We ignore client triggers.
                continue

            # ─────────────────────────────────────────────────────────────
            elif msg_type == "text_input":
                query = data.get("text")
                if query:
                    log.info("[TEXT] user keyboard input: %r", query)
                    await abort_pipeline()
                    pipeline_task = asyncio.create_task(run_pipeline(text_input=query))

            # ─────────────────────────────────────────────────────────────
            elif msg_type == "interrupt":
                # Already handled natively via on_speech_started cloud callback,
                # but keeping client interrupt as instant redundant fallback.
                log.info("[INTERRUPT]  Manual UI interrupt payload received")
                await abort_pipeline()
                await send_json({"type": "status", "message": "Listening…"})

            # ─────────────────────────────────────────────────────────────
            elif msg_type == "call_end":
                log.info("━━━ CALL ENDED ━━━")
                call_active = False
                await abort_pipeline()
                if dg_stt: await dg_stt.stop()
                bye = {
                    "en": "Goodbye! Have a great day.",
                    "hi": "Theek hai! Dhanyavaad. Aapka din accha rahe.",
                    "gu": "Saru che! Aabhaar. Tamaro divas saras rahe.",
                }.get(current_lang, "Goodbye!")
                log.info("[BYE]  %r", bye)
                await speak(bye, current_lang)
                await send_json({"type": "call_ended", "message": bye})
                break

    except WebSocketDisconnect:
        log.info("[WS]  client disconnected")
    except Exception as e:
        import traceback; traceback.print_exc()
        try:    await send_json({"type": "error", "message": str(e)})
        except Exception: pass


# ── UI ────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(CALL_UI)


CALL_UI = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Suvit — Voice Support</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0f0f0f;--surface:#1a1a1a;--border:#2e2e2e;
  --text:#f0f0f0;--muted:#777;
  --blue:#3b82f6;--red:#ef4444;--green:#22c55e;--amber:#f59e0b;
  --user-bg:#1e3a5f;--agent-bg:#1a2e1a;
}
html,body{height:100%;font-family:system-ui,sans-serif;background:var(--bg);color:var(--text)}
body{display:flex;align-items:center;justify-content:center;padding:1rem}

.card{width:100%;max-width:440px;background:var(--surface);border:1px solid var(--border);
  border-radius:24px;display:flex;flex-direction:column;overflow:hidden;
  box-shadow:0 8px 48px rgba(0,0,0,.7)}

/* header */
.hdr{padding:1rem 1.4rem;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px}
.av{width:42px;height:42px;border-radius:50%;background:var(--blue);display:flex;
  align-items:center;justify-content:center;font-size:1.1rem;font-weight:600;flex-shrink:0}
.hdr-info{flex:1}
.hdr-name{font-size:.95rem;font-weight:500}
.status-row{display:flex;align-items:center;gap:6px;margin-top:3px}
.dot{width:7px;height:7px;border-radius:50%;background:var(--border);flex-shrink:0}
.dot.listen{background:var(--green);animation:blink 1.8s ease-in-out infinite}
.dot.think {background:var(--amber);animation:blink 1s   ease-in-out infinite}
.dot.speak {background:var(--blue); animation:blink .8s  ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}
.status-row span{font-size:.74rem;color:var(--muted)}

/* lang */
.lang-row{display:flex;gap:6px;padding:.65rem 1.4rem;border-bottom:1px solid var(--border)}
.lb{padding:3px 14px;border-radius:20px;border:1px solid var(--border);
  background:transparent;color:var(--muted);font-size:.78rem;cursor:pointer;transition:all .15s}
.lb.on{background:var(--blue);color:#fff;border-color:var(--blue)}

/* conversation */
.conv{flex:1;min-height:280px;max-height:360px;overflow-y:auto;
  padding:1rem 1.2rem;display:flex;flex-direction:column;gap:.55rem}
.conv::-webkit-scrollbar{width:3px}
.conv::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}

.bbl{max-width:82%;padding:.5rem .9rem;border-radius:16px;
  font-size:.86rem;line-height:1.6;animation:rise .18s ease}
@keyframes rise{from{opacity:0;transform:translateY(5px)}}
.bbl.user {align-self:flex-end;background:var(--user-bg);border-bottom-right-radius:4px}
.bbl.agent{align-self:flex-start;background:var(--agent-bg);border-bottom-left-radius:4px}
.bbl.sys  {align-self:center;font-size:.72rem;color:var(--muted);background:none;padding:2px 0}
.ltag{font-size:.65rem;font-weight:600;padding:1px 5px;border-radius:8px;margin:0 3px;vertical-align:middle}
.tag-en{background:#1e3a5f;color:#7cb9f8}
.tag-hi{background:#1e2d1e;color:#86efac}
.tag-gu{background:#2d2010;color:#fcd34d}

.empty-state{flex:1;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:.5rem;color:var(--muted);font-size:.85rem;text-align:center}

/* waveform */
.viz{height:52px;padding:0 1.2rem;border-top:1px solid var(--border);display:flex;align-items:center}
canvas{width:100%;height:38px}

/* controls */
.ctrls{padding:.85rem 1.4rem 1.1rem;border-top:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between}
.vol{display:flex;align-items:center;gap:5px;font-size:.78rem;color:var(--muted)}
input[type=range]{width:70px;accent-color:var(--blue)}
.cbtn{width:64px;height:64px;border-radius:50%;border:none;cursor:pointer;
  font-size:1.5rem;display:flex;align-items:center;justify-content:center;
  background:var(--blue);color:#fff;transition:all .2s;
  box-shadow:0 0 0 0 rgba(59,130,246,.5)}
.cbtn.on{background:var(--red);box-shadow:0 0 0 0 rgba(239,68,68,.5)}
.cbtn.pulse{animation:callpulse 1.5s ease-in-out infinite}
@keyframes callpulse{
  0%,100%{box-shadow:0 0 0 0 rgba(59,130,246,.5)}
  70%    {box-shadow:0 0 0 18px rgba(59,130,246,0)}}
.cbtn.on.pulse{animation:callpulse-red 1.5s ease-in-out infinite}
@keyframes callpulse-red{
  0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,.5)}
  70%    {box-shadow:0 0 0 18px rgba(239,68,68,0)}}
.meta{width:90px;font-size:.7rem;color:var(--muted);text-align:right;line-height:1.7}

/* VAD indicator */
.vad-bar{height:3px;background:var(--border);border-radius:2px;margin:0 1.2rem}
.vad-fill{height:100%;width:0%;border-radius:2px;background:var(--green);transition:width .05s}
</style>
</head>
<body>
<div class="card">

  <div class="hdr">
    <div class="av">S</div>
    <div class="hdr-info">
      <div class="hdr-name">Suvit Support</div>
      <div class="status-row">
        <div class="dot" id="dot"></div>
        <span id="stxt">Ready — press 📞 to start</span>
      </div>
    </div>
    <a href="/health" target="_blank"
       style="font-size:.7rem;color:var(--muted);text-decoration:none;opacity:.5">⚙</a>
  </div>

  <div class="lang-row">
    <button class="lb on" data-l="en" onclick="pickLang('en')">English</button>
    <button class="lb"    data-l="hi" onclick="pickLang('hi')">Hindi</button>
    <button class="lb"    data-l="gu" onclick="pickLang('gu')">Gujarati</button>
  </div>

  <div class="conv" id="conv">
    <div class="empty-state" id="empty">
      <div style="font-size:2rem">📞</div>
      <div>Press the call button to connect</div>
      <div style="font-size:.72rem;opacity:.6;margin-top:.2rem">
        English · Hindi · Gujarati
      </div>
    </div>
  </div>

  <!-- Thin bar showing mic energy (VAD level) -->
  <div class="vad-bar"><div class="vad-fill" id="vad-fill"></div></div>

  <div class="viz"><canvas id="cv" width="400" height="38"></canvas></div>

  <div class="ctrls">
    <div class="vol">
      🔈
      <input type="range" id="vol" min="0" max="2" step=".05" value="1"
             oninput="if(gainNode) gainNode.gain.value=+this.value">
      🔊
    </div>
    <button class="cbtn" id="cbtn" onclick="toggleCall()">📞</button>
    <div class="meta" id="meta"></div>
  </div>

</div><!-- .card -->

<script>
/* ════════════════════════════════════════════════════════════════════════════
   AudioWorklet — runs on audio render thread (separate from main thread).

   FIXES vs v4:
     • SPEECH_THRESH raised to 0.015 (was 0.02 — too sensitive on some mics)
     • SILENCE_FRAMES = 80 frames × 128 samples @ 48kHz = ~213ms per frame-group
       → ~1700ms silence before vad_end. Previously 40 frames ≈ 107ms — too short.
     • hasSpeech flag: worklet only sends pcm chunks AFTER speech has started,
       not on every process() tick including background noise.
     • speakingGuard: main thread posts {type:'agent_speaking', v:bool} to worklet
       so the worklet itself can gate PCM output and VAD — eliminates race condition.
   ════════════════════════════════════════════════════════════════════════════ */
const WORKLET_SRC = `
class MicProcessor extends AudioWorkletProcessor {
  constructor(opts) {
    super();
    this._tgtSR  = opts.processorOptions.targetSR || 16000;
    this._ratio  = sampleRate / this._tgtSR;   // 48000/16000 = 3
    this._pcmBuf = [];

    // VAD thresholds (tuned for typical laptop/phone mics)
    this._SPEECH_THRESH  = 0.015;   // RMS above this = speech
    this._SILENCE_THRESH = 0.008;   // RMS below this = silence
    this._SPEECH_FRAMES  = 5;       // consecutive loud frames before vad_start
    this._SILENCE_FRAMES = 80;      // consecutive quiet frames before vad_end
                                    // 80 × 128 samples / 48000 Hz ≈ 213 ms per group
                                    // total silence ≈ 1.7 s

    this._speechCnt  = 0;
    this._silenceCnt = 0;
    this._inSpeech   = false;
    this._agentOn    = false;       // main thread tells us when agent speaks
    this._energy     = 0;          // smoothed RMS for UI

    this.port.onmessage = ({data}) => {
      // Main thread → worklet: update agent-speaking state
      if (data.type === 'agent_speaking') this._agentOn = data.v;
    };
  }

  process(inputs) {
    const ch = inputs[0]?.[0];
    if (!ch || ch.length === 0) return true;

    // Compute RMS energy
    let sum = 0;
    for (let i = 0; i < ch.length; i++) sum += ch[i] * ch[i];
    const rms = Math.sqrt(sum / ch.length);

    // Smooth energy for UI bar
    this._energy = this._energy * 0.85 + rms * 0.15;
    this.port.postMessage({ type: 'energy', v: this._energy });

    // While agent is speaking: reset all VAD state, do NOT send PCM or vad_end.
    // This is the key fix — the mic picks up speaker output, we must ignore it.
    if (this._agentOn) {
      this._speechCnt  = 0;
      this._silenceCnt = 0;
      this._inSpeech   = false;
      this._pcmBuf     = [];
      return true;
    }

    // ── VAD state machine ─────────────────────────────────────────────────
    if (rms > this._SPEECH_THRESH) {
      this._speechCnt++;
      this._silenceCnt = 0;
      if (this._speechCnt >= this._SPEECH_FRAMES && !this._inSpeech) {
        this._inSpeech = true;
        this.port.postMessage({ type: 'vad_start' });
      }
    } else if (rms < this._SILENCE_THRESH && this._inSpeech) {
      this._silenceCnt++;
      this._speechCnt = 0;
      if (this._silenceCnt >= this._SILENCE_FRAMES) {
        this._inSpeech   = false;
        this._silenceCnt = 0;
        this.port.postMessage({ type: 'vad_end' });
      }
    } else {
      // in between thresholds — decay speech counter
      if (this._speechCnt > 0) this._speechCnt--;
    }

    // ── Downsample Float32@48kHz → Int16@16kHz and emit ──────────────────
    // Only accumulate if we are (or just were) in speech — avoids sending
    // silence noise chunks that produce empty STT responses.
    if (this._inSpeech || this._pcmBuf.length > 0) {
      for (let i = 0; i < ch.length; i += this._ratio) {
        this._pcmBuf.push(ch[Math.round(i)]);
      }

      while (this._pcmBuf.length >= 4096) {
        const slice = this._pcmBuf.splice(0, 4096);
        const i16   = new Int16Array(4096);
        for (let i = 0; i < 4096; i++)
          i16[i] = Math.max(-32768, Math.min(32767, slice[i] * 32767));
        this.port.postMessage({ type: 'pcm', buf: i16.buffer }, [i16.buffer]);
      }
    }

    return true;
  }
}
registerProcessor('mic-proc', MicProcessor);
`;

/* ════════════════════════════════════════════════════════════════════════════
   Main thread globals
   ════════════════════════════════════════════════════════════════════════════ */
let ws           = null;
let callActive   = false;
let agentSpeaking= false;
let currentLang  = 'en';

// Mic capture (48 kHz AudioContext + AudioWorklet)
let micCtx       = null;
let workletNode  = null;
let micStream    = null;
let analyserNode = null;

// TTS playback (22050 Hz AudioContext, gapless scheduling)
let playCtx      = null;
let gainNode     = null;
const TTS_SR     = 22050;
let nextPlayAt   = 0;

// Interrupt: only send once per burst, not per chunk
let interruptSent = false;

// Waveform RAF
const cvEl = document.getElementById('cv');
const cx   = cvEl.getContext('2d');
let rafId  = null;

/* ── Language picker ──────────────────────────────────────────────────────── */
function pickLang(l) {
  currentLang = l;
  document.querySelectorAll('.lb')
    .forEach(b => b.classList.toggle('on', b.dataset.l === l));
}

/* ── Status display ───────────────────────────────────────────────────────── */
function setStatus(txt, mode) {
  document.getElementById('stxt').textContent = txt;
  const d = document.getElementById('dot');
  d.className = 'dot' + (mode ? ' ' + mode : '');
}

/* ── Conversation bubbles ─────────────────────────────────────────────────── */
// NOTE: function is named "addBubble" not "log" to avoid collision with
// document.getElementById('log') and Math.log.
function addBubble(role, text, lang) {
  const el  = document.getElementById('conv');
  const emp = document.getElementById('empty');
  if (emp) emp.remove();

  const d   = document.createElement('div');
  d.className = 'bbl ' + role;
  const tag = lang
    ? `<span class="ltag tag-${lang}">${lang.toUpperCase()}</span>`
    : '';
  d.innerHTML = role === 'user'
    ? tag + escHtml(text)
    : escHtml(text) + tag;
  el.appendChild(d);
  el.scrollTop = el.scrollHeight;
}

function sysMsg(text) {
  const el = document.getElementById('conv');
  const d  = document.createElement('div');
  d.className = 'bbl sys';
  d.textContent = text;
  el.appendChild(d);
  el.scrollTop = el.scrollHeight;
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

/* ── TTS playback helpers ─────────────────────────────────────────────────── */
function ensurePlayCtx() {
  if (playCtx && playCtx.state !== 'closed') return;
  playCtx    = new AudioContext({ sampleRate: TTS_SR });
  gainNode   = playCtx.createGain();
  gainNode.gain.value = +document.getElementById('vol').value;
  gainNode.connect(playCtx.destination);
  nextPlayAt = 0;
}

function scheduleChunk(arrayBuf) {
  if (!playCtx || playCtx.state === 'closed') return;

  const i16   = new Int16Array(arrayBuf);
  const f32   = new Float32Array(i16.length);
  for (let i = 0; i < i16.length; i++) f32[i] = i16[i] / 32768;

  const buf = playCtx.createBuffer(1, f32.length, TTS_SR);
  buf.copyToChannel(f32, 0);

  const src  = playCtx.createBufferSource();
  src.buffer = buf;
  src.connect(gainNode);

  const now  = playCtx.currentTime;
  const when = Math.max(now + 0.01, nextPlayAt);  // 10ms safety margin
  src.start(when);
  nextPlayAt = when + buf.duration;
}

function killPlayback() {
  if (playCtx && playCtx.state !== 'closed') {
    playCtx.close().catch(() => {});
  }
  playCtx       = null;
  gainNode      = null;
  nextPlayAt    = 0;
  agentSpeaking = false;
  setAgentSpeaking(false);
}

/* ── Sync agent-speaking state to worklet ─────────────────────────────────── */
function setAgentSpeaking(v) {
  agentSpeaking = v;
  if (workletNode) {
    workletNode.port.postMessage({ type: 'agent_speaking', v });
  }
  if (v) interruptSent = false;  // reset interrupt guard for new TTS burst
}

/* ── Waveform ─────────────────────────────────────────────────────────────── */
function startWave() {
  const data = new Uint8Array(analyserNode ? analyserNode.fftSize : 256);
  function draw() {
    rafId = requestAnimationFrame(draw);
    if (analyserNode) analyserNode.getByteTimeDomainData(data);
    cx.clearRect(0, 0, cvEl.width, cvEl.height);
    cx.beginPath();
    const sl = cvEl.width / data.length;
    let x = 0;
    for (let i = 0; i < data.length; i++) {
      const y = ((data[i] / 128) - 1) * (cvEl.height / 2) + cvEl.height / 2;
      i === 0 ? cx.moveTo(x, y) : cx.lineTo(x, y);
      x += sl;
    }
    cx.strokeStyle = agentSpeaking ? '#3b82f6' : '#22c55e';
    cx.lineWidth   = 1.5;
    cx.stroke();
  }
  draw();
}
function stopWave() {
  if (rafId) cancelAnimationFrame(rafId);
  cx.clearRect(0, 0, cvEl.width, cvEl.height);
}

/* ── WebSocket ────────────────────────────────────────────────────────────── */
function connectWS() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws/call`);
  ws.binaryType = 'arraybuffer';

  ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'call_start', language: currentLang }));
  };

  ws.onmessage = e => {
    // ── Binary frame = TTS PCM audio ──────────────────────────────────
    if (e.data instanceof ArrayBuffer) {
      if (!agentSpeaking) return;  // arrived after clear_queue, discard
      ensurePlayCtx();
      scheduleChunk(e.data);
      return;
    }

    // ── JSON control ──────────────────────────────────────────────────
    const msg = JSON.parse(e.data);

    switch (msg.type) {
      case 'call_accepted':
        setStatus('Connected', 'listen');
        break;

      case 'status':
        setStatus(msg.message,
          msg.message.includes('Transcrib') || msg.message.includes('Think') ? 'think' : 'listen');
        break;

      case 'transcript':
        addBubble('user', msg.user, msg.language);
        document.getElementById('meta').textContent =
          `${msg.chunks} chunks` + (msg.english !== msg.user
            ? '\n→ ' + msg.english.slice(0, 38) + (msg.english.length > 38 ? '…' : '')
            : '');
        break;

      case 'tts_start':
        setAgentSpeaking(true);
        ensurePlayCtx();
        setStatus('Speaking…', 'speak');
        break;

      case 'tts_end':
        setAgentSpeaking(false);
        if (callActive) setStatus('Listening…', 'listen');
        break;

      case 'clear_queue':
        killPlayback();
        if (callActive) setStatus('Listening…', 'listen');
        break;

      case 'call_ended':
        addBubble('agent', msg.message, currentLang);
        endCall(false);
        break;

      case 'error':
        sysMsg('⚠ ' + msg.message);
        if (callActive) setStatus('Listening…', 'listen');
        break;
    }
  };

  ws.onerror = () => sysMsg('WebSocket connection error — is the server running?');
  ws.onclose = () => { if (callActive) endCall(false); };
}

/* ── Microphone + AudioWorklet ────────────────────────────────────────────── */
async function startMic() {
  micStream = await navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl:  true,
      sampleRate:       48000,
    }
  });

  micCtx = new AudioContext({ sampleRate: 48000 });

  // Inject worklet via Blob URL — no static file needed
  const blob    = new Blob([WORKLET_SRC], { type: 'application/javascript' });
  const blobURL = URL.createObjectURL(blob);
  await micCtx.audioWorklet.addModule(blobURL);
  URL.revokeObjectURL(blobURL);

  const srcNode = micCtx.createMediaStreamSource(micStream);

  analyserNode = micCtx.createAnalyser();
  analyserNode.fftSize = 256;
  srcNode.connect(analyserNode);

  workletNode = new AudioWorkletNode(micCtx, 'mic-proc', {
    processorOptions: { targetSR: 16000 },
    channelCount:            1,
    channelCountMode:        'explicit',
    channelInterpretation:   'discrete',
  });
  srcNode.connect(workletNode);

  workletNode.port.onmessage = ({ data }) => {
    if (!callActive) return;

    if (data.type === 'energy') {
      // Update thin VAD-level bar at the top of waveform
      const pct = Math.min(100, data.v * 1200);
      document.getElementById('vad-fill').style.width = pct + '%';
      return;
    }

    if (data.type === 'pcm') {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(data.buf);   // zero-copy binary frame

        // BUG FIX: Interrupt only fires once per agent-speaking burst.
        // Previously fired on every 4096-sample chunk = floods the server.
        if (agentSpeaking && !interruptSent) {
          interruptSent = true;
          ws.send(JSON.stringify({ type: 'interrupt' }));
          killPlayback();
          setStatus('Listening…', 'listen');
        }
      }
      return;
    }

    if (data.type === 'vad_end') {
      if (ws && ws.readyState === WebSocket.OPEN && !agentSpeaking) {
        ws.send(JSON.stringify({ type: 'vad_end' }));
        setStatus('Processing…', 'think');
      }
      return;
    }

    if (data.type === 'vad_start') {
      if (!agentSpeaking) setStatus('Listening…', 'listen');
      return;
    }
  };

  startWave();
}

function stopMic() {
  if (workletNode)  { workletNode.disconnect(); workletNode  = null; }
  if (micCtx)       { micCtx.close().catch(() => {}); micCtx = null; }
  if (micStream)    { micStream.getTracks().forEach(t => t.stop()); micStream = null; }
  analyserNode = null;
  stopWave();
  document.getElementById('vad-fill').style.width = '0%';
}

/* ── Call control ─────────────────────────────────────────────────────────── */
async function toggleCall() {
  if (!callActive) await startCall();
  else             endCall(true);
}

async function startCall() {
  callActive = true;

  const btn = document.getElementById('cbtn');
  btn.textContent = '📵';
  btn.classList.add('on', 'pulse');

  // Clear conversation log
  const conv = document.getElementById('conv');
  conv.innerHTML = '';

  setStatus('Connecting…', '');
  connectWS();

  try {
    await startMic();
  } catch (err) {
    sysMsg('⚠ Microphone access denied: ' + err.message);
    endCall(true);
  }
}

function endCall(sendMsg) {
  callActive    = false;
  interruptSent = false;
  setAgentSpeaking(false);

  if (sendMsg && ws && ws.readyState === WebSocket.OPEN)
    ws.send(JSON.stringify({ type: 'call_end' }));
  else if (ws)
    ws.close();

  stopMic();
  killPlayback();

  const btn = document.getElementById('cbtn');
  btn.textContent = '📞';
  btn.classList.remove('on', 'pulse');

  setStatus('Call ended', '');
  document.getElementById('meta').textContent = '';
  setTimeout(() => setStatus('Ready — press 📞 to start', ''), 2500);
}
</script>
</body>
</html>"""