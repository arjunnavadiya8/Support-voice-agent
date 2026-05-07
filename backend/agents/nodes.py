# # from agents.state import VoiceState
# # from services.deepgram_stt import transcribe
# # from services.edge_tts_service import synthesize
# # from services.gemini_translate import translate_to_english, generate_answer
# # from kb.retriever import retrieve


# # async def node_transcribe(state: VoiceState) -> VoiceState:
# #     try:
# #         transcript, lang = await transcribe(state.audio_bytes)
# #         state.transcript = transcript
# #         state.detected_language = lang
# #     except Exception as e:
# #         state.error = f"STT failed: {e}"
# #     return state


# # async def node_translate(state: VoiceState) -> VoiceState:
# #     if state.error:
# #         return state
# #     try:
# #         state.english_query = await translate_to_english(
# #             state.transcript, state.detected_language
# #         )
# #     except Exception as e:
# #         state.error = f"Translation failed: {e}"
# #     return state


# # async def node_retrieve(state: VoiceState) -> VoiceState:
# #     if state.error:
# #         return state
# #     try:
# #         state.retrieved_chunks = retrieve(state.english_query)
# #     except Exception as e:
# #         state.error = f"Retrieval failed: {e}"
# #     return state


# # async def node_generate(state: VoiceState) -> VoiceState:
# #     if state.error:
# #         return state
# #     try:
# #         state.answer_text = await generate_answer(
# #             state.english_query,
# #             state.retrieved_chunks,
# #             state.detected_language,
# #         )
# #     except Exception as e:
# #         state.error = f"Generation failed: {e}"
# #     return state


# # async def node_synthesize(state: VoiceState) -> VoiceState:
# #     if state.error:
# #         # speak the error in English
# #         state.answer_text = "Sorry, something went wrong. Please try again."
# #         state.detected_language = "en"
# #     try:
# #         state.audio_response = await synthesize(
# #             state.answer_text, state.detected_language
# #         )
# #     except Exception as e:
# #         state.error = f"TTS failed: {e}"
# #     return state






# from agents.state import VoiceState
# from services.deepgram_stt import transcribe
# from services.sarvam_tts import synthesize
# from services.gemini_translate import (
#     translate_to_english,
#     detect_language,
#     generate_answer,
# )
# from kb.retriever import retrieve


# async def node_transcribe(state: VoiceState) -> VoiceState:
#     """STT: audio bytes → transcript + detected language (Deepgram nova-3)."""
#     try:
#         transcript, lang = await transcribe(state.audio_bytes)
#         state.transcript = transcript
#         state.detected_language = lang
#         print(f"[TRANSCRIBE] '{transcript}' | lang={lang}")
#     except Exception as e:
#         state.error = f"STT failed: {e}"
#         print(f"[TRANSCRIBE] Error: {e}")
#     return state


# async def node_detect_language(state: VoiceState) -> VoiceState:
#     """
#     Optional language re-check via LLM for romanised/ambiguous transcripts.
#     Deepgram's detected_language is usually reliable, but Hinglish in Latin
#     script can be mis-tagged. This node corrects it when needed.
#     """
#     if state.error:
#         return state
#     try:
#         if not state.transcript:
#             return state
#         # Only run LLM detection if Deepgram returned 'en' for a short phrase
#         # that might actually be romanised Hindi/Gujarati
#         refined = await detect_language(state.transcript)
#         if refined != state.detected_language:
#             print(
#                 f"[LANG] Deepgram={state.detected_language} → LLM refined to {refined}"
#             )
#             state.detected_language = refined
#     except Exception as e:
#         print(f"[LANG] detect_language failed (non-fatal): {e}")
#     return state


# async def node_translate(state: VoiceState) -> VoiceState:
#     """Translate transcript → English for RAG (OpenAI primary, Gemini fallback)."""
#     if state.error:
#         return state
#     try:
#         state.english_query = await translate_to_english(
#             state.transcript, state.detected_language
#         )
#         print(f"[TRANSLATE] '{state.english_query}'")
#     except Exception as e:
#         state.error = f"Translation failed: {e}"
#         print(f"[TRANSLATE] Error: {e}")
#     return state


# async def node_retrieve(state: VoiceState) -> VoiceState:
#     """RAG: vector search over FAISS knowledge base."""
#     if state.error:
#         return state
#     try:
#         state.retrieved_chunks = retrieve(state.english_query)
#         print(f"[RETRIEVE] {len(state.retrieved_chunks)} chunks")
#     except Exception as e:
#         state.error = f"Retrieval failed: {e}"
#         print(f"[RETRIEVE] Error: {e}")
#     return state


# async def node_generate(state: VoiceState) -> VoiceState:
#     """LLM: generate answer in user's language (Gemini primary, OpenAI fallback)."""
#     if state.error:
#         return state
#     try:
#         state.answer_text = await generate_answer(
#             state.english_query,
#             state.retrieved_chunks,
#             state.detected_language,
#         )
#         print(f"[GENERATE] {state.answer_text[:100]}...")
#     except Exception as e:
#         state.error = f"Generation failed: {e}"
#         print(f"[GENERATE] Error: {e}")
#     return state


