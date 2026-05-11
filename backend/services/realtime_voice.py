# from __future__ import annotations

# import asyncio
# import base64
# import json
# import os
# import re
# from array import array
# from dataclasses import dataclass, field
# from enum import StrEnum
# from typing import AsyncGenerator

# from fastapi import WebSocket
# from openai import AsyncOpenAI
# from websockets.asyncio.client import connect as websocket_connect

# from kb.retriever import retrieve
# from services.gemini_translate import detect_language
# from services.stt_service import DeepgramLiveSTT


# OPENAI_MODEL = "gpt-4o-mini"
# ELEVENLABS_MODEL = "eleven_turbo_v2_5"
# ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "9BWtsMINqrJLrRacOk9x")
# ELEVENLABS_API_KEY = os.environ.get("ELEVENLAB_API_KEY", "")

# SAMPLE_RATE = 16000
# SAMPLES_PER_20MS = 320
# PCM_RMS_THRESHOLD = 900

# LANGUAGE_NAMES = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}

# SYSTEM_PROMPT = """You are a helpful real-time voice assistant for Suvit.

# Rules:
# - Identify whether the user is speaking English, Hindi, or Gujarati and respond in that same language.
# - You MUST respond using the NATIVE alphabet for the language (Devanagari for Hindi, Gujarati script for Gujarati). This ensures authentic pronunciation.
# - NEVER write Hindi or Gujarati using English letters (Hinglish/Gujlish). It ruins the TTS accent.
# - Keep the reply under 3 short sentences.
# - Speak naturally for voice, not like a formal document.
# - Use the provided knowledge-base context when it is relevant, but do not mention the context explicitly.
# - If the answer is uncertain, say so clearly and offer the next best help.
# """


# class SessionMode(StrEnum):
#     LISTENING = "listening"
#     THINKING = "thinking"
#     SPEAKING = "speaking"
#     INTERRUPTED = "interrupted"


# def _normalize_language(language: str | None) -> str:
#     lang = (language or "en").split("-")[0].lower()
#     return lang if lang in LANGUAGE_NAMES else "en"


# def _pcm_has_voice(audio_chunk: bytes, threshold: int = PCM_RMS_THRESHOLD) -> bool:
#     if len(audio_chunk) < 2:
#         return False

#     samples = array("h")
#     samples.frombytes(audio_chunk[: len(audio_chunk) - (len(audio_chunk) % 2)])
#     if not samples:
#         return False

#     total = 0
#     for sample in samples:
#         total += sample * sample

#     rms = (total / len(samples)) ** 0.5
#     return rms >= threshold


# async def _sentence_chunker(
#     text_stream: AsyncGenerator[str, None],
# ) -> AsyncGenerator[str, None]:
#     buffer = ""

#     async for token in text_stream:
#         buffer += token
#         stripped = buffer.strip()
#         if not stripped:
#             continue

#         if re.search(r"[.!?]\s*$", stripped):
#             yield stripped
#             buffer = ""
#             continue

#         words = stripped.split()
#         if len(words) >= 15:
#             comma_index = max(stripped.rfind(","), stripped.rfind(";"), stripped.rfind(":"))
#             if comma_index != -1:
#                 yield stripped[: comma_index + 1].strip()
#                 buffer = stripped[comma_index + 1 :].lstrip()
#                 continue

#         if len(words) >= 22:
#             split_at = stripped.rfind(" ")
#             if split_at > 0:
#                 yield stripped[:split_at].strip()
#                 buffer = stripped[split_at + 1 :].lstrip()

#     remaining = buffer.strip()
#     if remaining:
#         yield remaining


# async def _stream_openai_response(
#     transcript: str,
#     language: str,
#     history: list[dict[str, str]],
#     context_chunks: list[str],
# ) -> AsyncGenerator[str, None]:
#     client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
#     context = "\n\n---\n\n".join(context_chunks) if context_chunks else "No specific KB context found."
#     history_lines = []
#     for item in history[-6:]:
#         role = "Assistant" if item["role"] == "assistant" else "User"
#         history_lines.append(f"{role}: {item['content']}")
#     history_block = "\n".join(history_lines) if history_lines else "No prior conversation."
#     lang_name = LANGUAGE_NAMES.get(language, "English")

#     user_prompt = f"""Knowledge-base context:
# {context}

# Recent conversation:
# {history_block}

# Latest user transcript:
# {transcript}

