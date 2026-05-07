import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
INDEX_DIR = os.path.join(os.path.dirname(__file__), "index")

def ingest():
    md_files = glob.glob(os.path.join(DOCS_DIR, "*.md"))
    if not md_files:
        print(f"No .md files found in {DOCS_DIR}")
        print(f"Put your .md files in: {DOCS_DIR}")
        return

    raw_docs = []
    for path in md_files:
        with open(path, "r", encoding="utf-8") as f:
            raw_docs.append(Document(page_content=f.read(), metadata={"source": path}))
        print(f"Loaded: {path}")

    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = splitter.split_documents(raw_docs)
    print(f"Created {len(chunks)} chunks from {len(md_files)} files")

    print("Loading embedding model (first run downloads ~90MB)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"local_files_only": True}
    )

    print("Building FAISS index...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_DIR)
    print(f"Done. Index saved to {INDEX_DIR}")

if __name__ == "__main__":
    ingest()