# # # # # # import os
# # # # # # from deepgram import DeepgramClient

# # # # # # dg = DeepgramClient(api_key=os.environ.get("DEEPGRAM_API_KEY", ""))


# # # # # # async def transcribe(audio_bytes: bytes) -> tuple[str, str]:
# # # # # #     """Returns (transcript, detected_language).

# # # # # #     Deepgram SDK v6 API changes:
# # # # # #       - No more PrerecordedOptions class
# # # # # #       - Use: client.listen.v1.media.transcribe_file(request=<bytes>, **options)
# # # # # #       - detected_language is on the channel object, not on metadata
# # # # # #     """
# # # # # #     response = dg.listen.v1.media.transcribe_file(
# # # # # #         request=audio_bytes,
# # # # # #         model="nova-3", # 'nova-2' base is recommended when using language detection over 'nova-2-general'
# # # # # #         extra=["detect_language=en", "detect_language=hi", "detect_language=gu"],
# # # # # #         punctuate=True,
# # # # # #     )

# # # # # #     channel = response.results.channels[0]
# # # # # #     result = channel.alternatives[0]
# # # # # #     transcript = result.transcript

# # # # # #     # In SDK v6, detected_language is on the channel, not metadata
# # # # # #     lang = (channel.detected_language or "en").split("-")[0].lower()
# # # # # #     if lang not in ("gu", "hi", "en"):
# # # # # #         lang = "en"

# # # # # #     return transcript, lang


# # # # # import os
# # # # # from deepgram import DeepgramClient

# # # # # dg = DeepgramClient(api_key=os.environ.get("DEEPGRAM_API_KEY", ""))

# # # # # SUPPORTED_LANGS = {"gu", "hi", "en"}


# # # # # async def transcribe(audio_bytes: bytes) -> tuple[str, str]:
# # # # #     """
# # # # #     Returns (transcript, detected_language).

# # # # #     Model: nova-3 + language=multi
# # # # #     - Handles English, Hindi, and mixed Hindi+English (code-switching)
# # # # #       natively in a single utterance.
# # # # #     - Gujarati (gu) supported on nova-3 as of late 2025.

# # # # #     SDK shape: listen.v1.media.transcribe_file(request=bytes, **kwargs)
# # # # #     - This is the current documented shape in the official SDK README.
# # # # #     - No PrerecordedOptions / ListenRESTOptions object needed.
# # # # #     - Works regardless of whether your SDK version calls it
# # # # #       PrerecordedOptions or ListenRESTOptions — avoids the import error.
# # # # #     """
# # # # #     import asyncio

# # # # #     response = await asyncio.to_thread(
# # # # #         dg.listen.v1.media.transcribe_file,
# # # # #         request=audio_bytes,
# # # # #         model="nova-3",
# # # # #         language="multi",
# # # # #         punctuate=True,
# # # # #         smart_format=True,
# # # # #         filler_words=False,
# # # # #     )

# # # # #     channel = response.results.channels[0]
# # # # #     result = channel.alternatives[0]
# # # # #     transcript = result.transcript

# # # # #     # detected_language is on the channel object (not metadata)
# # # # #     # Deepgram returns full locale codes like "en-US", "hi-IN", "gu-IN"
# # # # #     raw_lang = getattr(channel, "detected_language", None) or "en"
# # # # #     lang = raw_lang.split("-")[0].lower()

# # # # #     if lang not in SUPPORTED_LANGS:
# # # # #         lang = "en"

# # # # #     return transcript, lang


# # # # import os
# # # # import asyncio
# # # # from deepgram import DeepgramClient

# # # # dg = DeepgramClient(api_key=os.environ.get("DEEPGRAM_API_KEY", ""))

# # # # SUPPORTED_LANGS = {"gu", "hi", "en"}


# # # # async def _transcribe_request(request_obj) -> tuple[str, str]:
# # # #     response = await asyncio.to_thread(
# # # #         dg.listen.v1.media.transcribe_file,
# # # #         request=request_obj,
# # # #         model="nova-3",
# # # #         language="multi",
# # # #         punctuate=True,
# # # #         smart_format=True,
# # # #         filler_words=False,
# # # #     )