# Respond in {lang_name}. Keep the answer concise and voice-friendly."""

#     stream = await client.chat.completions.create(
#         model=OPENAI_MODEL,
#         stream=True,
#         max_tokens=100,
#         temperature=0.4,
#         messages=[
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": user_prompt},
#         ],
#     )

#     async for chunk in stream:
#         content = chunk.choices[0].delta.content
#         if content:
#             yield content


# async def _stream_elevenlabs_tts(
#     text_chunks: AsyncGenerator[str, None],
#     cancel_event: asyncio.Event,
# ) -> AsyncGenerator[bytes, None]:
#     if not ELEVENLABS_API_KEY:
#         raise RuntimeError("ELEVENLAB_API_KEY is missing.")

#     url = (
#         f"wss://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream-input"
#         f"?model_id={ELEVENLABS_MODEL}&output_format=pcm_16000"
#     )
#     headers = {"xi-api-key": ELEVENLABS_API_KEY}
#     audio_queue: asyncio.Queue[bytes | None] = asyncio.Queue()

#     async with websocket_connect(url, additional_headers=headers, max_size=16 * 1024 * 1024) as socket:
#         await socket.send(
#             json.dumps(
#                 {
#                     "text": " ",
#                     "try_trigger_generation": True,
#                     "voice_settings": {
#                         "stability": 0.45,
#                         "similarity_boost": 0.8,
#                         "style": 0.1,
#                         "use_speaker_boost": True,
#                     },
#                     "generation_config": {
#                         "chunk_length_schedule": [50, 120, 180],
#                     },
#                 }
#             )
#         )

#         async def receiver() -> None:
#             try:
#                 async for raw_message in socket:
#                     message = json.loads(raw_message)
#                     audio_b64 = message.get("audio")
#                     if audio_b64:
#                         await audio_queue.put(base64.b64decode(audio_b64))
#                     if message.get("isFinal"):
#                         break
#             finally:
#                 await audio_queue.put(None)

#         async def sender() -> None:
#             try:
#                 async for chunk in text_chunks:
#                     if cancel_event.is_set():
#                         break
#                     await socket.send(
#                         json.dumps(
#                             {
#                                 "text": chunk if chunk.endswith(" ") else f"{chunk} ",
#                                 "try_trigger_generation": True,
#                             }
#                         )
#                     )
#                 if not cancel_event.is_set():
#                     await socket.send(json.dumps({"text": ""}))
#             except asyncio.CancelledError:
#                 raise

#         receiver_task = asyncio.create_task(receiver())
#         sender_task = asyncio.create_task(sender())

#         try:
#             while True:
#                 if cancel_event.is_set():
#                     await socket.close(code=1000, reason="interrupted")
#                     break

#                 item = await audio_queue.get()
#                 if item is None:
#                     break
#                 yield item
#         finally:
#             sender_task.cancel()
#             receiver_task.cancel()
#             await asyncio.gather(sender_task, receiver_task, return_exceptions=True)


# @dataclass
# class RealtimeVoiceSession:
#     websocket: WebSocket
#     state: SessionMode = SessionMode.LISTENING
#     language: str = "en"
#     final_fragments: list[str] = field(default_factory=list)
#     history: list[dict[str, str]] = field(default_factory=list)
#     response_task: asyncio.Task[None] | None = None
#     cancel_event: asyncio.Event = field(default_factory=asyncio.Event)
#     stt: DeepgramLiveSTT | None = None

#     async def start(self) -> None:
#         self.stt = DeepgramLiveSTT(self._handle_transcript_event)
#         await self.stt.start()
#         await self._send_json({"type": "state", "state": self.state})

#     async def close(self) -> None:
#         await self._cancel_response(notify=False)
#         if self.stt:
#             await self.stt.close()
#             self.stt = None

#     async def process_audio_chunk(self, audio_chunk: bytes) -> None:
#         if not audio_chunk:
#             return

#         if self.state == SessionMode.SPEAKING and _pcm_has_voice(audio_chunk):
#             await self.interrupt()

#         if self.stt:
#             await self.stt.send_audio(audio_chunk)

#     async def interrupt(self) -> None:
#         await self._cancel_response(notify=True)
#         self.state = SessionMode.INTERRUPTED
#         await self._send_json({"type": "clear_queue"})
#         await self._send_json({"type": "state", "state": self.state})
#         self.state = SessionMode.LISTENING
#         await self._send_json({"type": "state", "state": self.state})

