# # """
# # sarvam_tts.py
# # ─────────────
# # Primary TTS: Sarvam AI Bulbul v3  (en-IN / hi-IN / gu-IN)
# # Fallback TTS: Microsoft edge-tts  (works offline, no API key needed)

# # Usage:
# #     from services.sarvam_tts import synthesize, synthesize_stream
# # """

# # import os
# # import httpx
# # import base64
# # import edge_tts

# # # ---------------------------------------------------------------------------
# # # Voice config
# # # ---------------------------------------------------------------------------

# # # Sarvam language codes
# # SARVAM_LANG_CODES = {
# #     "en": "en-IN",
# #     "hi": "hi-IN",
# #     "gu": "gu-IN",
# # }

# # # edge-tts neural voice fallbacks
# # EDGE_VOICES = {
# #     "en": "en-US-AriaNeural",
# #     "hi": "hi-IN-SwaraNeural",
# #     "gu": "gu-IN-DhwaniNeural",
# # }

# # # Sarvam speaker — "ishita" works well across all three languages
# # SARVAM_SPEAKER = "ishita"
# # SARVAM_MODEL = "bulbul:v3"
# # SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"


# # # ---------------------------------------------------------------------------
# # # Helpers
# # # ---------------------------------------------------------------------------


# # def _clean_text(text: str) -> str:
# #     """Strip markdown symbols that TTS engines mispronounce or skip."""
# #     if not text:
# #         return ""
# #     text = text.replace("**", "").replace("*", "")
# #     text = text.replace("__", "").replace("_", "")
# #     text = text.replace("#", "").replace("`", "")
# #     return text.strip()


# # async def _sarvam_synthesize(text: str, language: str) -> bytes:
# #     """
# #     Call the Sarvam AI Bulbul v3 REST API.
# #     Returns raw audio bytes (WAV) on success, raises on failure.
# #     """
# #     api_key = os.environ.get("SARVAMAI_API_KEY", "")
# #     if not api_key:
# #         raise ValueError("SARVAMAI_API_KEY is not set.")

# #     lang_code = SARVAM_LANG_CODES.get(language, "en-IN")

# #     payload = {
# #         "text": text,
# #         "target_language_code": lang_code,
# #         "speaker": SARVAM_SPEAKER,
# #         "model": SARVAM_MODEL,
# #     }
# #     headers = {
# #         "api-subscription-key": api_key,
# #         "Content-Type": "application/json",
# #     }

# #     async with httpx.AsyncClient(timeout=30.0) as client:
# #         resp = await client.post(SARVAM_TTS_URL, headers=headers, json=payload)

# #     if resp.status_code == 200:
# #         body = resp.json()
# #         audios = body.get("audios", [])
# #         if audios:
# #             return base64.b64decode(audios[0])

# #     raise ValueError(f"Sarvam TTS failed: HTTP {resp.status_code} — {resp.text[:200]}")


# # async def _edge_synthesize(text: str, language: str) -> bytes:
# #     """edge-tts fallback — returns full audio bytes."""
# #     voice = EDGE_VOICES.get(language, "en-US-AriaNeural")
# #     communicate = edge_tts.Communicate(text, voice)
# #     audio_data = bytearray()
# #     async for chunk in communicate.stream():
# #         if chunk["type"] == "audio":
# #             audio_data.extend(chunk["data"])
# #     return bytes(audio_data)


# # # ---------------------------------------------------------------------------
# # # Public API
# # # ---------------------------------------------------------------------------


# # async def synthesize(text: str, language: str) -> bytes:
# #     """
# #     Convert text to speech and return full audio bytes.

# #     Priority:
# #         1. Sarvam AI Bulbul v3  (if SARVAMAI_API_KEY is set)
# #         2. edge-tts             (always available, no key needed)
# #     """
# #     cleaned = _clean_text(text)
# #     if not cleaned:
# #         return b""

# #     if os.environ.get("SARVAMAI_API_KEY"):
# #         try:
# #             return await _sarvam_synthesize(cleaned, language)
# #         except Exception as e:
# #             print(f"[TTS] Sarvam failed: {e} — falling back to edge-tts")

