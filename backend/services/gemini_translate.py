# # # # import os
# # # # import traceback
# # # # from google import genai
# # # # from openai import OpenAI

# # # # # Use google-genai
# # # # client = genai.Client()
# # # # openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# # # # LANG_NAMES = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}

# # # # MODEL_NAME = "gemini-2.5-flash"
# # # # OPENAI_MODEL_NAME = "gpt-4o-mini"


# # # # async def detect_language(text: str) -> str:
# # # #     """Uses LLM to accurately identify the language of the transcript."""
# # # #     if not text:
# # # #         return "en"
# # # #     # Fast non-ASCII scan
# # # #     if any("\u0900" <= c <= "\u097f" for c in text):
# # # #         return "hi"
# # # #     if any("\u0a80" <= c <= "\u0aff" for c in text):
# # # #         return "gu"

# # # #     prompt = (
# # # #         f"Identify the language of the following text: English, Hindi, or Gujarati. "
# # # #         f"Respond with exactly one of these three words: English, Hindi, Gujarati. "
# # # #         f"Text:\n\n{text}"
# # # #     )
# # # #     try:
# # # #         res = openai_client.chat.completions.create(
# # # #             model=OPENAI_MODEL_NAME, messages=[{"role": "user", "content": prompt}]
# # # #         )
# # # #         res_txt = res.choices[0].message.content.strip().lower()
# # # #         if "hindi" in res_txt:
# # # #             return "hi"
# # # #         if "gujarati" in res_txt:
# # # #             return "gu"
# # # #         return "en"
# # # #     except Exception as oe:
# # # #         print(f"OpenAI detect_language failed: {oe}. Falling back to Gemini.")
# # # #         try:
# # # #             response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
# # # #             res = response.text.strip().lower()
# # # #             if "hindi" in res:
# # # #                 return "hi"
# # # #             if "gujarati" in res:
# # # #                 return "gu"
# # # #             return "en"
# # # #         except Exception:
# # # #             return "en"


# # # # async def translate_to_english(text: str, source_lang: str) -> str:
# # # #     # We ask the LLM to translate to English ALWAYS.
# # # #     # If the text is already in English, it returns it exactly as it is.
# # # #     # This prevents short phrases in Latin-script Hindi from bypassing the translation step!
# # # #     prompt = (
# # # #         f"Translate the following text to English. If it is already in English, "
# # # #         f"return it exactly as it is. Return ONLY the English translation, nothing else.\n\n{text}"
# # # #     )
# # # #     try:
# # # #         res = openai_client.chat.completions.create(
# # # #             model=OPENAI_MODEL_NAME, messages=[{"role": "user", "content": prompt}]
# # # #         )
# # # #         return res.choices[0].message.content.strip()
# # # #     except Exception as oe:
# # # #         print(f"OpenAI translation failed: {oe}. Falling back to Gemini.")
# # # #         try:
# # # #             response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
# # # #             return response.text.strip()
# # # #         except Exception as e:
# # # #             print(f"Gemini fallback failed: {e}")
# # # #             return text


# # # # async def generate_answer(
# # # #     query_english: str,
# # # #     context_chunks: list[str],
# # # #     response_language: str,
# # # # ) -> str:
# # # #     lang_name = LANG_NAMES.get(response_language, "English")
# # # #     context = "\n\n---\n\n".join(context_chunks)
# # # #     prompt = f"""You are a customer support agent for Suvit.

# # # # Answer using the provided context. If the user greets you (e.g. says hello, hi, how are you), respond warmly with a greeting first and introduce yourself, then answer the question or mention what you can assist with.

# # # # IMPORTANT LANGUAGE RULE:
# # # # - Respond in {lang_name}
# # # # - If language is Hindi → respond in Hinglish (Hindi written in English script)
# # # # - If language is Gujarati → respond in Gujlish (Gujarati written in English script)
# # # # - Do NOT use pure Hindi or Gujarati script

# # # # Examples:
# # # # Hindi → "aap bank statement kaise upload kar sakte hain"
# # # # Gujarati → "tame bank statement kevi rite upload kari shako cho"

# # # # STYLE:
# # # # - Keep it simple, conversational, and clear
# # # # - Use natural spoken style (like customer support agent speaking)

# # # # If answer not found:
# # # # "I don't have that information in my current knowledge base. Please contact our support team for assistance."

# # # # Context:
# # # # {context}

# # # # Question:
# # # # {query_english}"""

# # # #     try:
# # # #         res = openai_client.chat.completions.create(
# # # #             model=OPENAI_MODEL_NAME, messages=[{"role": "user", "content": prompt}]
# # # #         )
# # # #         return res.choices[0].message.content.strip()
# # # #     except Exception as oe:
# # # #         print(f"OpenAI generate_answer failed: {oe}. Falling back to Gemini.")
# # # #         try:
# # # #             response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
# # # #             return response.text.strip()
# # # #         except Exception as e:
# # # #             print(f"Gemini fallback failed: {e}")
# # # #             return "Error generating answer via fallback."


# # # # async def generate_answer_stream(
# # # #     query_english: str,
# # # #     context_chunks: list[str],
# # # #     response_language: str,
# # # # ):
# # # #     """Yields text chunks as they are generated by Gemini/OpenAI."""
# # # #     lang_name = LANG_NAMES.get(response_language, "English")
# # # #     context = "\n\n---\n\n".join(context_chunks)
# # # #     prompt = f"""You are a customer support agent for Suvit.

# # # # Answer using the provided context. If the user greets you (e.g. says hello, hi, how are you), respond warmly with a greeting first and introduce yourself, then answer the question or mention what you can assist with.

# # # # IMPORTANT LANGUAGE RULE:
# # # # - Respond in {lang_name}
# # # # - If language is Hindi → respond in Hinglish (Hindi written in English script)
# # # # - If language is Gujarati → respond in Gujlish (Gujarati written in English script)
# # # # - Do NOT use pure Hindi or Gujarati script

# # # # Examples:
# # # # Hindi → "aap bank statement kaise upload kar sakte hain"
# # # # Gujarati → "tame bank statement kevi rite upload kari shako cho"

# # # # STYLE:
# # # # - Keep it simple, conversational, and clear
# # # # - Use natural spoken style (like customer support agent speaking)

# # # # If answer not found:
# # # # "I don't have that information in my current knowledge base. Please contact our support team for assistance."

# # # # Context:
# # # # {context}

# # # # Question:
# # # # {query_english}"""

# # # #     try:
# # # #         res_stream = openai_client.chat.completions.create(
# # # #             model=OPENAI_MODEL_NAME,
# # # #             messages=[{"role": "user", "content": prompt}],
# # # #             stream=True,
# # # #         )
# # # #         for chunk in res_stream:
# # # #             content = chunk.choices[0].delta.content
# # # #             if content:
# # # #                 yield content
# # # #     except Exception as oe:
# # # #         print(f"OpenAI streaming failed: {oe}. Falling back to Gemini.")
# # # #         try:
# # # #             response_stream = client.models.generate_content_stream(
# # # #                 model=MODEL_NAME, contents=prompt
# # # #             )
# # # #             for chunk in response_stream:
# # # #                 if chunk.text:
# # # #                     yield chunk.text
# # # #         except Exception as e:
# # # #             print(f"Gemini fallback failed: {e}")
# # # #             yield "I encountered a quota limit error."