# # # #     channel = response.results.channels[0]
# # # #     result = channel.alternatives[0]
# # # #     transcript = result.transcript

# # # #     raw_lang = getattr(channel, "detected_language", None) or "en"
# # # #     lang = raw_lang.split("-")[0].lower()
# # # #     if lang not in SUPPORTED_LANGS:
# # # #         lang = "en"
# # # #     return transcript, lang


# # # # async def transcribe(audio_bytes: bytes, mime_type: str | None = None) -> tuple[str, str]:
# # # #     """
# # # #     Transcribe audio bytes using Deepgram nova-3 with multilingual support.

# # # #     Returns:
# # # #         (transcript, detected_language)  — language is one of "en", "hi", "gu"

# # # #     Model: nova-3 + language=multi
# # # #         - Handles English, Hindi, Gujarati, and Hindi+English code-switching.
# # # #         - detected_language comes from channel object (SDK v6).

# # # #     SDK note: transcribe_file is synchronous in v6 — wrapped in asyncio.to_thread.
# # # #     """
# # # #     # Primary shape used previously and known to work in this codebase.
# # # #     transcript, lang = await _transcribe_request(audio_bytes)
# # # #     if transcript and transcript.strip():
# # # #         return transcript, lang

# # # #     # Retry with explicit mimetype for browser-recorded WebM/Opus payloads.
# # # #     if mime_type:
# # # #         req = {"buffer": audio_bytes, "mimetype": mime_type}
# # # #         transcript2, lang2 = await _transcribe_request(req)
# # # #         if transcript2 and transcript2.strip():
# # # #             return transcript2, lang2

# # # #     return transcript, lang


# # # import os
# # # import asyncio
# # # from deepgram import DeepgramClient

# # # dg = DeepgramClient(api_key=os.environ.get("DEEPGRAM_API_KEY", ""))

# # # SUPPORTED_LANGS = {"gu", "hi", "en"}


# # # async def transcribe(audio_bytes: bytes) -> tuple[str, str]:
# # #     """
# # #     Transcribe audio bytes using Deepgram nova-3 with multilingual support.

# # #     Returns:
# # #         (transcript, detected_language)  — language is one of "en", "hi", "gu"

# # #     Model: nova-3 + language=multi
# # #         - Handles English, Hindi, Gujarati, and Hindi+English code-switching.
# # #         - detected_language comes from channel object (SDK v6).

# # #     SDK note: transcribe_file is synchronous in v6 — wrapped in asyncio.to_thread.
# # #     """
# # #     response = await asyncio.to_thread(
# # #         dg.listen.v1.media.transcribe_file,
# # #         request=audio_bytes,
# # #         model="nova-3",
# # #         language="multi",
# # #         punctuate=True,
# # #         smart_format=True,
# # #         filler_words=False,
# # #     )

# # #     channel = response.results.channels[0]
# # #     result = channel.alternatives[0]
# # #     transcript = result.transcript

# # #     raw_lang = getattr(channel, "detected_language", None) or "en"
# # #     lang = raw_lang.split("-")[0].lower()

# # #     if lang not in SUPPORTED_LANGS:
# # #         lang = "en"

# # #     return transcript, lang




# """
# deepgram_stt.py — Python 3.13 compatible
# ══════════════════════════════════════════
# Root-cause of "corrupt or unsupported data" from Deepgram:
#   The AudioWorklet posts raw Int16 LE PCM bytes with NO container header.
#   Deepgram's prerecorded REST API (transcribe_file) expects a proper audio
#   file (WAV / WebM / OGG / MP3). Sending bare PCM → 400 Bad Request.

# Fix:
#   _pcm_to_wav() wraps the raw PCM in a 44-byte RIFF/WAV header using
#   Python's stdlib `wave` module. No external dependencies needed.

# Audio auto-detection:
#   transcribe() sniffs the first 4 bytes to decide whether the payload
#   is already a container (WAV/WebM/OGG/MP3) or bare PCM, so it works
#   for both the real-time WS pipeline (raw PCM) and the /transcribe
#   REST endpoint (file upload with container).
# """