# #     return await _edge_synthesize(cleaned, language)


# # async def synthesize_stream(text_stream, language: str):
# #     """
# #     Streaming synthesis.

# #     Accepts an async generator that yields text chunks, buffers into sentences,
# #     and yields audio bytes as each sentence is ready. This keeps time-to-first-
# #     audio low while the LLM is still generating.

# #     Priority per sentence chunk:
# #         1. Sarvam AI Bulbul v3
# #         2. edge-tts
# #     """
# #     voice = EDGE_VOICES.get(language, "en-US-AriaNeural")
# #     sarvam_key = os.environ.get("SARVAMAI_API_KEY")
# #     punctuations = {".", "?", "!", "।", ","}

# #     buffer = ""

# #     async def _speak(segment: str):
# #         cleaned = _clean_text(segment)
# #         if not cleaned:
# #             return

# #         if sarvam_key:
# #             try:
# #                 audio = await _sarvam_synthesize(cleaned, language)
# #                 yield audio
# #                 return
# #             except Exception as e:
# #                 print(f"[TTS-stream] Sarvam failed: {e} — falling back to edge-tts")

# #         # edge-tts fallback
# #         communicate = edge_tts.Communicate(cleaned, voice)
# #         async for audio_chunk in communicate.stream():
# #             if audio_chunk["type"] == "audio":
# #                 yield audio_chunk["data"]

# #     async for text_chunk in text_stream:
# #         buffer += text_chunk

# #         if any(p in buffer for p in punctuations):
# #             last_idx = max(buffer.rfind(p) for p in punctuations if p in buffer)
# #             to_speak = buffer[: last_idx + 1].strip()
# #             buffer = buffer[last_idx + 1 :]

# #             if to_speak:
# #                 async for audio in _speak(to_speak):
# #                     yield audio

# #     # Flush any remaining text
# #     if buffer.strip():
# #         async for audio in _speak(buffer.strip()):
# #             yield audio














# """
# sarvam_tts.py
# ─────────────
# Primary TTS: Sarvam AI Bulbul v3  (en-IN / hi-IN / gu-IN)
# Fallback TTS: Microsoft edge-tts  (works offline, no API key needed)

# Usage:
#     from services.sarvam_tts import synthesize, synthesize_stream
# """

# import os
# import httpx
# import base64
# import edge_tts

# # ---------------------------------------------------------------------------
# # Voice config
# # ---------------------------------------------------------------------------

# # Sarvam language codes
# SARVAM_LANG_CODES = {
#     "en": "en-IN",
#     "hi": "hi-IN",
#     "gu": "gu-IN",
# }

# # edge-tts neural voice fallbacks
# EDGE_VOICES = {
#     "en": "en-US-AriaNeural",
#     "hi": "hi-IN-SwaraNeural",
#     "gu": "gu-IN-DhwaniNeural",
# }

# # Sarvam speaker — "ishita" works well across all three languages
# SARVAM_SPEAKER = "ishita"
# SARVAM_MODEL   = "bulbul:v3"
# SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"


# # ---------------------------------------------------------------------------
# # Helpers
# # ---------------------------------------------------------------------------

# def _clean_text(text: str) -> str:
#     """Strip markdown symbols that TTS engines mispronounce or skip."""
#     if not text:
#         return ""
#     text = text.replace("**", "").replace("*", "")
#     text = text.replace("__", "").replace("_", "")
#     text = text.replace("#", "").replace("`", "")
#     return text.strip()


# async def _sarvam_synthesize(text: str, language: str) -> bytes:
#     """
#     Call the Sarvam AI Bulbul v3 REST API.
#     Returns raw audio bytes (WAV) on success, raises on failure.
#     """
#     api_key = os.environ.get("SARVAMAI_API_KEY", "")
#     if not api_key:
#         raise ValueError("SARVAMAI_API_KEY is not set.")

#     lang_code = SARVAM_LANG_CODES.get(language, "en-IN")

#     payload = {
#         "text": text,
#         "target_language_code": lang_code,
#         "speaker": SARVAM_SPEAKER,
#         "model": SARVAM_MODEL,
#     }
#     headers = {
#         "api-subscription-key": api_key,
#         "Content-Type": "application/json",
#     }