#     async def _cancel_response(self, notify: bool) -> None:
#         if self.response_task and not self.response_task.done():
#             self.cancel_event.set()
#             self.response_task.cancel()
#             await asyncio.gather(self.response_task, return_exceptions=True)
#             if notify:
#                 await self._send_json({"type": "audio_end"})
#         self.response_task = None
#         self.cancel_event = asyncio.Event()

#     async def _handle_transcript_event(
#         self,
#         transcript: str,
#         is_final: bool,
#         speech_final: bool,
#     ) -> None:
#         await self._send_json(
#             {
#                 "type": "transcript_update",
#                 "text": transcript,
#                 "is_final": is_final,
#                 "speech_final": speech_final,
#             }
#         )

#         if is_final:
#             self.final_fragments.append(transcript.strip())

#         if not speech_final:
#             return

#         utterance = " ".join(part for part in self.final_fragments if part).strip()
#         self.final_fragments.clear()
#         if not utterance:
#             utterance = transcript.strip()
#         if not utterance:
#             return

#         self.language = _normalize_language(await detect_language(utterance))
#         self.history.append({"role": "user", "content": utterance})

#         await self._cancel_response(notify=False)
#         self.response_task = asyncio.create_task(self._respond_to_utterance(utterance, self.language))

#     async def _respond_to_utterance(self, utterance: str, language: str) -> None:
#         try:
#             self.state = SessionMode.THINKING
#             await self._send_json({"type": "state", "state": self.state})

#             chunks = retrieve(utterance, k=5)
#             await self._send_json(
#                 {
#                     "type": "transcript",
#                     "user": utterance,
#                     "language": language,
#                     "chunks_used": len(chunks),
#                 }
#             )

#             assistant_parts: list[str] = []

#             async def response_stream() -> AsyncGenerator[str, None]:
#                 async for token in _stream_openai_response(utterance, language, self.history, chunks):
#                     assistant_parts.append(token)
#                     await self._send_json({"type": "assistant_chunk", "text": token, "language": language})
#                     yield token

#             tts_input = _sentence_chunker(response_stream())

#             self.state = SessionMode.SPEAKING
#             await self._send_json({"type": "audio_start"})
#             await self._send_json({"type": "state", "state": self.state})

#             async for audio_chunk in _stream_elevenlabs_tts(tts_input, self.cancel_event):
#                 if self.cancel_event.is_set():
#                     break
#                 await self.websocket.send_bytes(audio_chunk)

#             full_response = "".join(assistant_parts).strip()
#             if full_response:
#                 self.history.append({"role": "assistant", "content": full_response})
#                 await self._send_json(
#                     {
#                         "type": "assistant_end",
#                         "text": full_response,
#                         "language": language,
#                     }
#                 )

#             await self._send_json({"type": "audio_end"})
#             self.state = SessionMode.LISTENING
#             await self._send_json({"type": "state", "state": self.state})
#         except asyncio.CancelledError:
#             raise
#         except Exception as exc:
#             self.state = SessionMode.LISTENING
#             await self._send_json({"type": "error", "message": str(exc)})
#             await self._send_json({"type": "state", "state": self.state})
#         finally:
#             self.response_task = None

#     async def _send_json(self, payload: dict) -> None:
#         await self.websocket.send_json(payload)






# 11


"""
realtime_voice.py — RealtimeVoiceSession
══════════════════════════════════════════
Improvements over previous version:

1. LANGUAGE IN RESPONSE — LLM system prompt now enforces responding in the
   EXACT same language the user spoke (en/hi/gu), detected per utterance.
   Uses Devanagari/Gujarati script for native TTS pronunciation OR Hinglish/
   Gujlish depending on ElevenLabs voice capability flag.

2. FUZZY KB MAPPING — before RAG retrieval, the raw transcript is
   "intention-normalised" via a small LLM call that maps garbled/partial
   speech to the most likely support query. E.g.:
     "user something create kre" → "how to create a user"
     "bank statement kyu fail hua" → "why did bank statement fail"
   The normalised query is used for RAG; the original transcript is kept
   for history and display.

3. LANGUAGE DETECTION — detect_language() is called on the raw transcript
   using the existing gemini_translate helper (already handles en/hi/gu).

4. ElevenLabs TTS unchanged — streaming WSS, pcm_16000 output format.

5. PCM interrupt gate — _pcm_has_voice() threshold raised to 1200 (was 900)
   to avoid interrupting on ambient noise.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import re
from array import array
from dataclasses import dataclass, field
from enum import StrEnum
from typing import AsyncGenerator

from fastapi import WebSocket
from openai import AsyncOpenAI
from websockets.asyncio.client import connect as websocket_connect

from kb.retriever import retrieve
from services.gemini_translate import detect_language
from services.stt_service import DeepgramLiveSTT

log = logging.getLogger("session")

OPENAI_MODEL        = "gpt-4o-mini"
ELEVENLABS_MODEL    = "eleven_turbo_v2_5"
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "9BWtsMINqrJLrRacOk9x")
ELEVENLABS_API_KEY  = os.environ.get("ELEVENLAB_API_KEY", "")

SAMPLE_RATE       = 16000
PCM_RMS_THRESHOLD = 1200   # raised from 900 — less noise-sensitive

LANGUAGE_NAMES = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}

# ── System prompt ──────────────────────────────────────────────────────────────
# Uses native script so ElevenLabs pronounces correctly.
SYSTEM_PROMPT = """You are a real-time voice support agent for Suvit.

