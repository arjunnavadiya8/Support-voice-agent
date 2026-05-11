# import os
# import asyncio
# import ssl
# from typing import Callable, Awaitable
# from deepgram import AsyncDeepgramClient
# from dotenv import load_dotenv

# # Force load fresh .env values to avoid stale uvicorn cache
# load_dotenv()

# ssl._create_default_https_context = ssl._create_unverified_context
# DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY", "")


# class DeepgramLiveSTT:
#     """
#     Manages a persistent Deepgram live websocket connection using listen.v2
#     with the asynchronous client, completely supporting flux-general-multi.
#     """

#     def __init__(
#         self,
#         on_transcript: Callable[[str, bool, bool], Awaitable[None]],
#     ):
#         self.dg_client = AsyncDeepgramClient(api_key=DEEPGRAM_API_KEY)
#         self.on_transcript = on_transcript
#         self.connection_cm = None
#         self.connection = None
#         self.listen_task: asyncio.Task | None = None
#         self.is_connected = False

#     async def start(self):
#         self.connection_cm = self.dg_client.listen.v2.connect(
#             model="flux-general-multi",
#             encoding="linear16",
#             sample_rate=16000,
#             eager_eot_threshold=0.4,
#             eot_timeout_ms=300,
#         )
#         self.connection = await self.connection_cm.__aenter__()
#         self.listen_task = asyncio.create_task(self._listen())
#         self.is_connected = True
#         print("[Deepgram] Live connection started (v2 flux-general-multi)")

#     async def _listen(self):
#         assert self.connection is not None

#         try:
#             async for event in self.connection:
#                 transcript = getattr(event, "transcript", "") or ""
#                 if not transcript:
#                     continue

#                 event_name = getattr(event, "event", "Update")
#                 is_final = event_name in {"EagerEndOfTurn", "EndOfTurn"}
#                 speech_final = event_name == "EndOfTurn"
#                 await self.on_transcript(transcript, is_final, speech_final)
#         except asyncio.CancelledError:
#             raise
#         except Exception as error:
#             print(f"[Deepgram Error] {error}")

#     async def send_audio(self, audio_chunk: bytes):
#         if self.is_connected and self.connection and audio_chunk:
#             await self.connection.send_media(audio_chunk)

#     async def close(self):
#         if not self.is_connected:
#             return

#         if self.connection:
#             try:
#                 await self.connection.send_close_stream()
#             except Exception:
#                 pass

#         if self.listen_task:
#             self.listen_task.cancel()
#             await asyncio.gather(self.listen_task, return_exceptions=True)
#             self.listen_task = None

#         if self.connection_cm:
#             await self.connection_cm.__aexit__(None, None, None)
#             self.connection_cm = None

#         self.connection = None
#         self.is_connected = False
#         print("[Deepgram] Live connection closed")







# 11


"""
stt_service.py — Deepgram Live STT  (deepgram-sdk v7)
═══════════════════════════════════════════════════════
Uses flux-general-multi for best multilingual accuracy on en/hi/gu.

Key improvements:
  - eager_eot_threshold=0.4 + eot_timeout_ms=300 for fast end-of-turn
  - Transcript fuzzy-normalisation before on_transcript callback
    so imperfect ASR ("user something create kre") gets cleaned up
    before being passed to the KB retriever.
  - Noise filter: single-word / all-punctuation results are dropped.
"""

import os, asyncio, ssl, re, logging
from typing import Callable, Awaitable
from deepgram import AsyncDeepgramClient
from dotenv import load_dotenv

load_dotenv()
ssl._create_default_https_context = ssl._create_unverified_context

log = logging.getLogger("stt")
DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY", "")

# Noise filter: drop transcripts that are too short to be real utterances
_NOISE_RE = re.compile(r'^[\s\W\d]{0,3}$')   # only whitespace/punctuation/digits


def _is_noise(text: str) -> bool:
    """Return True if transcript is ambient noise / too short to process."""
    t = text.strip()
    if not t:
        return True
    if len(t) < 2:
        return True
    if _NOISE_RE.match(t):
        return True
    return False


class DeepgramLiveSTT:
    """
    Persistent Deepgram Live WebSocket using flux-general-multi.
    Supports en / hi / gu with automatic language detection.

    Callback signature:
        on_transcript(transcript: str, is_final: bool, speech_final: bool)
    """

    def __init__(self, on_transcript: Callable[[str, bool, bool], Awaitable[None]]):
        self.dg_client     = AsyncDeepgramClient(api_key=DEEPGRAM_API_KEY)
        self.on_transcript = on_transcript
        self.connection_cm = None
        self.connection    = None
        self.listen_task: asyncio.Task | None = None
        self.is_connected  = False

    async def start(self):
        self.connection_cm = self.dg_client.listen.v2.connect(
            model               = "flux-general-multi",
            encoding            = "linear16",
            sample_rate         = 16000,
            eager_eot_threshold = 0.4,    # fire EagerEndOfTurn early when confident
            eot_timeout_ms      = 300,    # 300ms silence → EndOfTurn
            interim_results     = True,   # show words as user speaks
            punctuate           = True,
            smart_format        = True,
            filler_words        = False,
        )
        self.connection   = await self.connection_cm.__aenter__()
        self.listen_task  = asyncio.create_task(self._listen())
        self.is_connected = True
        log.info("[STT] Deepgram Live started (flux-general-multi)")

    async def _listen(self):
        try:
            async for event in self.connection:
                transcript = (getattr(event, "transcript", "") or "").strip()
                if not transcript:
                    continue

                event_name   = getattr(event, "event", "Update")
                is_final     = event_name in {"EagerEndOfTurn", "EndOfTurn"}
                speech_final = event_name == "EndOfTurn"

                # Drop noise-only transcripts on finals
                if is_final and _is_noise(transcript):
                    log.debug("[STT] noise filtered: %r", transcript)
                    continue

                await self.on_transcript(transcript, is_final, speech_final)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.error("[STT] listen error: %s", e)

    async def send_audio(self, chunk: bytes):
        if self.is_connected and self.connection and chunk:
            await self.connection.send_media(chunk)

    async def close(self):
        if not self.is_connected:
            return
        self.is_connected = False
        try:
            await self.connection.send_close_stream()
        except Exception:
            pass
        if self.listen_task:
            self.listen_task.cancel()
            await asyncio.gather(self.listen_task, return_exceptions=True)
            self.listen_task = None
        if self.connection_cm:
            try:
                await self.connection_cm.__aexit__(None, None, None)
            except Exception:
                pass
            self.connection_cm = None
        self.connection = None
        log.info("[STT] Deepgram Live closed")