#     async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
#         resp = await client.post(SARVAM_TTS_URL, headers=headers, json=payload)

#     if resp.status_code == 200:
#         body = resp.json()
#         audios = body.get("audios", [])
#         if audios:
#             return base64.b64decode(audios[0])

#     raise ValueError(
#         f"Sarvam TTS failed: HTTP {resp.status_code} — {resp.text[:200]}"
#     )


# async def _edge_synthesize(text: str, language: str) -> bytes:
#     """edge-tts fallback — returns full audio bytes."""
#     voice = EDGE_VOICES.get(language, "en-US-AriaNeural")
#     communicate = edge_tts.Communicate(text, voice)
#     audio_data = bytearray()
#     async for chunk in communicate.stream():
#         if chunk["type"] == "audio":
#             audio_data.extend(chunk["data"])
#     return bytes(audio_data)


# # ---------------------------------------------------------------------------
# # Public API
# # ---------------------------------------------------------------------------

# async def synthesize(text: str, language: str) -> bytes:
#     """
#     Convert text to speech and return full audio bytes.

#     Priority:
#         1. Sarvam AI Bulbul v3  (if SARVAMAI_API_KEY is set)
#         2. edge-tts             (always available, no key needed)
#     """
#     cleaned = _clean_text(text)
#     if not cleaned:
#         return b""

#     if os.environ.get("SARVAMAI_API_KEY"):
#         try:
#             return await _sarvam_synthesize(cleaned, language)
#         except Exception as e:
#             print(f"[TTS] Sarvam failed: {e} — falling back to edge-tts")

#     return await _edge_synthesize(cleaned, language)


# async def synthesize_stream(text_stream, language: str):
#     """
#     Streaming synthesis.

#     Accepts an async generator that yields text chunks, buffers into sentences,
#     and yields audio bytes as each sentence is ready. This keeps time-to-first-
#     audio low while the LLM is still generating.

#     Priority per sentence chunk:
#         1. Sarvam AI Bulbul v3
#         2. edge-tts
#     """
#     voice = EDGE_VOICES.get(language, "en-US-AriaNeural")
#     sarvam_key = os.environ.get("SARVAMAI_API_KEY")
#     punctuations = {".", "?", "!", "।", ","}

#     buffer = ""

#     async def _speak(segment: str):
#         cleaned = _clean_text(segment)
#         if not cleaned:
#             return

#         if sarvam_key:
#             try:
#                 audio = await _sarvam_synthesize(cleaned, language)
#                 yield audio
#                 return
#             except Exception as e:
#                 print(f"[TTS-stream] Sarvam failed: {e} — falling back to edge-tts")

#         # edge-tts fallback
#         communicate = edge_tts.Communicate(cleaned, voice)
#         async for audio_chunk in communicate.stream():
#             if audio_chunk["type"] == "audio":
#                 yield audio_chunk["data"]

#     async for text_chunk in text_stream:
#         buffer += text_chunk

#         if any(p in buffer for p in punctuations):
#             last_idx = max(buffer.rfind(p) for p in punctuations if p in buffer)
#             to_speak = buffer[: last_idx + 1].strip()
#             buffer = buffer[last_idx + 1:]

#             if to_speak:
#                 async for audio in _speak(to_speak):
#                     yield audio

#     # Flush any remaining text
#     if buffer.strip():
#         async for audio in _speak(buffer.strip()):
#             yield audio


# # ---------------------------------------------------------------------------
# # PCM streaming output  (used by the real-time WebSocket call endpoint)
# # ---------------------------------------------------------------------------
# # Python 3.13 compatible — audioop was removed in 3.13.
# # Uses numpy (already a transitive dep via faiss/sentence-transformers) +
# # scipy.signal for resampling, with a pure-Python integer fallback so the
# # code works even if scipy is not installed.
# # ---------------------------------------------------------------------------

# import io
# import wave
# import struct
# import numpy as np

# TTS_OUTPUT_SR = 22050   # must match client AudioContext sampleRate