# # # # # ─── Conversational Streaming (Real-Time Voice) ──────────────────────────────

# # # # async def generate_greeting_stream(language: str):
# # # #     """Yields a warm greeting when the session starts."""
# # # #     lang_name = LANG_NAMES.get(language, "English")
# # # #     prompt = f"""You are Suvit Assistant — a friendly, warm customer support agent.
# # # # Generate a short, friendly greeting to start a phone call. (Max 1 sentence).
# # # # Introduce yourself as the user's Suvit assistant.

# # # # IMPORTANT LANGUAGE RULE:
# # # # - Respond in {lang_name}
# # # # - If language is Hindi → respond in Hinglish (Hindi written in English script)
# # # # - If language is Gujarati → respond in Gujlish (Gujarati written in English script)
# # # # - Do NOT use Devanagari or Gujarati script

# # # # Example: "Hey! I'm your Suvit assistant, how can I help you today?"
# # # # """
# # # #     try:
# # # #         res_stream = openai_client.chat.completions.create(
# # # #             model=OPENAI_MODEL_NAME,
# # # #             messages=[{"role": "user", "content": prompt}],
# # # #             stream=True,
# # # #         )
# # # #         for chunk in res_stream:
# # # #             content = chunk.choices[0].delta.content
# # # #             if content:
# # # #                 yield content
# # # #     except Exception as oe:
# # # #         print(f"OpenAI greeting failed: {oe}. Falling back to Gemini")
# # # #         try:
# # # #             response_stream = client.models.generate_content_stream(
# # # #                 model=MODEL_NAME, contents=prompt
# # # #             )
# # # #             for chunk in response_stream:
# # # #                 if chunk.text:
# # # #                     yield chunk.text
# # # #         except Exception as e:
# # # #             print(f"Gemini greeting fallback failed: {e}")
# # # #             yield "Hello! I am your Suvit assistant. How can I help you today?"


# # # # async def generate_conversational_response_stream(
# # # #     transcript: str,
# # # #     context_chunks: list[str],
# # # #     conversation_history: list[dict],
# # # #     language: str,
# # # # ):
# # # #     """
# # # #     Single-pass translation + RAG answer + conversational tone.
# # # #     Yields text chunks.
# # # #     """
# # # #     lang_name = LANG_NAMES.get(language, "English")
# # # #     context = "\n\n---\n\n".join(context_chunks)

# # # #     # Format history for the prompt
# # # #     history_text = ""
# # # #     if conversation_history:
# # # #         history_text = "CONVERSATION HISTORY:\n"
# # # #         for msg in conversation_history[-5:]: # Keep last 5 turns
# # # #             history_text += f"{msg['role'].upper()}: {msg['content']}\n"

# # # #     prompt = f"""You are Suvit Assistant — a friendly, warm customer support agent on a voice call.

# # # # The user just said something. It might be in English, Hindi, or Gujarati.
# # # # Listen to them, use the context provided, and answer their question.

# # # # {history_text}

# # # # CONTEXT FROM KNOWLEDGE BASE:
# # # # {context if context else "No specific context found. Answer generally or ask for clarification."}

# # # # USER'S LATEST MESSAGE:
# # # # "{transcript}"

# # # # RULES:
# # # # 1. Speak naturally, like a real person on a phone call.
# # # # 2. Keep it concise (1-3 sentences max). Nobody likes a long voice lecture.
# # # # 3. If they greet you, greet them back warmly.
# # # # 4. If you don't know the answer based on the context, politely say so.

# # # # IMPORTANT LANGUAGE RULE:
# # # # - Respond in {lang_name}
# # # # - If language is Hindi → respond in Hinglish (Hindi written in English script)
# # # # - If language is Gujarati → respond in Gujlish (Gujarati written in English script)
# # # # - Do NOT use pure Hindi (Devanagari) or Gujarati script!

# # # # Respond now:"""

# # # #     try:
# # # #         res_stream = openai_client.chat.completions.create(
# # # #             model=OPENAI_MODEL_NAME,
# # # #             messages=[{"role": "user", "content": prompt}],
# # # #             stream=True,
# # # #         )
# # # #         for chunk in res_stream:
# # # #             content = chunk.choices[0].delta.content
# # # #             if content:
# # # #                 yield content
# # # #     except Exception as oe:
# # # #         print(f"OpenAI conversational stream failed: {oe}. Falling back to Gemini.")
# # # #         try:
# # # #             response_stream = client.models.generate_content_stream(
# # # #                 model=MODEL_NAME, contents=prompt
# # # #             )
# # # #             for chunk in response_stream:
# # # #                 if chunk.text:
# # # #                     yield chunk.text
# # # #         except Exception as e:
# # # #             print(f"Gemini fallback failed: {e}")
# # # #             yield "I'm sorry, I'm having trouble connecting right now."


# # # """
# # # gemini_translate.py
# # # ────────────────────
# # # Language utilities for the voice agent:
# # #   - detect_language()        : identify en / hi / gu from transcript
# # #   - translate_to_english()   : convert any supported language → English
# # #   - generate_answer()        : RAG-grounded answer (non-streaming)
# # #   - generate_answer_stream() : RAG-grounded answer (streaming)

# # # Translation: OpenAI GPT-4o-mini (primary) → Gemini 2.5 Flash (fallback)
# # # Generation:  Gemini 2.5 Flash (primary)   → OpenAI GPT-4o-mini (fallback)
# # # """

# # # import os
# # # import ssl
# # # from openai import AsyncOpenAI
# # # from google import genai

# # # ssl._create_default_https_context = ssl._create_unverified_context


# # # # ---------------------------------------------------------------------------
# # # # Clients
# # # # ---------------------------------------------------------------------------

# # # openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# # # # google-genai uses GOOGLE_API_KEY from env automatically
# # # gemini_client = genai.Client()

# # # OPENAI_MODEL  = "gpt-4o-mini"
# # # GEMINI_MODEL  = "gemini-2.5-flash"

# # # LANG_NAMES = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}


# # # # ---------------------------------------------------------------------------
# # # # Language detection
# # # # ---------------------------------------------------------------------------

# # # async def detect_language(text: str) -> str:
# # #     """
# # #     Identify whether the transcript is English, Hindi, or Gujarati.

# # #     Fast Unicode scan first; LLM call only when the script is ambiguous
# # #     (e.g. romanised Hinglish that can't be caught by code-point ranges).
# # #     """
# # #     if not text:
# # #         return "en"

# # #     # Unicode block fast-path
# # #     if any("\u0900" <= c <= "\u097f" for c in text):   # Devanagari
# # #         return "hi"
# # #     if any("\u0a80" <= c <= "\u0aff" for c in text):   # Gujarati script
# # #         return "gu"

