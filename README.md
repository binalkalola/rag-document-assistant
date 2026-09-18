# RAG Document Assistant

A Retrieval-Augmented Generation (RAG) system that answers questions about a set of PDF documents using semantic search and an LLM, with citations to the source file and page.

## Overview

This project allows users to ask natural language questions about a fictional institute's documents (Course Handbook, Student Guidelines, Syllabus, and FAQ). The system retrieves the most relevant passages from the documents and uses an LLM to generate an answer grounded strictly in that evidence, along with the source file and page number.

## Architecture

PDF Documents
↓ (ingestion.py)
Extracted Text (page by page)
↓ (chunking.py)
Overlapping Text Chunks
↓ (build_index.py)
Embeddings (sentence-transformers) → ChromaDB (vector store)
↓
User Question
↓ (test_retrieval.py logic)
Top-K Similar Chunks Retrieved
↓ (generation.py)
LLM Answer (evidence-based, with citations)
↓ (app.py)
Streamlit Web Interface


## Tech Stack

- **PDF Extraction:** pypdf
- **Chunking:** Custom word-based chunking with overlap
- **Embeddings:** sentence-transformers (`all-MiniLM-L6-v2`)
- **Vector Database:** ChromaDB (persistent, local)
- **LLM Provider:** NVIDIA NIM API (OpenAI-compatible), model: `meta/muse-glimmer-30b`
- **Interface:** Streamlit

## Project Structure

```
rag-document-assistant/
├── documents/              # Source PDFs
├── ingestion.py            # Extracts text from PDFs, page by page
├── chunking.py             # Splits text into overlapping chunks
├── build_index.py          # Builds embeddings and stores them in ChromaDB
├── test_retrieval.py       # Retrieval function + manual retrieval testing
├── generation.py           # Builds prompts and calls the LLM
├── app.py                  # Streamlit web interface
├── requirements.txt
├── .env.example            # Sample environment file (no secrets)
├── .gitignore
└── evaluation.md           # Evaluation questions and results
```

## Setup Instructions

1. **Clone the repository**
```bash
   git clone <repo-url>
   cd rag-document-assistant
```

2. **Create and activate a virtual environment**
```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac/Linux
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Add your NVIDIA NIM API key (get one free at https://build.nvidia.com):

    NVIDIA_API_KEY=your_key_here

    
5. **Build the index** (extracts text, creates chunks, generates embeddings, stores in ChromaDB)
```bash
   python build_index.py
```

6. **Run the app**
```bash
   streamlit run app.py
```

7. Open the browser at `http://localhost:8501` and start asking questions.

## How It Works

1. **Ingestion:** Each PDF is opened and text is extracted page by page using `pypdf`. Pages with no extractable text (e.g. scanned images) are flagged with a warning, since `pypdf` does not perform OCR.
2. **Chunking:** Each page's text is split into overlapping word-based chunks (chunk size: 80 words, overlap: 20 words) to preserve context across chunk boundaries.
3. **Indexing:** Each chunk is converted into a 384-dimension embedding using `all-MiniLM-L6-v2` and stored in a persistent ChromaDB collection, along with its source filename and page number.
4. **Retrieval:** A user's question is embedded using the same model, and ChromaDB returns the top 6 most semantically similar chunks.
5. **Generation:** The retrieved chunks are combined into a prompt that instructs the LLM to answer **only** using the provided context, and to explicitly say "I could not find that information in the documents" if the answer isn't present — preventing hallucination.
6. **Interface:** A Streamlit app lets the user type a question, view the generated answer, and see the exact file/page sources used (only shown when an answer was actually found).

## Known Limitations

- Retrieval occasionally misses short, list-style facts (e.g. a numbered reference book list) that are less semantically "rich" for the embedding model to match against a natural-language question. See `evaluation.md` for details.
- `pypdf` cannot extract text from scanned image PDFs (no OCR support).
- The system is limited to the documents present in the `documents/` folder at the time `build_index.py` is run; new PDFs require re-running the indexing step.

## Evaluation

See `evaluation.md` for the full set of 20 test questions and results (95% accuracy — 19/20 correct).