# def _resample_numpy(samples: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
#     """
#     Resample a 1-D float32 numpy array from src_sr → dst_sr.
#     Uses scipy.signal.resample_poly when available (high quality),
#     falls back to linear interpolation (good enough for speech).
#     """
#     if src_sr == dst_sr:
#         return samples
#     try:
#         from scipy.signal import resample_poly
#         import math
#         g = math.gcd(src_sr, dst_sr)
#         return resample_poly(samples, dst_sr // g, src_sr // g).astype(np.float32)
#     except ImportError:
#         # Pure numpy linear interpolation fallback
#         n_out = int(len(samples) * dst_sr / src_sr)
#         x_old = np.linspace(0, 1, len(samples))
#         x_new = np.linspace(0, 1, n_out)
#         return np.interp(x_new, x_old, samples).astype(np.float32)


# def _wav_bytes_to_int16_pcm(wav_bytes: bytes) -> bytes:
#     """
#     Extract raw Int16 LE PCM from a WAV blob.
#     Handles any sample width (8/16/24/32-bit) and channel count.
#     Resamples to TTS_OUTPUT_SR using numpy/scipy (Python 3.13-safe).
#     """
#     try:
#         with wave.open(io.BytesIO(wav_bytes)) as wf:
#             src_sr    = wf.getframerate()
#             n_ch      = wf.getnchannels()
#             sampwidth = wf.getsampwidth()   # bytes per sample
#             n_frames  = wf.getnframes()
#             raw       = wf.readframes(n_frames)

#         # ── Decode raw bytes → float32 [-1, 1] ────────────────────────
#         if sampwidth == 1:                  # uint8
#             arr = np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
#             arr = (arr - 128.0) / 128.0
#         elif sampwidth == 2:                # int16  (most common)
#             arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
#             arr /= 32768.0
#         elif sampwidth == 3:                # int24 — unpack manually
#             n_samples = len(raw) // 3
#             arr = np.zeros(n_samples, dtype=np.float32)
#             for i in range(n_samples):
#                 b = raw[i*3:(i+1)*3]
#                 val = struct.unpack('<i', b + (b'\xff' if b[2] & 0x80 else b'\x00'))[0]
#                 arr[i] = val / 8388608.0
#         elif sampwidth == 4:                # int32
#             arr = np.frombuffer(raw, dtype=np.int32).astype(np.float32)
#             arr /= 2147483648.0
#         else:
#             raise ValueError(f"Unsupported sample width: {sampwidth}")

#         # ── Mix down to mono ───────────────────────────────────────────
#         if n_ch > 1:
#             arr = arr.reshape(-1, n_ch).mean(axis=1)

#         # ── Resample to TTS_OUTPUT_SR ─────────────────────────────────
#         arr = _resample_numpy(arr, src_sr, TTS_OUTPUT_SR)

#         # ── Clip + convert back to int16 LE ───────────────────────────
#         arr = np.clip(arr, -1.0, 1.0)
#         int16 = (arr * 32767).astype(np.int16)
#         return int16.tobytes()

#     except Exception as e:
#         print(f"[PCM] WAV decode failed: {e} — returning raw bytes")
#         return wav_bytes


# async def synthesize_pcm_stream(text: str, language: str):
#     """
#     Sentence-level streaming synthesis → yields raw Int16 LE PCM chunks.

#     Used by /ws/call to send binary audio frames directly to the client's
#     AudioContext scheduler. No base64, no MP3 container — raw samples only.

#     Flow:
#         LLM text stream → split at punctuation → TTS per sentence → PCM → yield
#     """
#     cleaned = _clean_text(text)
#     if not cleaned:
#         return

#     # Split text into sentences for low-latency first-chunk delivery
#     import re
#     sentences = [s.strip() for s in re.split(r'(?<=[.!?,।])\s+', cleaned) if s.strip()]
#     if not sentences:
#         sentences = [cleaned]

#     sarvam_key = os.environ.get("SARVAMAI_API_KEY")
#     voice      = EDGE_VOICES.get(language, "en-US-AriaNeural")

#     for sentence in sentences:
#         wav_bytes = None