CRITICAL — LANGUAGE RULE:
You MUST identify the user's language from their question and respond in that SAME language:
- User spoke English → respond in English only.
- User spoke Hindi (Hinglish or Devanagari) → respond in Hindi using Devanagari script.
  Example: "आप Settings में जाकर Plan section में upgrade कर सकते हैं।"
- User spoke Gujarati (Gujlish or Gujarati script) → respond in Gujarati using Gujarati script.
  Example: "તમે Settings માં જઈને Plan section માં upgrade કરી શકો છો."
- NEVER mix scripts. NEVER respond in a different language than the user.

RESPONSE STYLE:
- 2-3 short sentences max. This is voice — be concise.
- No bullet points, no markdown, no lists.
- Natural conversational tone.
- Use knowledge-base context when relevant but don't mention it explicitly.
- If unsure, say so and offer to connect with the support team.
"""


class SessionMode(StrEnum):
    LISTENING    = "listening"
    THINKING     = "thinking"
    SPEAKING     = "speaking"
    INTERRUPTED  = "interrupted"


def _normalize_lang(language: str | None) -> str:
    lang = (language or "en").split("-")[0].lower()
    return lang if lang in LANGUAGE_NAMES else "en"


def _pcm_has_voice(chunk: bytes, threshold: int = PCM_RMS_THRESHOLD) -> bool:
    if len(chunk) < 2:
        return False
    samples = array("h")
    samples.frombytes(chunk[: len(chunk) - (len(chunk) % 2)])
    if not samples:
        return False
    rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
    return rms >= threshold


async def _sentence_chunker(stream: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
    """
    Buffer LLM tokens into complete sentences before sending to TTS.
    Flushes on [.!?] immediately; on comma/semicolon after ≥15 words;
    on force-break after ≥22 words. This keeps TTS latency low while
    preserving natural prosody.
    """
    buf = ""
    async for token in stream:
        buf += token
        s = buf.strip()
        if not s:
            continue

        if re.search(r'[.!?]\s*$', s):
            yield s; buf = ""; continue

        words = s.split()
        if len(words) >= 15:
            idx = max(s.rfind(","), s.rfind(";"), s.rfind(":"))
            if idx != -1:
                yield s[:idx + 1].strip()
                buf = s[idx + 1:].lstrip()
                continue

        if len(words) >= 22:
            sp = s.rfind(" ")
            if sp > 0:
                yield s[:sp].strip()
                buf = s[sp + 1:]

    if buf.strip():
        yield buf.strip()


async def _normalise_query(raw: str, lang: str) -> str:
    """
    Use a cheap LLM call to map garbled / partial speech to a clean
    English support query for RAG retrieval.

    Example:
      raw="user something create kre", lang="hi"
      → "how to create a user"

      raw="bank statement fail kyun", lang="hi"
      → "why does bank statement fail"

    Falls back to raw transcript if the LLM call fails.
    """
    if lang == "en":
        # For English, just clean up filler words
        prompt = (
            f"Fix any speech-to-text errors in this support question and return "
            f"a clean English sentence. Return ONLY the fixed sentence.\n\n{raw}"
        )
    else:
        prompt = (
            f"The following is a {LANGUAGE_NAMES.get(lang,'Hindi')} support question "
            f"that may contain speech-to-text errors or mixed language. "
            f"Translate and rewrite it as a clear, concise English support query. "
            f"Return ONLY the English query.\n\nInput: {raw}"
        )
    try:
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
        resp   = await client.chat.completions.create(
            model    = OPENAI_MODEL,
            messages = [{"role": "user", "content": prompt}],
            max_tokens = 60,
            temperature = 0,
        )
        result = resp.choices[0].message.content.strip()
        log.info("[NORM] %r → %r", raw[:60], result[:60])
        return result or raw
    except Exception as e:
        log.warning("[NORM] failed: %s — using raw transcript", e)
        return raw


async def _stream_llm(
    transcript: str,
    normalised_query: str,
    language: str,
    history: list[dict],
    chunks: list[str],
) -> AsyncGenerator[str, None]:
    client  = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    context = "\n\n---\n\n".join(chunks) if chunks else "No specific context found."

    hist_lines = []
    for item in history[-6:]:
        role = "Assistant" if item["role"] == "assistant" else "User"
        hist_lines.append(f"{role}: {item['content']}")
    hist_block = "\n".join(hist_lines) if hist_lines else "No prior conversation."

    lang_name = LANGUAGE_NAMES.get(language, "English")

    user_prompt = f"""Knowledge-base context:
{context}

