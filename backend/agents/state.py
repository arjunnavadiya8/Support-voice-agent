# # from dataclasses import dataclass, field
# # from typing import Optional


# # @dataclass
# # class VoiceState:
# #     audio_bytes: bytes = b""
# #     transcript: str = ""
# #     detected_language: str = "en"  # "en" | "hi" | "gu"
# #     english_query: str = ""  # always English for RAG
# #     retrieved_chunks: list[str] = field(default_factory=list)
# #     answer_text: str = ""
# #     audio_response: bytes = b""
# #     error: Optional[str] = None








# from dataclasses import dataclass, field
# from typing import Optional


# @dataclass
# class ConversationTurn:
#     role: str       # "user" | "assistant"
#     text: str
#     language: str   # "en" | "hi" | "gu"


# @dataclass
# class VoiceState:
#     audio_bytes: bytes = b""
#     transcript: str = ""
#     detected_language: str = "en"        # "en" | "hi" | "gu"
#     english_query: str = ""              # always English for RAG
#     retrieved_chunks: list[str] = field(default_factory=list)
#     answer_text: str = ""
#     audio_response: bytes = b""
#     error: Optional[str] = None

#     # Phone-call context: full conversation history for multi-turn continuity
#     history: list[ConversationTurn] = field(default_factory=list)

#     # Call lifecycle flags
#     is_greeting: bool = False            # True on the very first turn
#     call_ended: bool = False
















from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ConversationTurn:
    role: str       # "user" | "assistant"
    text: str
    language: str   # "en" | "hi" | "gu"


@dataclass
class VoiceState:
    audio_bytes: bytes = b""
    transcript: str = ""
    detected_language: str = "en"        # "en" | "hi" | "gu"
    english_query: str = ""              # always English for RAG
    retrieved_chunks: list[str] = field(default_factory=list)
    answer_text: str = ""
    audio_response: bytes = b""
    error: Optional[str] = None

    # Phone-call context: full conversation history for multi-turn continuity
    history: list[ConversationTurn] = field(default_factory=list)

    # Call lifecycle flags
    is_greeting: bool = False            # True on the very first turn
    call_ended: bool = False