# ================================
# RAG MEMORY SYSTEM (DOCUMENT BRAIN)
# ================================

# This file creates long-term memory for our chatbot.
# Instead of AI guessing answers, it will search inside uploaded files.

# ------------------------------------------------
# Import required libraries
# ------------------------------------------------

# Reads PDF files and converts them into readable text documents
from langchain_community.document_loaders import PyPDFLoader

# Splits large text into smaller overlapping pieces (important for LLM context)
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Converts text → vectors (numbers representing meaning)
# Using free local embedding model (no API cost)
from langchain_huggingface import HuggingFaceEmbeddings


# Vector database to store embeddings (acts like AI memory)
from langchain_community.vectorstores import Chroma


# Folder where memory database will be saved
DB_PATH = "app/vector_store"


# ============================================================
# FUNCTION 1 — INGEST DOCUMENT INTO MEMORY
# Called when user uploads a PDF
# ============================================================

def ingest_pdf(pdf_path):

    # -------- STEP 1: LOAD PDF --------
    # Convert each page of PDF into text document objects
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Example:
    # 10 page PDF → 10 Document objects


    # -------- STEP 2: SPLIT INTO SMALL CHUNKS --------
    # LLM cannot read large documents directly
    # So we break into small overlapping paragraphs

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,      # smaller chunks → more precise retrieval
        chunk_overlap=80,    # still keeps context
        separators=["\n\n", "\n", ".", " ", ""]
    )


    chunks = splitter.split_documents(documents)

    # Example:
    # 10 pages → ~120 small paragraphs


    # -------- STEP 3: CREATE EMBEDDINGS --------
    # Convert text meaning into numbers (vectors)
    # Similar meaning → similar vectors

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Example:
    # "tumor detected" → [0.234, -0.884, 0.113 ...]


    # -------- STEP 4: STORE INTO VECTOR DATABASE --------
    # This becomes chatbot memory

    db = Chroma.from_documents(
        chunks,                    # text pieces
        embeddings,                # convert to vectors
        persist_directory=DB_PATH  # save location
    )

    # Physically save memory on disk
    db.persist()

    print("PDF successfully stored in AI memory")


# ============================================================
# FUNCTION 2 — SEARCH RELEVANT KNOWLEDGE
# Called when user asks a question
# ============================================================

def search_docs(query):

    # -------- STEP 1: LOAD SAME EMBEDDING MODEL --------
    # Must match ingest embedding model for similarity to work
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


    # -------- STEP 2: LOAD VECTOR DATABASE --------
    # This loads stored memory
    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )


    # -------- STEP 3: FIND MOST RELEVANT TEXT --------
    # Convert question → vector → compare with stored vectors

    docs = db.similarity_search(query, k=8)

    # k=4 means return top 4 most relevant paragraphs


    # -------- STEP 4: MERGE CONTEXT --------
    # Combine retrieved paragraphs into one text block

    context = "\n".join([doc.page_content for doc in docs])


    # This context will be given to LLM as knowledge
    return context