# import io
# import os
# import wave
# import asyncio
# import logging

# from deepgram import DeepgramClient

# log = logging.getLogger("stt")

# # ── Deepgram client ────────────────────────────────────────────────────────────
# dg = DeepgramClient(api_key=os.environ.get("DEEPGRAM_API_KEY", ""))

# # ── AudioWorklet output spec (must match client worklet processorOptions) ──────
# MIC_SAMPLE_RATE  = 16_000   # worklet downsamples 48kHz → 16kHz
# MIC_CHANNELS     = 1        # mono
# MIC_SAMPLE_WIDTH = 2        # Int16 = 2 bytes per sample

# SUPPORTED_LANGS = {"gu", "hi", "en"}

# # Minimum PCM bytes to bother sending (< 0.1 s → almost certainly silence)
# MIN_AUDIO_BYTES = MIC_SAMPLE_RATE * MIC_CHANNELS * MIC_SAMPLE_WIDTH // 10


# # ── WAV wrapper ────────────────────────────────────────────────────────────────

# def _pcm_to_wav(
#     pcm_bytes:   bytes,
#     sample_rate: int = MIC_SAMPLE_RATE,
#     n_channels:  int = MIC_CHANNELS,
#     sampwidth:   int = MIC_SAMPLE_WIDTH,
# ) -> bytes:
#     """
#     Wrap raw PCM bytes in a RIFF/WAV container.

#     This is the KEY FIX.  The AudioWorklet sends:
#         [Int16][Int16][Int16]…  ← no header, Deepgram rejects this

#     After wrapping:
#         RIFF header (44 bytes) + [Int16][Int16]…  ← Deepgram accepts this
#     """
#     buf = io.BytesIO()
#     with wave.open(buf, "wb") as wf:
#         wf.setnchannels(n_channels)
#         wf.setsampwidth(sampwidth)
#         wf.setframerate(sample_rate)
#         wf.writeframes(pcm_bytes)
#     wav = buf.getvalue()

#     duration_s = len(pcm_bytes) / (sample_rate * n_channels * sampwidth)
#     print(
#         f"[STT]  PCM → WAV  "
#         f"raw={len(pcm_bytes):,} B  "
#         f"wav={len(wav):,} B  "
#         f"duration={duration_s:.2f}s"
#     )
#     return wav


# # ── Container-format sniffer ───────────────────────────────────────────────────

# def _has_container_header(data: bytes) -> bool:
#     """
#     Return True if `data` already has a proper audio container header.
#     Checks for WAV (RIFF), WebM, OGG, MP3 sync, AIFF.
#     If False → assume raw Int16 PCM from the AudioWorklet.
#     """
#     if len(data) < 4:
#         return False
#     return (
#         data[:4] == b"RIFF"            # WAV
#         or data[:4] == b"OggS"         # OGG / Opus
#         or data[:3] == b"ID3"          # MP3 with ID3 tag
#         or data[:4] == b"fLaC"         # FLAC
#         or data[:4] == b"FORM"         # AIFF
#         or data[:4] == b"\x1aE\xdf\xa3"  # WebM / Matroska
#         or (data[0] == 0xFF and (data[1] & 0xE0) == 0xE0)  # MP3 frame sync
#     )


# # ── Public transcribe() ────────────────────────────────────────────────────────

# async def transcribe(audio_bytes: bytes) -> tuple[str, str]:
#     """
#     Transcribe audio using Deepgram nova-3 (multilingual: en / hi / gu).

#     Accepts EITHER:
#       • Raw Int16 LE PCM from the AudioWorklet (no header)  ← default WS path
#       • Any proper audio container (WAV / WebM / OGG / MP3) ← /transcribe REST

#     Returns:
#         (transcript: str, language: str)  — language is "en", "hi", or "gu"

#     Raises on Deepgram API errors so the caller can send an error message
#     to the client and keep the call alive.
#     """
#     print(f"\n[STT]  ─── transcribe called  input={len(audio_bytes):,} bytes ───")