# # #     prompt = (
# # #         "Identify the language of the following text. "
# # #         "Reply with exactly one word: English, Hindi, or Gujarati.\n\n"
# # #         f"Text:\n{text}"
# # #     )

# # #     # OpenAI primary
# # #     try:
# # #         resp = await openai_client.chat.completions.create(
# # #             model=OPENAI_MODEL,
# # #             messages=[{"role": "user", "content": prompt}],
# # #             max_tokens=10,
# # #             temperature=0,
# # #         )
# # #         res = resp.choices[0].message.content.strip().lower()
# # #         if "hindi" in res:
# # #             return "hi"
# # #         if "gujarati" in res:
# # #             return "gu"
# # #         return "en"
# # #     except Exception as e:
# # #         print(f"[detect_language] OpenAI failed: {e} — trying Gemini")

# # #     # Gemini fallback
# # #     try:
# # #         resp = gemini_client.models.generate_content(
# # #             model=GEMINI_MODEL, contents=prompt
# # #         )
# # #         res = resp.text.strip().lower()
# # #         if "hindi" in res:
# # #             return "hi"
# # #         if "gujarati" in res:
# # #             return "gu"
# # #         return "en"
# # #     except Exception as e:
# # #         print(f"[detect_language] Gemini also failed: {e}")
# # #         return "en"


# # # # ---------------------------------------------------------------------------
# # # # Translation → English
# # # # ---------------------------------------------------------------------------

# # # async def translate_to_english(text: str, source_lang: str) -> str:
# # #     """
# # #     Translate text to English.
# # #     If it is already English, the model returns it unchanged.

# # #     Primary:  OpenAI GPT-4o-mini
# # #     Fallback: Gemini 2.5 Flash
# # #     """
# # #     if not text:
# # #         return text

# # #     # Skip the API call if language is already English
# # #     if source_lang == "en":
# # #         return text

# # #     prompt = (
# # #         "Translate the following text to English. "
# # #         "If it is already in English, return it exactly as-is. "
# # #         "Return ONLY the English translation — no explanation, no preamble.\n\n"
# # #         f"{text}"
# # #     )

# # #     # OpenAI primary
# # #     try:
# # #         resp = await openai_client.chat.completions.create(
# # #             model=OPENAI_MODEL,
# # #             messages=[{"role": "user", "content": prompt}],
# # #             temperature=0,
# # #         )
# # #         return resp.choices[0].message.content.strip()
# # #     except Exception as e:
# # #         print(f"[translate] OpenAI failed: {e} — trying Gemini")

# # #     # Gemini fallback
# # #     try:
# # #         resp = gemini_client.models.generate_content(
# # #             model=GEMINI_MODEL, contents=prompt
# # #         )
# # #         return resp.text.strip()
# # #     except Exception as e:
# # #         print(f"[translate] Gemini also failed: {e}")
# # #         return text   # last resort: return original


# # # async def translate_from_english(text: str, target_lang: str) -> str:
# # #     """
# # #     Translate English text to the requested target language.
# # #     If target is English, return unchanged text.
# # #     """
# # #     if not text:
# # #         return text
# # #     if target_lang == "en":
# # #         return text

# # #     target_name = LANG_NAMES.get(target_lang, "English")
# # #     prompt = (
# # #         f"Translate the following English text to {target_name}. "
# # #         "Return ONLY the translated text with no explanation.\n\n"
# # #         f"{text}"
# # #     )

# # #     # OpenAI primary
# # #     try:
# # #         resp = await openai_client.chat.completions.create(
# # #             model=OPENAI_MODEL,
# # #             messages=[{"role": "user", "content": prompt}],
# # #             temperature=0,
# # #         )
# # #         return resp.choices[0].message.content.strip()
# # #     except Exception as e:
# # #         print(f"[translate_back] OpenAI failed: {e} — trying Gemini")

# # #     # Gemini fallback
# # #     try:
# # #         resp = gemini_client.models.generate_content(
# # #             model=GEMINI_MODEL, contents=prompt
# # #         )
# # #         return resp.text.strip()
# # #     except Exception as e:
# # #         print(f"[translate_back] Gemini also failed: {e}")
# # #         return text


# # # # ---------------------------------------------------------------------------
# # # # Shared prompt builder
# # # # ---------------------------------------------------------------------------

# # # def _build_answer_prompt(
# # #     query_english: str,
# # #     context_chunks: list[str],
# # #     response_language: str,
# # # ) -> str:
# # #     lang_name = LANG_NAMES.get(response_language, "English")
# # #     context   = "\n\n---\n\n".join(context_chunks)

# # #     return f"""You are a customer support agent for Suvit (an automated Tally/software data import, mapping, and syncing service).
# # # Your goal is to assist customers politely, conversationally, and practically, using the exact support patterns found in real calls.

# # # CRITICAL RULES:
# # # 1. GREETING: If the user greets you or starts the call, always greet them back warmly, introduce yourself as the Suvit Support Team, and ask how you can help.
# # # 2. CLOSING: Always end your response with a helpful question or closing, e.g., "Iske alawa koi aur concern hai sir?" or "Aur koi help chahiye aapko?"
# # # 3. VOICE STYLE: Speak naturally like a real person on a phone call. Keep sentences short, simple, and polite. Avoid long explanations; explain things step-by-step.
# # # 4. LANGUAGE RULE (strictly mandatory):
# # #    - Respond in {lang_name}.
# # #    - You MUST respond using the NATIVE alphabet for the language (Devanagari for Hindi, Gujarati script for Gujarati). This ensures authentic pronunciation.
# # #    - NEVER write Hindi or Gujarati using English letters (Hinglish/Gujlish). It ruins the TTS accent.

# # # Suvit Technical Troubleshooting Context for reference:
# # # - UltraViewer/AnyDesk: If checking details on user's machine, suggest: "Aap UltraViewer connect karwa lijiye, main check kar leta hoon." or "AnyDesk ID share kijiye sir."
# # # - Spaces/Hashtags: Trailing spaces or blank spaces in ledger names cause sync/mapping errors. Instruct user to backspace/remove blank spaces and re-sync.
# # # - Multi-user access/Roles: Primary user sees all data. Secondary users need assigned companies and roles mapped.
# # # - Tax/GST Rates: If there is a single rate, map it directly. If mixed rates, add three columns (CGST, SGST, IGST) to the Excel sheet.
# # # - Auto Sync vs Manual Sync: Suggest clicking 'Manual Sync' or 'Sync Masters' if auto-sync is delayed.

# # # Answer the question using ONLY the provided context. If the answer is not in the context, politely mention it or offer to arrange a call back or training:
# # # "Main check karke aapko update karta hoon." or "Main aapke liye training arrange karwa deti hoon."

# # # Context:
# # # {context}

# # # Question:
# # # {query_english}"""


# # # # ---------------------------------------------------------------------------
# # # # Answer generation — non-streaming
# # # # ---------------------------------------------------------------------------

# # # async def generate_answer(
# # #     query_english: str,
# # #     context_chunks: list[str],
# # #     response_language: str,
# # # ) -> str:
# # #     """
# # #     Generate a RAG-grounded answer (full string, non-streaming).