# async def node_synthesize(state: VoiceState) -> VoiceState:
#     """TTS: text → audio bytes (Sarvam Bulbul v3 primary, edge-tts fallback)."""
#     if state.error:
#         state.answer_text = "Sorry, something went wrong. Please try again."
#         state.detected_language = "en"

#     try:
#         state.audio_response = await synthesize(
#             state.answer_text, state.detected_language
#         )
#         print(f"[SYNTHESIZE] {len(state.audio_response)} bytes")
#     except Exception as e:
#         state.error = f"TTS failed: {e}"
#         print(f"[SYNTHESIZE] Error: {e}")
#     return state















"""
nodes.py — phone-call pipeline nodes
──────────────────────────────────────
Each async function receives VoiceState, does one job, returns VoiceState.
Error in any node short-circuits to node_synthesize which speaks the fallback.

Phone-call additions vs the original:
  • node_transcribe    — same, but skips empty transcript gracefully
  • node_detect_language — same
  • node_translate     — same, skip API when lang=en
  • node_retrieve      — same FAISS search
  • node_generate      — now passes conversation history for multi-turn context
  • node_synthesize    — same Sarvam/edge-tts
"""

from agents.state import VoiceState, ConversationTurn
from services.deepgram_stt import transcribe
from services.sarvam_tts import synthesize
from services.gemini_translate import (
    translate_to_english,
    detect_language,
    generate_answer,
)
from kb.retriever import retrieve


async def node_transcribe(state: VoiceState) -> VoiceState:
    """STT: audio bytes → transcript + detected language (Deepgram nova-3)."""
    try:
        transcript, lang = await transcribe(state.audio_bytes)
        state.transcript = transcript.strip()
        state.detected_language = lang
        print(f"[TRANSCRIBE] '{state.transcript}' | lang={lang}")
    except Exception as e:
        state.error = f"STT failed: {e}"
        print(f"[TRANSCRIBE] Error: {e}")
    return state


async def node_detect_language(state: VoiceState) -> VoiceState:
    """
    LLM language refinement for romanised Hinglish mis-tagged as 'en'.
    Non-fatal — if it fails we keep Deepgram's detection.
    """
    if state.error or not state.transcript:
        return state
    try:
        refined = await detect_language(state.transcript)
        if refined != state.detected_language:
            print(f"[LANG] Deepgram={state.detected_language} → refined={refined}")
            state.detected_language = refined
    except Exception as e:
        print(f"[LANG] detect_language failed (non-fatal): {e}")
    return state


async def node_translate(state: VoiceState) -> VoiceState:
    """Translate transcript → English for RAG (skip if already English)."""
    if state.error:
        return state
    try:
        state.english_query = await translate_to_english(
            state.transcript, state.detected_language
        )
        print(f"[TRANSLATE] '{state.english_query}'")
    except Exception as e:
        state.error = f"Translation failed: {e}"
        print(f"[TRANSLATE] Error: {e}")
    return state


async def node_retrieve(state: VoiceState) -> VoiceState:
    """RAG: vector search over FAISS knowledge base."""
    if state.error:
        return state
    try:
        state.retrieved_chunks = retrieve(state.english_query)
        print(f"[RETRIEVE] {len(state.retrieved_chunks)} chunks")
    except Exception as e:
        state.error = f"Retrieval failed: {e}"
        print(f"[RETRIEVE] Error: {e}")
    return state


async def node_generate(state: VoiceState) -> VoiceState:
    """
    LLM: generate answer in user's language, with full conversation history
    so multi-turn follow-ups feel natural (phone-call context).

    Primary: Gemini 2.5 Flash  |  Fallback: OpenAI GPT-4o-mini
    """
    if state.error:
        return state
    try:
        state.answer_text = await generate_answer(
            query_english=state.english_query,
            context_chunks=state.retrieved_chunks,
            response_language=state.detected_language,
            history=state.history,          # ← multi-turn history
            is_greeting=state.is_greeting,  # ← first-turn greeting flag
        )
        # Append this turn to history for next round
        state.history.append(
            ConversationTurn(role="user", text=state.transcript, language=state.detected_language)
        )
        state.history.append(
            ConversationTurn(role="assistant", text=state.answer_text, language=state.detected_language)
        )
        # Keep last 10 turns (5 exchanges) to avoid context bloat
        state.history = state.history[-10:]
        print(f"[GENERATE] {state.answer_text[:100]}...")
    except Exception as e:
        state.error = f"Generation failed: {e}"
        print(f"[GENERATE] Error: {e}")
    return state


async def node_synthesize(state: VoiceState) -> VoiceState:
    """TTS: text → audio bytes (Sarvam Bulbul v3 primary, edge-tts fallback)."""
    if state.error:
        state.answer_text = "Sorry, something went wrong. Please try again."
        state.detected_language = "en"

    try:
        state.audio_response = await synthesize(
            state.answer_text, state.detected_language
        )
        print(f"[SYNTHESIZE] {len(state.audio_response)} bytes")
    except Exception as e:
        state.error = f"TTS failed: {e}"
        print(f"[SYNTHESIZE] Error: {e}")
    return state