import asyncio
from dataclasses import dataclass

from kb.retriever import retrieve
from services.deepgram_stt import transcribe
from services.gemini_translate import (
    detect_language,
    generate_answer,
)
from services.sarvam_tts import synthesize


SUPPORTED_LANGS = {"en", "hi", "gu"}


@dataclass
class VoicePipelineResult:
    transcript: str
    input_language: str
    english_query: str
    retrieved_chunks: list[str]
    answer_english: str
    answer_localized: str
    audio_bytes: bytes


async def _resolve_input_language(transcript: str, lang_from_stt: str) -> str:
    """
    Prefer STT language for speed.
    If STT says English, refine with LLM to catch romanized Hindi/Gujarati.
    """
    stt_lang = (lang_from_stt or "en").split("-")[0].lower()
    if stt_lang not in SUPPORTED_LANGS:
        stt_lang = "en"
    if stt_lang != "en":
        return stt_lang
    return await detect_language(transcript)


async def run_voice_pipeline(
    audio_bytes: bytes, k: int = 5, mime_type: str | None = None
) -> VoicePipelineResult:
    """
    High-performance Voice Pipeline optimized for sub-second latency:
      1. Raw audio -> Transcribe to text (Deepgram).
      2. Direct Multilingual Search in FAISS using raw transcript (Bypasses Translate-to-English).
      3. Direct Localized Generation (Hinglish/Gujlish) in a single LLM call (Bypasses Translate-from-English).
      4. Synthesize Audio directly (Sarvam AI / Edge TTS).
    """
    transcript, lang_from_stt = await transcribe(audio_bytes, mime_type=mime_type)
    if not transcript or not transcript.strip():
        raise ValueError("No speech detected.")

    input_language = await _resolve_input_language(transcript, lang_from_stt)

    # Optimization A: Direct multilingual FAISS retrieval offloaded to background thread
    chunks = await asyncio.to_thread(retrieve, transcript, k)

    # Optimization B: Single-shot generation directly in Hinglish/Gujlish/English (saves ~2.0s of double translation)
    answer_localized = await generate_answer(transcript, chunks, input_language)

    # Optimization C: Synthesize directly
    audio_out = await synthesize(answer_localized, input_language)

    return VoicePipelineResult(
        transcript=transcript,
        input_language=input_language,
        english_query=transcript,
        retrieved_chunks=chunks,
        answer_english=answer_localized,
        answer_localized=answer_localized,
        audio_bytes=audio_out,
    )