# # #     Primary:  Gemini 2.5 Flash
# # #     Fallback: OpenAI GPT-4o-mini
# # #     """
# # #     prompt = _build_answer_prompt(query_english, context_chunks, response_language)

# # #     # Gemini primary
# # #     try:
# # #         resp = gemini_client.models.generate_content(
# # #             model=GEMINI_MODEL, contents=prompt
# # #         )
# # #         return resp.text.strip()
# # #     except Exception as e:
# # #         print(f"[generate] Gemini failed: {e} — trying OpenAI")

# # #     # OpenAI fallback
# # #     try:
# # #         resp = await openai_client.chat.completions.create(
# # #             model=OPENAI_MODEL,
# # #             messages=[{"role": "user", "content": prompt}],
# # #         )
# # #         return resp.choices[0].message.content.strip()
# # #     except Exception as e:
# # #         print(f"[generate] OpenAI also failed: {e}")
# # #         return "I'm having trouble generating a response. Please try again."


# # # # ---------------------------------------------------------------------------
# # # # Answer generation — streaming
# # # # ---------------------------------------------------------------------------

# # # async def generate_answer_stream(
# # #     query_english: str,
# # #     context_chunks: list[str],
# # #     response_language: str,
# # # ):
# # #     """
# # #     Streaming answer generator — yields text chunks as they arrive.

# # #     Primary:  Gemini 2.5 Flash streaming
# # #     Fallback: OpenAI GPT-4o-mini streaming
# # #     """
# # #     prompt = _build_answer_prompt(query_english, context_chunks, response_language)

# # #     # Gemini primary (streaming)
# # #     try:
# # #         stream = gemini_client.models.generate_content_stream(
# # #             model=GEMINI_MODEL, contents=prompt
# # #         )
# # #         for chunk in stream:
# # #             if chunk.text:
# # #                 yield chunk.text
# # #         return
# # #     except Exception as e:
# # #         print(f"[generate_stream] Gemini failed: {e} — trying OpenAI")

# # #     # OpenAI fallback (streaming)
# # #     try:
# # #         stream = await openai_client.chat.completions.create(
# # #             model=OPENAI_MODEL,
# # #             messages=[{"role": "user", "content": prompt}],
# # #             stream=True,
# # #         )
# # #         async for chunk in stream:
# # #             content = chunk.choices[0].delta.content
# # #             if content:
# # #                 yield content
# # #     except Exception as e:
# # #         print(f"[generate_stream] OpenAI also failed: {e}")
# # #         yield "I encountered an error generating a response. Please try again."


# # """
# # gemini_translate.py
# # ────────────────────
# # Language utilities for the voice agent (phone-call mode):
# #   - detect_language()        : identify en / hi / gu
# #   - translate_to_english()   : any supported language → English
# #   - generate_answer()        : RAG-grounded, multi-turn, phone-call style
# #   - generate_answer_stream() : same but streaming

# # Translation : OpenAI GPT-4o-mini (primary) → Gemini 2.5 Flash (fallback)
# # Generation  : Gemini 2.5 Flash (primary)   → OpenAI GPT-4o-mini (fallback)
# # """

# # import os
# # from typing import TYPE_CHECKING

# # from openai import AsyncOpenAI
# # from google import genai

# # if TYPE_CHECKING:
# #     from agents.state import ConversationTurn

# # # ---------------------------------------------------------------------------
# # # Clients
# # # ---------------------------------------------------------------------------

# # openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
# # gemini_client = genai.Client()   # reads GOOGLE_API_KEY automatically

# # OPENAI_MODEL = "gpt-4o-mini"
# # GEMINI_MODEL = "gemini-2.5-flash"

# # LANG_NAMES = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}

# # # Greeting lines per language — spoken on the very first turn of every call
# # GREETINGS = {
# #     "en": "Hello! I'm Suvit's support assistant. How can I help you today?",
# #     "hi": "Namaste! Main Suvit ka support assistant hoon. Aap kaise madad kar sakta hoon?",
# #     "gu": "Kem cho! Hoon Suvit no support assistant chhu. Hu tamari kem madad kari shakun?",
# # }


# # # ---------------------------------------------------------------------------
# # # Language detection
# # # ---------------------------------------------------------------------------

# # async def detect_language(text: str) -> str:
# #     """
# #     Identify whether the transcript is English, Hindi, or Gujarati.
# #     Unicode fast-path first; LLM only for ambiguous Roman-script text.
# #     """
# #     if not text:
# #         return "en"

# #     if any("\u0900" <= c <= "\u097f" for c in text):   # Devanagari
# #         return "hi"
# #     if any("\u0a80" <= c <= "\u0aff" for c in text):   # Gujarati script
# #         return "gu"

# #     prompt = (
# #         "Identify the language of the following text. "
# #         "Reply with exactly one word: English, Hindi, or Gujarati.\n\n"
# #         f"Text:\n{text}"
# #     )
# #     try:
# #         resp = await openai_client.chat.completions.create(
# #             model=OPENAI_MODEL,
# #             messages=[{"role": "user", "content": prompt}],
# #             max_tokens=10,
# #             temperature=0,
# #         )
# #         res = resp.choices[0].message.content.strip().lower()
# #         if "hindi" in res:
# #             return "hi"
# #         if "gujarati" in res:
# #             return "gu"
# #         return "en"
# #     except Exception as e:
# #         print(f"[detect_language] OpenAI failed: {e} — trying Gemini")

# #     try:
# #         resp = gemini_client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
# #         res = resp.text.strip().lower()
# #         if "hindi" in res:
# #             return "hi"
# #         if "gujarati" in res:
# #             return "gu"
# #         return "en"
# #     except Exception as e:
# #         print(f"[detect_language] Gemini also failed: {e}")
# #         return "en"


# # # ---------------------------------------------------------------------------
# # # Translation → English
# # # ---------------------------------------------------------------------------

# # async def translate_to_english(text: str, source_lang: str) -> str:
# #     """
# #     Translate text to English.
# #     Skips the API call entirely when source_lang == "en".
# #     Primary: OpenAI  |  Fallback: Gemini
# #     """
# #     if not text:
# #         return text
# #     if source_lang == "en":
# #         return text

# #     prompt = (
# #         "Translate the following text to English. "
# #         "If it is already in English, return it exactly as-is. "
# #         "Return ONLY the English translation — no explanation, no preamble.\n\n"
# #         f"{text}"
# #     )
# #     try:
# #         resp = await openai_client.chat.completions.create(
# #             model=OPENAI_MODEL,
# #             messages=[{"role": "user", "content": prompt}],
# #             temperature=0,
# #         )
# #         return resp.choices[0].message.content.strip()
# #     except Exception as e:
# #         print(f"[translate] OpenAI failed: {e} — trying Gemini")

# #     try:
# #         resp = gemini_client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
# #         return resp.text.strip()
# #     except Exception as e:
# #         print(f"[translate] Gemini also failed: {e}")
# #         return text