#         # ── Sarvam primary ─────────────────────────────────────────────
#         if sarvam_key:
#             try:
#                 wav_bytes = await _sarvam_synthesize(sentence, language)
#             except Exception as e:
#                 print(f"[PCM-stream] Sarvam failed: {e} — falling back to edge-tts")

#         # ── edge-tts fallback → collect MP3 then decode ─────────────────
#         if wav_bytes is None:
#             # edge-tts yields MP3 chunks; collect and decode via pydub/ffmpeg
#             mp3_buf = bytearray()
#             try:
#                 communicate = edge_tts.Communicate(sentence, voice)
#                 async for chunk in communicate.stream():
#                     if chunk["type"] == "audio":
#                         mp3_buf.extend(chunk["data"])
#             except Exception as e:
#                 print(f"[PCM-stream] edge-tts failed (likely SSL/network error): {e}")

#             if mp3_buf:
#                 try:
#                     from pydub import AudioSegment
#                     seg = AudioSegment.from_file(io.BytesIO(bytes(mp3_buf)), format="mp3")
#                     seg = seg.set_frame_rate(TTS_OUTPUT_SR).set_channels(1).set_sample_width(2)
#                     wav_bytes = seg.raw_data
#                 except Exception:
#                     # pydub not installed — yield MP3 as-is and let client handle it
#                     yield bytes(mp3_buf)
#                     continue

#         if wav_bytes:
#             pcm = _wav_bytes_to_int16_pcm(wav_bytes)
#             # Send in 8 KB chunks so the scheduler gets audio progressively
#             chunk_size = 8192
#             for i in range(0, len(pcm), chunk_size):
#                 yield pcm[i:i+chunk_size]




















"""
sarvam_tts.py
─────────────
Primary TTS: Sarvam AI Bulbul v3  (en-IN / hi-IN / gu-IN)
Fallback TTS: Microsoft edge-tts  (works offline, no API key needed)

Usage:
    from services.sarvam_tts import synthesize, synthesize_stream
"""

import os
import httpx
import base64
import edge_tts

# ---------------------------------------------------------------------------
# Voice config
# ---------------------------------------------------------------------------

# Sarvam language codes
SARVAM_LANG_CODES = {
    "en": "en-IN",
    "hi": "hi-IN",
    "gu": "gu-IN",
}

# edge-tts neural voice fallbacks
EDGE_VOICES = {
    "en": "en-US-AriaNeural",
    "hi": "hi-IN-SwaraNeural",
    "gu": "gu-IN-DhwaniNeural",
}

# Sarvam speaker — "ishita" works well across all three languages
SARVAM_SPEAKER = "ishita"
SARVAM_MODEL   = "bulbul:v3"
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_text(text: str) -> str:
    """Strip markdown symbols that TTS engines mispronounce or skip."""
    if not text:
        return ""
    text = text.replace("**", "").replace("*", "")
    text = text.replace("__", "").replace("_", "")
    text = text.replace("#", "").replace("`", "")
    return text.strip()


async def _sarvam_synthesize(text: str, language: str) -> bytes:
    """
    Call the Sarvam AI Bulbul v3 REST API.
    Returns raw audio bytes (WAV) on success, raises on failure.
    """
    api_key = os.environ.get("SARVAMAI_API_KEY", "")
    if not api_key:
        raise ValueError("SARVAMAI_API_KEY is not set.")

    lang_code = SARVAM_LANG_CODES.get(language, "en-IN")

    payload = {
        "text": text,
        "target_language_code": lang_code,
        "speaker": SARVAM_SPEAKER,
        "model": SARVAM_MODEL,
    }
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(SARVAM_TTS_URL, headers=headers, json=payload)

    if resp.status_code == 200:
        body = resp.json()
        audios = body.get("audios", [])
        if audios:
            return base64.b64decode(audios[0])

    raise ValueError(
        f"Sarvam TTS failed: HTTP {resp.status_code} — {resp.text[:200]}"
    )