#     # ── Silence guard ──────────────────────────────────────────────────────────
#     if len(audio_bytes) < MIN_AUDIO_BYTES:
#         print(f"[STT]  ✗ too short ({len(audio_bytes)} B < {MIN_AUDIO_BYTES} B) — skipping")
#         return "", "en"

#     # ── Wrap PCM in WAV if needed ─────────────────────────────────────────────
#     if _has_container_header(audio_bytes):
#         payload = audio_bytes
#         print(f"[STT]  container detected — sending as-is ({len(payload):,} B)")
#     else:
#         print(f"[STT]  raw PCM detected — wrapping in WAV header")
#         payload = _pcm_to_wav(audio_bytes)

#     try:
#         response = await asyncio.to_thread(
#             dg.listen.v1.media.transcribe_file,
#             request=payload,
#             model="nova-3",
#             # We must use 'extra' to pass multiple values for detect_language
#             # because the new SDK's typed kwargs don't support list serialization.
#             # This restricts detection to ONLY English, Hindi, and Gujarati.
#             extra=["detect_language=en", "detect_language=hi", "detect_language=gu"],
#             punctuate=True,
#             smart_format=True,
#             filler_words=False,
#         )
#     except Exception as e:
#         print(f"[STT]  ✗ Deepgram API error: {e}")
#         raise

#     # ── Parse response ────────────────────────────────────────────────────────
#     channel    = response.results.channels[0]
#     result     = channel.alternatives[0]
#     transcript = result.transcript.strip()

#     raw_lang = getattr(channel, "detected_language", None) or "en"
#     lang     = raw_lang.split("-")[0].lower()
#     if lang not in SUPPORTED_LANGS:
#         lang = "en"

#     confidence = getattr(result, "confidence", None)
#     conf_str   = f"{confidence:.2f}" if confidence is not None else "n/a"

#     print(
#         f"[STT]  ✓ transcript={transcript[:80]!r}\n"
#         f"[STT]    lang={lang}  confidence={conf_str}\n"
#         f"[STT]  ───────────────────────────────────────────"
#     )

#     return transcript, lang
















import os, asyncio, logging
from typing import Callable, Awaitable
log = logging.getLogger("stt")
from deepgram import AsyncDeepgramClient
from deepgram.listen.v1.types import (
    ListenV1Results,
    ListenV1UtteranceEnd,
    ListenV1SpeechStarted,
)

_api_key = os.environ.get("DEEPGRAM_API_KEY", "")