# # # ---------------------------------------------------------------------------
# # # Prompt builder  (phone-call system prompt)
# # # ---------------------------------------------------------------------------

# # def _build_system_prompt(response_language: str) -> str:
# #     lang_name = LANG_NAMES.get(response_language, "English")
# #     return f"""You are a real-time voice assistant for Suvit, behaving like a live phone call.

# # PERSONA
# # - Warm, professional support agent — like a real person on a call.
# # - Friendly, clear, and highly helpful. Do not be overly brief; provide full, thorough help.
# # - You are mid-conversation: no greetings unless it's the first turn.

# # LANGUAGE (mandatory)
# # - Respond in {lang_name}.
# # - Hindi  → Hinglish  (Hindi meaning, Roman script, e.g. "aap kaise help kar sakta hoon")
# # - Gujarati → Gujlish (Gujarati meaning, Roman script, e.g. "tame bank statement kevi rite upload kari shako cho")
# # - NEVER use Devanagari or Gujarati Unicode script.

# # RESPONSE STYLE
# # - Provide a complete, detailed, comprehensive step-by-step (A to Z) answer covering all retrieved information in a single go.
# # - Explain steps in a clear, sequential spoken format (e.g., use spoken transition words like "First, you need to...", "Next, you should...", "After that, please...", "Finally, you can...").
# # - No bullet points, no markdown headers or asterisks, no dash lists — write the entire detailed response in natural spoken paragraphs.
# # - No filler phrases like "Great question!" or "Certainly!".
# # - Never omit details, instructions, or steps found in the retrieved context; explain everything clearly and fully.

# # KNOWLEDGE
# # - Answer only from the provided context.
# # - If context doesn't cover it: "I don't have that info right now. Our support team can help."
# # - Never make up facts.

# # INTERRUPTION AWARENESS
# # - The user may interrupt. Respond naturally to what they last said.
# # - Do not repeat previous answers unless asked."""


# # def _build_history_messages(history: "list[ConversationTurn]") -> list[dict]:
# #     """Convert ConversationTurn history → OpenAI/Gemini message list."""
# #     messages = []
# #     for turn in history:
# #         role = "user" if turn.role == "user" else "assistant"
# #         messages.append({"role": role, "content": turn.text})
# #     return messages


# # def _build_user_message(
# #     query_english: str,
# #     context_chunks: list[str],
# # ) -> str:
# #     context = "\n\n---\n\n".join(context_chunks) if context_chunks else "No relevant context found."
# #     return f"""Context from knowledge base:
# # {context}

# # User's question:
# # {query_english}"""


# # # ---------------------------------------------------------------------------
# # # generate_answer — non-streaming, with history + greeting support
# # # ---------------------------------------------------------------------------

# # async def generate_answer(
# #     query_english: str,
# #     context_chunks: list[str],
# #     response_language: str,
# #     history: "list[ConversationTurn] | None" = None,
# #     is_greeting: bool = False,
# # ) -> str:
# #     """
# #     Generate a RAG-grounded phone-call-style answer.

# #     Args:
# #         query_english    : User's query translated to English
# #         context_chunks   : Retrieved KB chunks
# #         response_language: "en" | "hi" | "gu"
# #         history          : Previous ConversationTurns for multi-turn context
# #         is_greeting      : If True, returns a canned greeting without LLM call

# #     Primary: Gemini 2.5 Flash  |  Fallback: OpenAI GPT-4o-mini
# #     """
# #     # First turn of every call — return greeting immediately, no LLM needed
# #     if is_greeting:
# #         return GREETINGS.get(response_language, GREETINGS["en"])

# #     system_prompt  = _build_system_prompt(response_language)
# #     history_msgs   = _build_history_messages(history or [])
# #     user_content   = _build_user_message(query_english, context_chunks)

# #     # ── Gemini primary ──────────────────────────────────────────────────────
# #     try:
# #         # Build a single-string prompt for Gemini (it doesn't use chat format)
# #         history_text = ""
# #         for m in history_msgs:
# #             prefix = "User" if m["role"] == "user" else "Assistant"
# #             history_text += f"{prefix}: {m['content']}\n"

# #         full_prompt = f"{system_prompt}\n\n{history_text}User: {user_content}\nAssistant:"
# #         resp = gemini_client.models.generate_content(
# #             model=GEMINI_MODEL, contents=full_prompt
# #         )
# #         return resp.text.strip()
# #     except Exception as e:
# #         print(f"[generate] Gemini failed: {e} — trying OpenAI")

# #     # ── OpenAI fallback ─────────────────────────────────────────────────────
# #     try:
# #         messages = [{"role": "system", "content": system_prompt}]
# #         messages.extend(history_msgs)
# #         messages.append({"role": "user", "content": user_content})

# #         resp = await openai_client.chat.completions.create(
# #             model=OPENAI_MODEL, messages=messages
# #         )
# #         return resp.choices[0].message.content.strip()
# #     except Exception as e:
# #         print(f"[generate] OpenAI also failed: {e}")
# #         return "I'm having a little trouble right now. Please try again in a moment."


# # # ---------------------------------------------------------------------------
# # # generate_answer_stream — streaming version for low-latency audio
# # # ---------------------------------------------------------------------------

# # async def generate_answer_stream(
# #     query_english: str,
# #     context_chunks: list[str],
# #     response_language: str,
# #     history: "list[ConversationTurn] | None" = None,
# #     is_greeting: bool = False,
# # ):
# #     """
# #     Streaming answer generator — yields text chunks as they arrive.
# #     Primary: Gemini 2.5 Flash streaming  |  Fallback: OpenAI streaming
# #     """
# #     # First-turn greeting — yield immediately, no LLM latency
# #     if is_greeting:
# #         yield GREETINGS.get(response_language, GREETINGS["en"])
# #         return

# #     system_prompt = _build_system_prompt(response_language)
# #     history_msgs  = _build_history_messages(history or [])
# #     user_content  = _build_user_message(query_english, context_chunks)

# #     # ── Gemini streaming ────────────────────────────────────────────────────
# #     try:
# #         history_text = ""
# #         for m in history_msgs:
# #             prefix = "User" if m["role"] == "user" else "Assistant"
# #             history_text += f"{prefix}: {m['content']}\n"

# #         full_prompt = f"{system_prompt}\n\n{history_text}User: {user_content}\nAssistant:"
# #         stream = gemini_client.models.generate_content_stream(
# #             model=GEMINI_MODEL, contents=full_prompt
# #         )
# #         for chunk in stream:
# #             if chunk.text:
# #                 yield chunk.text
# #         return
# #     except Exception as e:
# #         print(f"[generate_stream] Gemini failed: {e} — trying OpenAI")

# #     # ── OpenAI fallback streaming ───────────────────────────────────────────
# #     try:
# #         messages = [{"role": "system", "content": system_prompt}]
# #         messages.extend(history_msgs)
# #         messages.append({"role": "user", "content": user_content})

