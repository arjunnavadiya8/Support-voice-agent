# # from langgraph.graph import StateGraph, END
# # from agents.state import VoiceState
# # from agents.nodes import (
# #     node_transcribe,
# #     node_translate,
# #     node_retrieve,
# #     node_generate,
# #     node_synthesize,
# # )


# # def build_graph():
# #     g = StateGraph(VoiceState)

# #     g.add_node("transcribe", node_transcribe)
# #     g.add_node("translate", node_translate)
# #     g.add_node("retrieve", node_retrieve)
# #     g.add_node("generate", node_generate)
# #     g.add_node("synthesize", node_synthesize)

# #     g.set_entry_point("transcribe")
# #     g.add_edge("transcribe", "translate")
# #     g.add_edge("translate", "retrieve")
# #     g.add_edge("retrieve", "generate")
# #     g.add_edge("generate", "synthesize")
# #     g.add_edge("synthesize", END)

# #     return g.compile()


# # agent_graph = build_graph()







# from langgraph.graph import StateGraph, END
# from agents.state import VoiceState
# from agents.nodes import (
#     node_transcribe,
#     node_detect_language,
#     node_translate,
#     node_retrieve,
#     node_generate,
#     node_synthesize,
# )


# def build_graph():
#     g = StateGraph(VoiceState)

#     g.add_node("transcribe",       node_transcribe)
#     g.add_node("detect_language",  node_detect_language)
#     g.add_node("translate",        node_translate)
#     g.add_node("retrieve",         node_retrieve)
#     g.add_node("generate",         node_generate)
#     g.add_node("synthesize",       node_synthesize)

#     g.set_entry_point("transcribe")
#     g.add_edge("transcribe",      "detect_language")
#     g.add_edge("detect_language", "translate")
#     g.add_edge("translate",       "retrieve")
#     g.add_edge("retrieve",        "generate")
#     g.add_edge("generate",        "synthesize")
#     g.add_edge("synthesize",       END)

#     return g.compile()


# agent_graph = build_graph()









from langgraph.graph import StateGraph, END
from agents.state import VoiceState
from agents.nodes import (
    node_transcribe,
    node_detect_language,
    node_translate,
    node_retrieve,
    node_generate,
    node_synthesize,
)


def build_graph():
    g = StateGraph(VoiceState)

    g.add_node("transcribe",       node_transcribe)
    g.add_node("detect_language",  node_detect_language)
    g.add_node("translate",        node_translate)
    g.add_node("retrieve",         node_retrieve)
    g.add_node("generate",         node_generate)
    g.add_node("synthesize",       node_synthesize)

    g.set_entry_point("transcribe")
    g.add_edge("transcribe",      "detect_language")
    g.add_edge("detect_language", "translate")
    g.add_edge("translate",       "retrieve")
    g.add_edge("retrieve",        "generate")
    g.add_edge("generate",        "synthesize")
    g.add_edge("synthesize",       END)

    return g.compile()


agent_graph = build_graph()