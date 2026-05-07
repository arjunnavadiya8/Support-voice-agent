import logging
import os
from typing import Annotated
from dotenv import load_dotenv

from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.plugins import deepgram, openai, silero

# Try to import VoiceAssistant (1.x) or VoicePipelineAgent (0.x fallback)
try:
    from livekit.agents.voice_assistant import VoiceAssistant as VoiceAgent
except ImportError:
    try:
        from livekit.agents.pipeline import VoicePipelineAgent as VoiceAgent
    except ImportError:
        raise ImportError(
            "Could not import VoiceAssistant or VoicePipelineAgent from livekit.agents."
        )

from kb.retriever import retrieve

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("suvit-agent")


# ─── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a premium, friendly, and extremely helpful real-time voice support assistant for Suvit.

Rules:
- Identify whether the user is speaking English, Hindi (Hinglish), or Gujarati (Gujlish), and respond in that same language.
- Provide complete, comprehensive, and detailed A-to-Z instructions where relevant.
- Speak in natural paragraphs. Use conversational transition words like "First", "Next", "After that", and "Finally" to explain steps.
- STRICTLY DO NOT use any markdown formatting (such as bullet points, asterisks, headers, or lists) in your output. It ruins the voice synthesis.
- Use the 'search_knowledge_base' tool whenever a user asks a question about Suvit's features, client accounts, user management, roles, bank statements, imports, or other support topics.
- Keep the tone polite, natural, and friendly—exactly like a premium human phone support agent.
"""


# ─── Function Context (RAG Tool) ──────────────────────────────────────────────


class SuvitKnowledgeTool(llm.FunctionContext):
    @llm.ai_callable(
        description=(
            "Search the Suvit support documentation/knowledge base for answers "
            "about importing data, bank statements, client accounts, users, "
            "roles, and other support issues."
        )
    )
    async def search_knowledge_base(
        self,
        query: Annotated[
            str,
            llm.TypeInfo(description="The search query in plain English"),
        ],
    ) -> str:
        logger.info(f"RAG Tool: Searching knowledge base for query: '{query}'")
        try:
            chunks = retrieve(query, k=5)
            if not chunks:
                return "No matching Suvit documentation found."

            context = "\n\n---\n\n".join(chunks)
            logger.info(f"RAG Tool: Found {len(chunks)} matching chunks.")
            return context
        except Exception as e:
            logger.error(f"RAG Tool failed: {e}")
            return f"Error retrieving context: {e}"


# ─── Entry Point ──────────────────────────────────────────────────────────────


async def entrypoint(ctx: JobContext):
    logger.info("Agent job starting. Connecting to LiveKit room...")

    # Configure initial chat context
    chat_ctx = llm.ChatContext().append(
        role="system",
        text=SYSTEM_PROMPT,
    )

    # Initialize the voice agent with Silero VAD, Deepgram STT, OpenAI LLM, and OpenAI TTS
    # Passes SuvitKnowledgeTool as the function context
    agent = VoiceAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(),
        chat_ctx=chat_ctx,
        fnc_ctx=SuvitKnowledgeTool(),
    )

    # Connect to room (audio only for voice agent)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info(f"Connected to room: {ctx.room.name}. Starting agent...")

    # Start the agent pipeline
    agent.start(ctx.room)

    # Say a friendly custom greeting when joining
    await agent.say(
        "Hello! I am your Suvit support voice assistant. How can I help you today?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