# #         stream = await openai_client.chat.completions.create(
# #             model=OPENAI_MODEL, messages=messages, stream=True
# #         )
# #         async for chunk in stream:
# #             content = chunk.choices[0].delta.content
# #             if content:
# #                 yield content
# #     except Exception as e:
# #         print(f"[generate_stream] OpenAI also failed: {e}")
# #         yield "I'm having a little trouble right now. Please try again."


#     """
#     gemini_translate.py
#     ────────────────────
#     Language utilities for the voice agent (phone-call mode):
#     - detect_language()        : identify en / hi / gu
#     - translate_to_english()   : any supported language → English
#     - generate_answer()        : RAG-grounded, multi-turn, phone-call style
#     - generate_answer_stream() : same but streaming

#     Translation : OpenAI GPT-4o-mini (primary) → Gemini 2.5 Flash (fallback)
#     Generation  : Gemini 2.5 Flash (primary)   → OpenAI GPT-4o-mini (fallback)
#     """

#     import os
#     from typing import TYPE_CHECKING

#     from openai import AsyncOpenAI
#     from google import genai

#     if TYPE_CHECKING:
#         from agents.state import ConversationTurn

#     # ---------------------------------------------------------------------------
#     # Clients
#     # ---------------------------------------------------------------------------

#     openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
#     gemini_client = genai.Client()   # reads GOOGLE_API_KEY automatically

#     OPENAI_MODEL = "gpt-4o-mini"
#     GEMINI_MODEL = "gemini-2.5-flash"

#     LANG_NAMES = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}

#     # Greeting lines per language — spoken on the very first turn of every call
#     GREETINGS = {
#         "en": "Hello! I'm Suvit's support assistant. How can I help you today?",
#         "hi": "Namaste! Main Suvit ka support assistant hoon. Aap kaise madad kar sakta hoon?",
#         "gu": "Kem cho! Hoon Suvit no support assistant chhu. Hu tamari kem madad kari shakun?",
#     }


#     # ---------------------------------------------------------------------------
#     # Language detection
#     # ---------------------------------------------------------------------------

#     async def detect_language(text: str) -> str:
#         """
#         Identify whether the transcript is English, Hindi, or Gujarati.
#         Unicode fast-path first; LLM only for ambiguous Roman-script text.
#         """
#         if not text:
#             return "en"

#         if any("\u0900" <= c <= "\u097f" for c in text):   # Devanagari
#             return "hi"
#         if any("\u0a80" <= c <= "\u0aff" for c in text):   # Gujarati script
#             return "gu"

#         prompt = (
#             "Identify the language of the following text. "
#             "Reply with exactly one word: English, Hindi, or Gujarati.\n\n"
#             f"Text:\n{text}"
#         )
#         try:
#             resp = await openai_client.chat.completions.create(
#                 model=OPENAI_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=10,
#                 temperature=0,
#             )
#             res = resp.choices[0].message.content.strip().lower()
#             if "hindi" in res:
#                 return "hi"
#             if "gujarati" in res:
#                 return "gu"
#             return "en"
#         except Exception as e:
#             print(f"[detect_language] OpenAI failed: {e} — trying Gemini")

#         try:
#             resp = gemini_client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
#             res = resp.text.strip().lower()
#             if "hindi" in res:
#                 return "hi"
#             if "gujarati" in res:
#                 return "gu"
#             return "en"
#         except Exception as e:
#             print(f"[detect_language] Gemini also failed: {e}")
#             return "en"


#     # ---------------------------------------------------------------------------
#     # Translation → English
#     # ---------------------------------------------------------------------------

#     async def translate_to_english(text: str, source_lang: str) -> str:
#         """
#         Translate text to English.
#         Skips the API call entirely when source_lang == "en".
#         Primary: OpenAI  |  Fallback: Gemini
#         """
#         if not text:
#             return text
#         if source_lang == "en":
#             return text

#         prompt = (
#             "Translate the following text to English. "
#             "If it is already in English, return it exactly as-is. "
#             "Return ONLY the English translation — no explanation, no preamble.\n\n"
#             f"{text}"
#         )
#         try:
#             resp = await openai_client.chat.completions.create(
#                 model=OPENAI_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0,
#             )
#             return resp.choices[0].message.content.strip()
#         except Exception as e:
#             print(f"[translate] OpenAI failed: {e} — trying Gemini")

#         try:
#             resp = gemini_client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
#             return resp.text.strip()
#         except Exception as e:
#             print(f"[translate] Gemini also failed: {e}")
#             return text


#     # ---------------------------------------------------------------------------
#     # Prompt builder  (phone-call system prompt)
#     # ---------------------------------------------------------------------------

#     def _build_system_prompt(response_language: str) -> str:
#         lang_name = LANG_NAMES.get(response_language, "English")
#         return f"""You are a real-time voice assistant for Suvit on a live phone call.

#     LANGUAGE — mandatory, no exceptions:
#     - Always respond in {lang_name}.
#     - Hindi → Hinglish: Hindi words written in Roman/English script. Example: "aap Settings mein jaayein, phir Users select karein."
#     - Gujarati → Gujlish: Gujarati words written in Roman/English script. Example: "tame Settings ma jao, pachhi Users select karo."
#     - NEVER output Devanagari (हिंदी) or Gujarati (ગુજરાતી) Unicode script — TTS cannot read it.

#     RESPONSE LENGTH — this is the most important rule:
#     - Maximum 2 short sentences per reply. Hard limit. No exceptions.
#     - Each sentence must be under 15 words.
#     - If steps are needed, give ONE step per turn. Wait for user to respond before giving the next step.
#     - NEVER give a full list of steps in one reply.

#     STYLE:
#     - Speak like a support agent on a phone call — natural, warm, direct.
#     - No bullet points, no numbered lists, no markdown, no asterisks.
#     - No filler: never say "Great question!", "Certainly!", "Of course!".
#     - No preamble: answer immediately.

#     KNOWLEDGE:
#     - Use ONLY the provided context. Never guess or make up steps.
#     - If not in context: "I don't have that info. Please contact our support team."

#     EXAMPLE good reply (English): "Go to the Users section and click Add New User."
#     EXAMPLE bad reply: "Sure! To create a user, you need to first navigate to the Settings page, then look for the Users & Roles section, click on it, and then you will see an Add New User button which you can click to proceed." ← TOO LONG, never do this."""


#     def _build_history_messages(history: "list[ConversationTurn]") -> list[dict]:
#         """Convert ConversationTurn history → OpenAI/Gemini message list."""
#         messages = []
#         for turn in history:
#             role = "user" if turn.role == "user" else "assistant"
#             messages.append({"role": role, "content": turn.text})
#         return messages


#     def _build_user_message(
#         query_english: str,
#         context_chunks: list[str],
#     ) -> str:
#         context = "\n\n---\n\n".join(context_chunks) if context_chunks else "No relevant context found."
#         return f"""Context from knowledge base:
#     {context}

#     User's question:
#     {query_english}"""


#     # ---------------------------------------------------------------------------
#     # generate_answer — non-streaming, with history + greeting support
#     # ---------------------------------------------------------------------------