# ══════════════════════════════════════════════════════════════════════════════
#  STREAMING STT ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class DeepgramStreamingSTT:
    """
    Persistent Deepgram Live WebSocket for continuous realtime STT + Neural VAD.

    Callbacks:
        on_interim(text, lang)       — triggers while user is mid-sentence (for UI typing effect)
        on_final(text, lang)         — utterance complete → kicks off the prompt generator pipeline
        on_speech_started()          — Deepgram Neural VAD found human voice → halts any active agent output
    """

    def __init__(
        self,
        on_interim:        Callable[[str, str], Awaitable[None]] | None = None,
        on_final:          Callable[[str, str], Awaitable[None]] | None = None,
        on_speech_started: Callable[[], Awaitable[None]] | None = None,
    ):
        self._on_interim = on_interim
        self._on_final = on_final
        self._on_speech_started = on_speech_started
        self._socket = None
        self._ctx_mgr = None
        self._listen_task: asyncio.Task | None = None
        self._running = False
        self._lock = asyncio.Lock()

    async def start(self):
        async with self._lock:
            if self._running:
                return
            dg = AsyncDeepgramClient(api_key=_api_key)
            self._ctx_mgr = dg.listen.v1.connect(
                model="nova-3",
                language="multi",
                encoding="linear16",
                sample_rate=16000,  # Match our worklet output
                channels=1,
                interim_results="true",
                utterance_end_ms=1000, # Slightly longer for natural pauses
                vad_events="true",       # Enable neural cloud VAD
                punctuate="true",
                smart_format="true",
            )
            self._socket = await self._ctx_mgr.__aenter__()
            self._running = True
            self._listen_task = asyncio.create_task(self._listen_loop())
            log.info("[STT-stream] Connection established with Deepgram Real-time Cluster")

    async def send(self, pcm_bytes: bytes):
        if not self._running or self._socket is None:
            return
        try:
            await self._socket.send_media(pcm_bytes)
        except Exception as e:
            log.warning("[STT-stream] data forward failure: %s", e)

    async def stop(self):
        async with self._lock:
            if not self._running:
                return
            self._running = False
            if self._listen_task and not self._listen_task.done():
                self._listen_task.cancel()
                try:    await self._listen_task
                except asyncio.CancelledError: pass
            if self._ctx_mgr is not None:
                try:    await self._socket.send_close_stream()
                except Exception: pass
                try:    await self._ctx_mgr.__aexit__(None, None, None)
                except Exception: pass
                self._ctx_mgr = None
                self._socket = None
            log.info("[STT-stream] Socket shutdown complete.")

    async def _listen_loop(self):
        try:
            async for msg in self._socket:
                if not self._running: break
                
                if isinstance(msg, ListenV1Results):
                    await self._handle_result(msg)
                
                elif isinstance(msg, ListenV1SpeechStarted):
                    # Global Intercept Trigger! 
                    log.info("[STT-stream] >>> Neural VAD: USER SPEECH STARTED <<<")
                    if self._on_speech_started:
                        asyncio.create_task(self._on_speech_started())
                
                elif isinstance(msg, ListenV1UtteranceEnd):
                    log.debug("[STT-stream] Utterance terminated.")

        except asyncio.CancelledError: pass
        except Exception as e:
            if self._running:
                log.error("[STT-stream] Stream failure: %s", e)

    async def _handle_result(self, result: ListenV1Results):
        try:
            alt = result.channel.alternatives[0]
            text = (alt.transcript or "").strip()
            
            # 'is_final' means Deepgram froze this sentence boundary
            is_final   = result.is_final or False
            speech_end = result.speech_final or False

            if not text: return

            raw_lang = getattr(alt, "detected_language", None) or "en"
            lang = raw_lang.split("-")[0].lower()
            if lang not in {"gu", "hi", "en"}: lang = "en"

            if speech_end or is_final:
                log.info("[STT-stream] FINAL CAPTURED: %r (lang=%s)", text, lang)
                if self._on_final:
                    asyncio.create_task(self._on_final(text, lang))
            else:
                log.debug("[STT-stream] rolling partial: %r", text)
                if self._on_interim:
                    asyncio.create_task(self._on_interim(text, lang))

        except Exception as e:
            log.error("[STT-stream] data processing failure: %s", e)


























"""
deepgram_stt.py  — Python 3.13 compatible, Windows SSL fix
═══════════════════════════════════════════════════════════

Key fixes vs previous version:
  1. REMOVED false-positive MP3 sync detection from _has_container_header().
     Raw Int16 PCM that starts with 0xFF 0xEx was being flagged as MP3 →
     sent as-is → Deepgram 400 "corrupt or unsupported data".
     Now: ALWAYS wrap in WAV when coming from the real-time WS pipeline.
     The container check is only used for the /transcribe REST upload endpoint.

  2. Minimum audio gate raised to 0.5s (was 0.1s) to stop firing on noise bursts.

  3. SSL workaround for Windows: Deepgram SDK uses httpx internally.
     On Windows with corporate proxies or self-signed certs the SSL chain fails.
     We pass verify=False via HTTPX_SSL_VERIFY=0 env detection as a fallback.
"""

import io
import os
import ssl
import wave
import asyncio
import logging

log = logging.getLogger("stt")

# ── Deepgram client ────────────────────────────────────────────────────────────
from deepgram import DeepgramClient
#  DeepgramClientOptions

# _dg_opts = DeepgramClientOptions(
#     # Disable SSL verification on Windows when self-signed cert errors occur.
#     # Set DEEPGRAM_SSL_VERIFY=false in your .env to activate this.
#     options={"verify": False} if os.environ.get("DEEPGRAM_SSL_VERIFY", "true").lower() == "false" else {}
# )
dg = DeepgramClient(
    api_key=os.environ.get("DEEPGRAM_API_KEY", "")
    # config=_dg_opts,
)