async def _edge_synthesize(text: str, language: str) -> bytes:
    """edge-tts fallback — returns full audio bytes."""
    voice = EDGE_VOICES.get(language, "en-US-AriaNeural")
    communicate = edge_tts.Communicate(text, voice)
    audio_data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
    return bytes(audio_data)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def synthesize(text: str, language: str) -> bytes:
    """
    Convert text to speech and return full audio bytes.

    Priority:
        1. Sarvam AI Bulbul v3  (if SARVAMAI_API_KEY is set)
        2. edge-tts             (always available, no key needed)
    """
    cleaned = _clean_text(text)
    if not cleaned:
        return b""

    if os.environ.get("SARVAMAI_API_KEY"):
        try:
            return await _sarvam_synthesize(cleaned, language)
        except Exception as e:
            print(f"[TTS] Sarvam failed: {e} — falling back to edge-tts")

    return await _edge_synthesize(cleaned, language)


async def synthesize_stream(text_stream, language: str):
    """
    Streaming synthesis.

    Accepts an async generator that yields text chunks, buffers into sentences,
    and yields audio bytes as each sentence is ready. This keeps time-to-first-
    audio low while the LLM is still generating.

    Priority per sentence chunk:
        1. Sarvam AI Bulbul v3
        2. edge-tts
    """
    voice = EDGE_VOICES.get(language, "en-US-AriaNeural")
    sarvam_key = os.environ.get("SARVAMAI_API_KEY")
    punctuations = {".", "?", "!", "।", ","}

    buffer = ""

    async def _speak(segment: str):
        cleaned = _clean_text(segment)
        if not cleaned:
            return

        if sarvam_key:
            try:
                audio = await _sarvam_synthesize(cleaned, language)
                yield audio
                return
            except Exception as e:
                print(f"[TTS-stream] Sarvam failed: {e} — falling back to edge-tts")

        # edge-tts fallback
        communicate = edge_tts.Communicate(cleaned, voice)
        async for audio_chunk in communicate.stream():
            if audio_chunk["type"] == "audio":
                yield audio_chunk["data"]

    async for text_chunk in text_stream:
        buffer += text_chunk

        if any(p in buffer for p in punctuations):
            last_idx = max(buffer.rfind(p) for p in punctuations if p in buffer)
            to_speak = buffer[: last_idx + 1].strip()
            buffer = buffer[last_idx + 1:]

            if to_speak:
                async for audio in _speak(to_speak):
                    yield audio

    # Flush any remaining text
    if buffer.strip():
        async for audio in _speak(buffer.strip()):
            yield audio


# ---------------------------------------------------------------------------
# PCM streaming output  (used by the real-time WebSocket call endpoint)
# ---------------------------------------------------------------------------
# Python 3.13 compatible — audioop was removed in 3.13.
# Uses numpy (already a transitive dep via faiss/sentence-transformers) +
# scipy.signal for resampling, with a pure-Python integer fallback so the
# code works even if scipy is not installed.
# ---------------------------------------------------------------------------

import io
import wave
import struct
import numpy as np

TTS_OUTPUT_SR = 22050   # must match client AudioContext sampleRate