#     async def generate_answer(
#         query_english: str,
#         context_chunks: list[str],
#         response_language: str,
#         history: "list[ConversationTurn] | None" = None,
#         is_greeting: bool = False,
#     ) -> str:
#         """
#         Generate a RAG-grounded phone-call-style answer.

#         Args:
#             query_english    : User's query translated to English
#             context_chunks   : Retrieved KB chunks
#             response_language: "en" | "hi" | "gu"
#             history          : Previous ConversationTurns for multi-turn context
#             is_greeting      : If True, returns a canned greeting without LLM call

#         Primary: Gemini 2.5 Flash  |  Fallback: OpenAI GPT-4o-mini
#         """
#         # First turn of every call — return greeting immediately, no LLM needed
#         if is_greeting:
#             return GREETINGS.get(response_language, GREETINGS["en"])

#         system_prompt  = _build_system_prompt(response_language)
#         history_msgs   = _build_history_messages(history or [])
#         user_content   = _build_user_message(query_english, context_chunks)

#         # ── Gemini primary ──────────────────────────────────────────────────────
#         try:
#             # Build a single-string prompt for Gemini (it doesn't use chat format)
#             history_text = ""
#             for m in history_msgs:
#                 prefix = "User" if m["role"] == "user" else "Assistant"
#                 history_text += f"{prefix}: {m['content']}\n"

#             full_prompt = f"{system_prompt}\n\n{history_text}User: {user_content}\nAssistant:"
#             resp = gemini_client.models.generate_content(
#                 model=GEMINI_MODEL, contents=full_prompt
#             )
#             return resp.text.strip()
#         except Exception as e:
#             print(f"[generate] Gemini failed: {e} — trying OpenAI")

#         # ── OpenAI fallback ─────────────────────────────────────────────────────
#         try:
#             messages = [{"role": "system", "content": system_prompt}]
#             messages.extend(history_msgs)
#             messages.append({"role": "user", "content": user_content})

#             resp = await openai_client.chat.completions.create(
#                 model=OPENAI_MODEL, messages=messages
#             )
#             return resp.choices[0].message.content.strip()
#         except Exception as e:
#             print(f"[generate] OpenAI also failed: {e}")
#             return "I'm having a little trouble right now. Please try again in a moment."


#     # ---------------------------------------------------------------------------
#     # generate_answer_stream — streaming version for low-latency audio
#     # ---------------------------------------------------------------------------

#     async def generate_answer_stream(
#         query_english: str,
#         context_chunks: list[str],
#         response_language: str,
#         history: "list[ConversationTurn] | None" = None,
#         is_greeting: bool = False,
#     ):
#         """
#         Streaming answer generator — yields text chunks as they arrive.
#         Primary: Gemini 2.5 Flash streaming  |  Fallback: OpenAI streaming
#         """
#         # First-turn greeting — yield immediately, no LLM latency
#         if is_greeting:
#             yield GREETINGS.get(response_language, GREETINGS["en"])
#             return

#         system_prompt = _build_system_prompt(response_language)
#         history_msgs  = _build_history_messages(history or [])
#         user_content  = _build_user_message(query_english, context_chunks)

#         # ── Gemini streaming ────────────────────────────────────────────────────
#         try:
#             history_text = ""
#             for m in history_msgs:
#                 prefix = "User" if m["role"] == "user" else "Assistant"
#                 history_text += f"{prefix}: {m['content']}\n"

#             full_prompt = f"{system_prompt}\n\n{history_text}User: {user_content}\nAssistant:"
#             stream = gemini_client.models.generate_content_stream(
#                 model=GEMINI_MODEL, contents=full_prompt
#             )
#             for chunk in stream:
#                 if chunk.text:
#                     yield chunk.text
#             return
#         except Exception as e:
#             print(f"[generate_stream] Gemini failed: {e} — trying OpenAI")

#         # ── OpenAI fallback streaming ───────────────────────────────────────────
#         try:
#             messages = [{"role": "system", "content": system_prompt}]
#             messages.extend(history_msgs)
#             messages.append({"role": "user", "content": user_content})

#             stream = await openai_client.chat.completions.create(
#                 model=OPENAI_MODEL, messages=messages, stream=True
#             )
#             async for chunk in stream:
#                 content = chunk.choices[0].delta.content
#                 if content:
#                     yield content
#         except Exception as e:
#             print(f"[generate_stream] OpenAI also failed: {e}")
#             yield "I'm having a little trouble right now. Please try again."


"""
gemini_translate.py
────────────────────
Language utilities for the voice agent (phone-call mode):
  - detect_language()        : identify en / hi / gu
  - translate_to_english()   : any supported language → English
  - generate_answer()        : RAG-grounded, multi-turn, phone-call style
  - generate_answer_stream() : same but streaming

Translation : OpenAI GPT-4o-mini (primary) → Gemini 2.5 Flash (fallback)
Generation  : Gemini 2.5 Flash (primary)   → OpenAI GPT-4o-mini (fallback)
"""

import os
from typing import TYPE_CHECKING

from openai import AsyncOpenAI
from google import genai

if TYPE_CHECKING:
    from agents.state import ConversationTurn

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
gemini_client = genai.Client()  # reads GOOGLE_API_KEY automatically

OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "gemini-2.5-flash"

LANG_NAMES = {"en": "English", "hi": "Hindi", "gu": "Gujarati"}

# Greeting lines per language — spoken on the very first turn of every call
GREETINGS = {
    "en": "Hello! I'm Suvit's support assistant. How can I help you today?",
    "hi": "Namaste! Main Suvit ka support assistant hoon. Aap kaise madad kar sakta hoon?",
    "gu": "Kem cho! Hoon Suvit no support assistant chhu. Hu tamari kem madad kari shakun?",
}


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------


async def detect_language(text: str) -> str:
    """
    Identify whether the transcript is English, Hindi, or Gujarati.
    Unicode fast-path first; LLM only for ambiguous Roman-script text.
    """
    if not text:
        return "en"

    if any("\u0900" <= c <= "\u097f" for c in text):  # Devanagari
        return "hi"
    if any("\u0a80" <= c <= "\u0aff" for c in text):  # Gujarati script
        return "gu"

    prompt = (
        "Identify the language of the following text. "
        "Reply with exactly one word: English, Hindi, or Gujarati.\n\n"
        f"Text:\n{text}"
    )
    try:
        resp = await openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0,
        )
        res = resp.choices[0].message.content.strip().lower()
        if "hindi" in res:
            return "hi"
        if "gujarati" in res:
            return "gu"
        return "en"
    except Exception as e:
        print(f"[detect_language] OpenAI failed: {e} — trying Gemini")

    try:
        resp = gemini_client.models.generate_content(
            model=GEMINI_MODEL, contents=prompt
        )
        res = resp.text.strip().lower()
        if "hindi" in res:
            return "hi"
        if "gujarati" in res:
            return "gu"
        return "en"
    except Exception as e:
        print(f"[detect_language] Gemini also failed: {e}")
        return "en"


# ---------------------------------------------------------------------------
# Translation → English
# ---------------------------------------------------------------------------


