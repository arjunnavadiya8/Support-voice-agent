import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

INDEX_DIR = os.path.join(os.path.dirname(__file__), "index")

_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={"local_files_only": True}
        )
        _vectorstore = FAISS.load_local(
            INDEX_DIR, embeddings, allow_dangerous_deserialization=True
        )
    return _vectorstore

def retrieve(query: str, k: int = 5) -> list[str]:
    print(f"[RETRIEVER] Searching context for: {query}")
    vs = get_vectorstore()
    docs = vs.similarity_search(query, k=k)
    print(f"[RETRIEVER] Found {len(docs)} chunks.")
    return [d.page_content for d in docs]