def _resample_numpy(samples: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    """
    Resample a 1-D float32 numpy array from src_sr → dst_sr.
    Uses scipy.signal.resample_poly when available (high quality),
    falls back to linear interpolation (good enough for speech).
    """
    if src_sr == dst_sr:
        return samples
    try:
        from scipy.signal import resample_poly
        import math
        g = math.gcd(src_sr, dst_sr)
        return resample_poly(samples, dst_sr // g, src_sr // g).astype(np.float32)
    except ImportError:
        # Pure numpy linear interpolation fallback
        n_out = int(len(samples) * dst_sr / src_sr)
        x_old = np.linspace(0, 1, len(samples))
        x_new = np.linspace(0, 1, n_out)
        return np.interp(x_new, x_old, samples).astype(np.float32)


def _wav_bytes_to_int16_pcm(wav_bytes: bytes) -> bytes:
    """
    Extract raw Int16 LE PCM from a WAV blob.
    Handles any sample width (8/16/24/32-bit) and channel count.
    Resamples to TTS_OUTPUT_SR using numpy/scipy (Python 3.13-safe).
    """
    try:
        with wave.open(io.BytesIO(wav_bytes)) as wf:
            src_sr    = wf.getframerate()
            n_ch      = wf.getnchannels()
            sampwidth = wf.getsampwidth()   # bytes per sample
            n_frames  = wf.getnframes()
            raw       = wf.readframes(n_frames)

        # ── Decode raw bytes → float32 [-1, 1] ────────────────────────
        if sampwidth == 1:                  # uint8
            arr = np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
            arr = (arr - 128.0) / 128.0
        elif sampwidth == 2:                # int16  (most common)
            arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
            arr /= 32768.0
        elif sampwidth == 3:                # int24 — unpack manually
            n_samples = len(raw) // 3
            arr = np.zeros(n_samples, dtype=np.float32)
            for i in range(n_samples):
                b = raw[i*3:(i+1)*3]
                val = struct.unpack('<i', b + (b'\xff' if b[2] & 0x80 else b'\x00'))[0]
                arr[i] = val / 8388608.0
        elif sampwidth == 4:                # int32
            arr = np.frombuffer(raw, dtype=np.int32).astype(np.float32)
            arr /= 2147483648.0
        else:
            raise ValueError(f"Unsupported sample width: {sampwidth}")

        # ── Mix down to mono ───────────────────────────────────────────
        if n_ch > 1:
            arr = arr.reshape(-1, n_ch).mean(axis=1)

        # ── Resample to TTS_OUTPUT_SR ─────────────────────────────────
        arr = _resample_numpy(arr, src_sr, TTS_OUTPUT_SR)

        # ── Clip + convert back to int16 LE ───────────────────────────
        arr = np.clip(arr, -1.0, 1.0)
        int16 = (arr * 32767).astype(np.int16)
        return int16.tobytes()

    except Exception as e:
        print(f"[PCM] WAV decode failed: {e} — returning raw bytes")
        return wav_bytes


async def synthesize_pcm_stream(text: str, language: str):
    """
    Sentence-level streaming synthesis → yields raw Int16 LE PCM chunks.

    Used by /ws/call to send binary audio frames directly to the client's
    AudioContext scheduler. No base64, no MP3 container — raw samples only.

    Flow:
        LLM text stream → split at punctuation → TTS per sentence → PCM → yield
    """
    cleaned = _clean_text(text)
    if not cleaned:
        return

    # Split text into sentences for low-latency first-chunk delivery
    import re
    sentences = [s.strip() for s in re.split(r'(?<=[.!?,।])\s+', cleaned) if s.strip()]
    if not sentences:
        sentences = [cleaned]

    sarvam_key = os.environ.get("SARVAMAI_API_KEY")
    voice      = EDGE_VOICES.get(language, "en-US-AriaNeural")

    for sentence in sentences:
        wav_bytes = None

        # ── Sarvam primary ─────────────────────────────────────────────
        if sarvam_key:
            try:
                wav_bytes = await _sarvam_synthesize(sentence, language)
            except Exception as e:
                print(f"[PCM-stream] Sarvam failed: {e} — falling back to edge-tts")

        # ── edge-tts fallback → collect MP3 then decode ─────────────────
        if wav_bytes is None:
            # edge-tts yields MP3 chunks; collect and decode via pydub/ffmpeg
            mp3_buf = bytearray()
            communicate = edge_tts.Communicate(sentence, voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    mp3_buf.extend(chunk["data"])

            if mp3_buf:
                try:
                    from pydub import AudioSegment
                    seg = AudioSegment.from_file(io.BytesIO(bytes(mp3_buf)), format="mp3")
                    seg = seg.set_frame_rate(TTS_OUTPUT_SR).set_channels(1).set_sample_width(2)
                    wav_bytes = seg.raw_data
                except Exception:
                    # pydub not installed — yield MP3 as-is and let client handle it
                    yield bytes(mp3_buf)
                    continue

        if wav_bytes:
            pcm = _wav_bytes_to_int16_pcm(wav_bytes)
            # Send in 8 KB chunks so the scheduler gets audio progressively
            chunk_size = 8192
            for i in range(0, len(pcm), chunk_size):
                yield pcm[i:i+chunk_size]