async def translate_to_english(text: str, source_lang: str) -> str:
    """
    Translate text to English.
    Skips the API call entirely when source_lang == "en".
    Primary: OpenAI  |  Fallback: Gemini
    """
    if not text:
        return text
    if source_lang == "en":
        return text

    prompt = (
        "Translate the following text to English. "
        "If it is already in English, return it exactly as-is. "
        "Return ONLY the English translation — no explanation, no preamble.\n\n"
        f"{text}"
    )
    try:
        resp = await openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[translate] OpenAI failed: {e} — trying Gemini")

    try:
        resp = gemini_client.models.generate_content(
            model=GEMINI_MODEL, contents=prompt
        )
        return resp.text.strip()
    except Exception as e:
        print(f"[translate] Gemini also failed: {e}")
        return text


# ---------------------------------------------------------------------------
# Prompt builder  (phone-call system prompt)
# ---------------------------------------------------------------------------


def _build_system_prompt(response_language: str) -> str:
    lang_name = LANG_NAMES.get(response_language, "English")
    return f"""You are a real-time voice assistant for Suvit on a live phone call.
    LANGUAGE (mandatory)
    - Respond in {lang_name}.
    - Hindi  → Hinglish  (Hindi meaning, Roman script, e.g. "aap kaise help kar sakta hoon")
    - Gujarati → Gujlish (Gujarati meaning, Roman script, e.g. "tame bank statement kevi rite upload kari shako cho")
    - NEVER use Devanagari or Gujarati Unicode script.

    RESPONSE STYLE
    - Provide a complete, detailed, comprehensive step-by-step (A to Z) answer covering all retrieved information in a single go.
    - Explain steps in a clear, sequential spoken format (e.g., use spoken transition words like "First, you need to...", "Next, you should...", "After that, please...", "Finally, you can...").
    - No bullet points, no markdown headers or asterisks, no dash lists — write the entire detailed response in natural spoken paragraphs.
    - No filler phrases like "Great question!" or "Certainly!".
    - Never omit details, instructions, or steps found in the retrieved context; explain everything clearly and fully.

    KNOWLEDGE
    - Answer only from the provided context.
    - If context doesn't cover it: "I don't have that info right now. Our support team can help."
    - Never make up facts.

    INTERRUPTION AWARENESS
    - The user may interrupt. Respond naturally to what they last said.
    - Do not repeat previous answers unless asked.
 
    EXAMPLE good reply (English): "Go to the Users section and click Add New User."
    EXAMPLE bad reply: "Sure! To create a user, you need to first navigate to the Settings page, then look for the Users & Roles section, click on it, and then you will see an Add New User button which you can click to proceed." ← TOO LONG, never do this."""


def _build_history_messages(history: "list[ConversationTurn]") -> list[dict]:
    """Convert ConversationTurn history → OpenAI/Gemini message list."""
    messages = []
    for turn in history:
        role = "user" if turn.role == "user" else "assistant"
        messages.append({"role": role, "content": turn.text})
    return messages


def _build_user_message(
    query_english: str,
    context_chunks: list[str],
) -> str:
    context = (
        "\n\n---\n\n".join(context_chunks)
        if context_chunks
        else "No relevant context found."
    )
    return f"""Context from knowledge base:
{context}

User's question:
{query_english}"""


# ---------------------------------------------------------------------------
# generate_answer — non-streaming, with history + greeting support
# ---------------------------------------------------------------------------


async def generate_answer(
    query_english: str,
    context_chunks: list[str],
    response_language: str,
    history: "list[ConversationTurn] | None" = None,
    is_greeting: bool = False,
) -> str:
    """
    Generate a RAG-grounded phone-call-style answer.

    Args:
        query_english    : User's query translated to English
        context_chunks   : Retrieved KB chunks
        response_language: "en" | "hi" | "gu"
        history          : Previous ConversationTurns for multi-turn context
        is_greeting      : If True, returns a canned greeting without LLM call

    Primary: Gemini 2.5 Flash  |  Fallback: OpenAI GPT-4o-mini
    """
    # First turn of every call — return greeting immediately, no LLM needed
    if is_greeting:
        return GREETINGS.get(response_language, GREETINGS["en"])

    system_prompt = _build_system_prompt(response_language)
    history_msgs = _build_history_messages(history or [])
    user_content = _build_user_message(query_english, context_chunks)

    # ── Gemini primary ──────────────────────────────────────────────────────
    try:
        # Build a single-string prompt for Gemini (it doesn't use chat format)
        history_text = ""
        for m in history_msgs:
            prefix = "User" if m["role"] == "user" else "Assistant"
            history_text += f"{prefix}: {m['content']}\n"

        full_prompt = (
            f"{system_prompt}\n\n{history_text}User: {user_content}\nAssistant:"
        )
        resp = gemini_client.models.generate_content(
            model=GEMINI_MODEL, contents=full_prompt
        )
        return resp.text.strip()
    except Exception as e:
        print(f"[generate] Gemini failed: {e} — trying OpenAI")

    # ── OpenAI fallback ─────────────────────────────────────────────────────
    try:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history_msgs)
        messages.append({"role": "user", "content": user_content})

        resp = await openai_client.chat.completions.create(
            model=OPENAI_MODEL, messages=messages
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[generate] OpenAI also failed: {e}")
        return "I'm having a little trouble right now. Please try again in a moment."


# ---------------------------------------------------------------------------
# generate_answer_stream — streaming version for low-latency audio
# ---------------------------------------------------------------------------


async def generate_answer_stream(
    query_english: str,
    context_chunks: list[str],
    response_language: str,
    history: "list[ConversationTurn] | None" = None,
    is_greeting: bool = False,
):
    """
    Streaming answer generator — yields text chunks as they arrive.
    Primary: Gemini 2.5 Flash streaming  |  Fallback: OpenAI streaming
    """
    # First-turn greeting — yield immediately, no LLM latency
    if is_greeting:
        yield GREETINGS.get(response_language, GREETINGS["en"])
        return

    system_prompt = _build_system_prompt(response_language)
    history_msgs = _build_history_messages(history or [])
    user_content = _build_user_message(query_english, context_chunks)

    # ── Gemini streaming ────────────────────────────────────────────────────
    try:
        history_text = ""
        for m in history_msgs:
            prefix = "User" if m["role"] == "user" else "Assistant"
            history_text += f"{prefix}: {m['content']}\n"

        full_prompt = (
            f"{system_prompt}\n\n{history_text}User: {user_content}\nAssistant:"
        )
        stream = gemini_client.models.generate_content_stream(
            model=GEMINI_MODEL, contents=full_prompt
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text
        return
    except Exception as e:
        print(f"[generate_stream] Gemini failed: {e} — trying OpenAI")

    # ── OpenAI fallback streaming ───────────────────────────────────────────
    try:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history_msgs)
        messages.append({"role": "user", "content": user_content})

        stream = await openai_client.chat.completions.create(
            model=OPENAI_MODEL, messages=messages, stream=True
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        print(f"[generate_stream] OpenAI also failed: {e}")
        yield "I'm having a little trouble right now. Please try again."