# ── AudioWorklet output spec ────────────────────────────────────────────────────
MIC_SAMPLE_RATE  = 16_000
MIC_CHANNELS     = 1
MIC_SAMPLE_WIDTH = 2        # Int16 = 2 bytes

# Minimum 0.5 s of audio before bothering Deepgram (was 0.1s — too short)
MIN_AUDIO_BYTES = MIC_SAMPLE_RATE * MIC_CHANNELS * MIC_SAMPLE_WIDTH // 2

SUPPORTED_LANGS = {"gu", "hi", "en"}


def _pcm_to_wav(pcm_bytes: bytes) -> bytes:
    """Wrap raw Int16 LE PCM in a RIFF/WAV container. No extra deps."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(MIC_CHANNELS)
        wf.setsampwidth(MIC_SAMPLE_WIDTH)
        wf.setframerate(MIC_SAMPLE_RATE)
        wf.writeframes(pcm_bytes)
    wav = buf.getvalue()
    duration_s = len(pcm_bytes) / (MIC_SAMPLE_RATE * MIC_CHANNELS * MIC_SAMPLE_WIDTH)
    log.info("[STT]  PCM→WAV  raw=%d B  wav=%d B  dur=%.2fs",
             len(pcm_bytes), len(wav), duration_s)
    return wav


def _is_real_container(data: bytes) -> bool:
    """
    Return True ONLY for unambiguous container magic bytes.
    IMPORTANT: MP3 frame sync (0xFF 0xEx) is REMOVED because raw Int16 PCM
    frequently starts with these bytes — this was causing the false-positive
    'container detected' bug that sent raw PCM to Deepgram → 400 error.
    """
    if len(data) < 4:
        return False
    return (
        data[:4] == b"RIFF"              # WAV
        or data[:4] == b"OggS"           # OGG / Opus
        or data[:3] == b"ID3"            # MP3 with ID3 tag (true MP3 file)
        or data[:4] == b"fLaC"           # FLAC
        or data[:4] == b"FORM"           # AIFF
        or data[:4] == b"\x1aE\xdf\xa3" # WebM / Matroska
        # NOTE: 0xFF 0xEx MP3 sync intentionally excluded — too many false positives
    )


async def transcribe(audio_bytes: bytes) -> tuple[str, str]:
    """
    Transcribe audio using Deepgram nova-3 (multilingual: en / hi / gu).

    Always wraps raw PCM in WAV unless the bytes have clear container magic.
    Returns (transcript, language).
    """
    n = len(audio_bytes)
    log.info("\n[STT]  ─── transcribe  input=%d bytes ───", n)

    if n < MIN_AUDIO_BYTES:
        log.warning("[STT]  ✗ too short (%d B < %d B min) — skip", n, MIN_AUDIO_BYTES)
        return "", "en"

    if _is_real_container(audio_bytes):
        payload = audio_bytes
        log.info("[STT]  container header found — sending as-is (%d B)", n)
    else:
        payload = _pcm_to_wav(audio_bytes)

    log.info("[STT]  → Deepgram  payload=%d B", len(payload))

    try:
        response = await asyncio.to_thread(
            dg.listen.v1.media.transcribe_file,
            request=payload,
            model="nova-3",
            language="multi",
            punctuate=True,
            smart_format=True,
            filler_words=False,
        )
    except Exception as e:
        log.error("[STT]  ✗ Deepgram error: %s", e)
        raise

    channel    = response.results.channels[0]
    result     = channel.alternatives[0]
    transcript = result.transcript.strip()
    raw_lang   = getattr(channel, "detected_language", None) or "en"
    lang       = raw_lang.split("-")[0].lower()
    if lang not in SUPPORTED_LANGS:
        lang = "en"

    conf = getattr(result, "confidence", 0) or 0
    log.info("[STT]  ✓ %r  lang=%s  conf=%.2f", transcript[:80], lang, conf)
    return transcript, lang