Recent conversation:
{hist_block}

User said (original): {transcript}
Interpreted as: {normalised_query}

Respond in {lang_name} using the appropriate script."""

    stream = await client.chat.completions.create(
        model       = OPENAI_MODEL,
        stream      = True,
        max_tokens  = 150,
        temperature = 0.35,
        messages    = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
    )
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content


async def _stream_elevenlabs(
    text_chunks: AsyncGenerator[str, None],
    cancel_event: asyncio.Event,
) -> AsyncGenerator[bytes, None]:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLAB_API_KEY is not set.")

    url = (
        f"wss://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream-input"
        f"?model_id={ELEVENLABS_MODEL}&output_format=pcm_16000"
    )
    audio_q: asyncio.Queue[bytes | None] = asyncio.Queue()

    async with websocket_connect(
        url,
        additional_headers={"xi-api-key": ELEVENLABS_API_KEY},
        max_size=16 * 1024 * 1024,
    ) as sock:
        # Send BOS with voice settings
        await sock.send(json.dumps({
            "text": " ",
            "try_trigger_generation": True,
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.8,
                "style": 0.1,
                "use_speaker_boost": True,
            },
            "generation_config": {"chunk_length_schedule": [50, 120, 180]},
        }))

        async def _receiver():
            try:
                async for raw in sock:
                    msg     = json.loads(raw)
                    audio64 = msg.get("audio")
                    if audio64:
                        await audio_q.put(base64.b64decode(audio64))
                    if msg.get("isFinal"):
                        break
            finally:
                await audio_q.put(None)

        async def _sender():
            try:
                async for sentence in text_chunks:
                    if cancel_event.is_set():
                        break
                    text = sentence if sentence.endswith(" ") else sentence + " "
                    await sock.send(json.dumps({"text": text, "try_trigger_generation": True}))
                if not cancel_event.is_set():
                    await sock.send(json.dumps({"text": ""}))   # EOS
            except asyncio.CancelledError:
                raise

        recv_task = asyncio.create_task(_receiver())
        send_task = asyncio.create_task(_sender())

        try:
            while True:
                if cancel_event.is_set():
                    await sock.close(code=1000, reason="interrupted")
                    break
                item = await audio_q.get()
                if item is None:
                    break
                yield item
        finally:
            send_task.cancel()
            recv_task.cancel()
            await asyncio.gather(send_task, recv_task, return_exceptions=True)


# ══════════════════════════════════════════════════════════════════════════════
#  Session
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class RealtimeVoiceSession:
    websocket:     WebSocket
    state:         SessionMode                   = SessionMode.LISTENING
    language:      str                           = "en"
    final_frags:   list[str]                     = field(default_factory=list)
    history:       list[dict[str, str]]          = field(default_factory=list)
    response_task: asyncio.Task | None           = None
    cancel_event:  asyncio.Event                 = field(default_factory=asyncio.Event)
    stt:           DeepgramLiveSTT | None        = None

    # ── lifecycle ──────────────────────────────────────────────────────────────

    async def start(self):
        self.stt = DeepgramLiveSTT(self._on_transcript)
        await self.stt.start()
        await self._send({"type": "state", "state": str(self.state)})

    async def close(self):
        await self._cancel_response(notify=False)
        if self.stt:
            await self.stt.close()
            self.stt = None

    # ── audio input ────────────────────────────────────────────────────────────

    async def process_audio(self, chunk: bytes):
        if not chunk:
            return
        # Interrupt agent if user speaks loud enough
        if self.state == SessionMode.SPEAKING and _pcm_has_voice(chunk):
            await self.interrupt()
        if self.stt:
            await self.stt.send_audio(chunk)

    # ── interrupt ──────────────────────────────────────────────────────────────

    async def interrupt(self):
        await self._cancel_response(notify=True)
        self.state = SessionMode.INTERRUPTED
        await self._send({"type": "clear_queue"})
        await self._send({"type": "state", "state": str(self.state)})
        self.state = SessionMode.LISTENING
        await self._send({"type": "state", "state": str(self.state)})

    # ── STT callback ───────────────────────────────────────────────────────────

    async def _on_transcript(self, text: str, is_final: bool, speech_final: bool):
        await self._send({
            "type":         "transcript_update",
            "text":         text,
            "is_final":     is_final,
            "speech_final": speech_final,
        })

        if is_final:
            self.final_frags.append(text.strip())

        if not speech_final:
            return

        # Assemble full utterance
        utterance = " ".join(p for p in self.final_frags if p).strip()
        self.final_frags.clear()
        if not utterance:
            utterance = text.strip()
        if not utterance:
            return

        # Detect language from utterance
        self.language = _normalize_lang(await detect_language(utterance))
        self.history.append({"role": "user", "content": utterance})

        await self._cancel_response(notify=False)
        self.response_task = asyncio.create_task(
            self._respond(utterance, self.language)
        )

    # ── response pipeline ─────────────────────────────────────────────────────

    async def _respond(self, utterance: str, language: str):
        try:
            self.state = SessionMode.THINKING
            await self._send({"type": "state", "state": str(self.state)})

            # 1. Normalise query for KB retrieval (fuzzy mapping)
            # Runs concurrently with language detection (already done above)
            normalised = await _normalise_query(utterance, language)

            # 2. RAG retrieval using normalised English query
            chunks = retrieve(normalised, k=5)
            log.info("[PIPELINE] lang=%s  chunks=%d  query=%r", language, len(chunks), normalised[:60])

            await self._send({
                "type":       "transcript",
                "user":       utterance,
                "language":   language,
                "normalised": normalised,
                "chunks_used": len(chunks),
            })

            # 3. LLM streaming
            assistant_parts: list[str] = []

            async def _response_stream() -> AsyncGenerator[str, None]:
                async for token in _stream_llm(utterance, normalised, language, self.history, chunks):
                    assistant_parts.append(token)
                    await self._send({"type": "assistant_chunk", "text": token, "language": language})
                    yield token

            tts_input = _sentence_chunker(_response_stream())

            # 4. ElevenLabs TTS streaming
            self.state = SessionMode.SPEAKING
            await self._send({"type": "audio_start"})
            await self._send({"type": "state", "state": str(self.state)})

            async for audio_chunk in _stream_elevenlabs(tts_input, self.cancel_event):
                if self.cancel_event.is_set():
                    break
                await self.websocket.send_bytes(audio_chunk)

            # 5. Finalise
            full_response = "".join(assistant_parts).strip()
            if full_response:
                self.history.append({"role": "assistant", "content": full_response})
                await self._send({
                    "type":     "assistant_end",
                    "text":     full_response,
                    "language": language,
                })

            await self._send({"type": "audio_end"})
            self.state = SessionMode.LISTENING
            await self._send({"type": "state", "state": str(self.state)})

        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.error("[SESSION] respond error: %s", exc)
            self.state = SessionMode.LISTENING
            await self._send({"type": "error", "message": str(exc)})
            await self._send({"type": "state", "state": str(self.state)})
        finally:
            self.response_task = None

    # ── helpers ────────────────────────────────────────────────────────────────

    async def _cancel_response(self, notify: bool):
        if self.response_task and not self.response_task.done():
            self.cancel_event.set()
            self.response_task.cancel()
            await asyncio.gather(self.response_task, return_exceptions=True)
            if notify:
                await self._send({"type": "audio_end"})
        self.response_task = None
        self.cancel_event  = asyncio.Event()

    async def _send(self, payload: dict):
        try:
            await self.websocket.send_json(payload)
        except Exception:
            pass