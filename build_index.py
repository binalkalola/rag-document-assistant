
# Extract text page-by-page from PDF
from ingestion import extract_text_from_pdf

# Split extracted text into smaller overlapping chunks
from chunking import split_text_into_chunks

# Used for working with files and folders
import os

# SentenceTransformer is used to convert text into embeddings
from sentence_transformers import SentenceTransformer

# ChromaDB is used to store and search embeddings
import chromadb


# ============================================================
# 1. LOAD EMBEDDING MODEL
# ============================================================

# IMPORTANT:
# The same embedding model must be used for:
# 1. Document chunks
# 2. User questions
#
# This model converts text into numerical vectors (embeddings).
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# 2. CONNECT TO CHROMADB
# ============================================================

# PersistentClient stores ChromaDB data on disk.
#
# "chroma_db" is the folder where our vector database is stored.
chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)


# Get the existing collection.
# If the collection does not exist, create it.
collection = chroma_client.get_or_create_collection(
    name="rag_documents"
)


# ============================================================
# 3. RESET ENTIRE COLLECTION
# ============================================================

def reset_collection():
    """
    Delete the complete ChromaDB collection and create
    a fresh empty collection.

    This is useful when starting a completely fresh index.
    """

    global collection

    # Try to delete the existing collection.
    try:
        chroma_client.delete_collection(
            name="rag_documents"
        )

    except Exception:
        # If the collection does not exist,
        # simply continue.
        pass

    # Create a new empty collection.
    collection = chroma_client.get_or_create_collection(
        name="rag_documents"
    )

    print("ChromaDB collection reset successfully.")


# ============================================================
# 4. BUILD CHUNKS FROM ALL PDF FILES
# ============================================================

def build_all_chunks(documents_folder):
    """
    Read all PDF files from the documents folder,
    extract their text page-by-page,
    split the text into chunks,
    and return all chunks with metadata.
    """

    # This list will contain chunks from all PDFs.
    all_chunks = []

    # Get all PDF filenames from the documents folder.
    pdf_files = [
        filename
        for filename in os.listdir(documents_folder)
        if filename.lower().endswith(".pdf")
    ]

    # Process every PDF.
    for filename in pdf_files:

        # Create the complete PDF path.
        pdf_path = os.path.join(
            documents_folder,
            filename
        )

        print(
            f"\nProcessing file: {pdf_path}"
        )

        # Extract text page-by-page.
        pages = extract_text_from_pdf(
            pdf_path
        )

        # Process every page.
        for page in pages:

            # Split page text into smaller chunks.
            #
            # Your chunking.py currently uses:
            # chunk_size = 80 words
            # overlap = 20 words
            page_chunks = split_text_into_chunks(
                page["text"]
            )

            # Store every chunk with metadata.
            for chunk in page_chunks:

                all_chunks.append({
                    "text": chunk,
                    "filename": filename,
                    "page_number": page["page_number"]
                })

    return all_chunks


# ============================================================
# 5. STORE CHUNKS + EMBEDDINGS IN CHROMADB
# ============================================================

def store_chunks_in_chromadb(chunks):
    """
    Convert each chunk into an embedding and store it
    in ChromaDB along with the original text and metadata.
    """

    # Process every chunk.
    for i, chunk in enumerate(chunks):

        # Convert chunk text into an embedding.
        #
        # .tolist() converts the NumPy array into
        # a normal Python list for ChromaDB.
        embedding = embedding_model.encode(
            chunk["text"]
        ).tolist()

        # ----------------------------------------------------
        # Create a UNIQUE ID for this chunk.
        #
        # Example:
        # Course_Handbook.pdf_page_2_chunk_15
        #
        # This prevents ID conflicts when adding new PDFs.
        # ----------------------------------------------------

        chunk_id = (
            f"{chunk['filename']}_"
            f"page_{chunk['page_number']}_"
            f"chunk_{i}"
        )

        # Add the chunk to ChromaDB.
        collection.add(
            ids=[chunk_id],

            # Numerical vector representation
            embeddings=[embedding],

            # Original text
            documents=[chunk["text"]],

            # Information about where the chunk came from
            metadatas=[{
                "filename": chunk["filename"],
                "page_number": chunk["page_number"]
            }]
        )

        # Print progress after every 10 chunks.
        if i % 10 == 0:
            print(
                f"Stored chunk {i + 1} "
                f"of {len(chunks)}"
            )

    print(
        f"\nAll {len(chunks)} chunks "
        f"stored in ChromaDB successfully!"
    )


# ============================================================
# 6. INDEX ONLY ONE PDF
# ============================================================

def index_single_pdf(pdf_path):
    """
    Extract, chunk, embed and store only one PDF.

    This function is useful when a NEW PDF is uploaded.
    We don't need to re-index all existing PDFs.
    """

    # Get only the filename from the complete path.
    filename = os.path.basename(
        pdf_path
    )

    print(
        f"\nIndexing new PDF: {filename}"
    )

    # Extract text from the PDF.
    pages = extract_text_from_pdf(
        pdf_path
    )

    # Store chunks for this PDF.
    chunks = []

    # Process every page.
    for page in pages:

        # Split page text into chunks.
        page_chunks = split_text_into_chunks(
            page["text"]
        )

        # Store each chunk with metadata.
        for chunk in page_chunks:

            chunks.append({
                "text": chunk,
                "filename": filename,
                "page_number": page["page_number"]
            })

    # If chunks were successfully created,
    # create embeddings and store them.
    if chunks:

        store_chunks_in_chromadb(
            chunks
        )

    print(
        f"Indexed {len(chunks)} chunks "
        f"from {filename}"
    )

    return len(chunks)


# ============================================================
# 7. DELETE ONE PDF'S CHUNKS FROM CHROMADB
# ============================================================

def delete_document_from_chromadb(filename):
    """
    Delete ONLY the chunks belonging to the specified PDF.

    Other PDFs and their embeddings remain untouched.
    """

    global collection

    # Get stored metadata from ChromaDB.
    data = collection.get(
        include=["metadatas"]
    )

    # This list will contain IDs of the PDF's chunks.
    ids_to_delete = []

    # Check every stored record.
    for i, metadata in enumerate(
        data["metadatas"]
    ):

        # Compare the stored filename
        # with the PDF we want to delete.
        if metadata.get("filename") == filename:

            # Save that chunk's ID.
            ids_to_delete.append(
                data["ids"][i]
            )

    # If matching chunks were found,
    # delete only those chunks.
    if ids_to_delete:

        collection.delete(
            ids=ids_to_delete
        )

        print(
            f"Deleted {len(ids_to_delete)} "
            f"chunks for {filename}"
        )

    else:

        print(
            f"No ChromaDB chunks found "
            f"for {filename}"
        )


# ============================================================
# 8. TEST FULL INDEXING
# ============================================================

# This section runs only when:
#
# python build_index.py
#
# is executed directly from the terminal.
#
# It does NOT run when another file imports
# build_index.py.
if __name__ == "__main__":

    # --------------------------------------------------------
    # Start with a completely fresh ChromaDB collection.
    # --------------------------------------------------------
    reset_collection()

    # --------------------------------------------------------
    # Read all PDFs currently present in documents/
    # --------------------------------------------------------
    chunks = build_all_chunks(
        "documents"
    )

    print(
        f"\nTotal chunks created: "
        f"{len(chunks)}"
    )

    # --------------------------------------------------------
    # Create embeddings and store all chunks.
    # --------------------------------------------------------
    if chunks:

        store_chunks_in_chromadb(
            chunks
        )

    # --------------------------------------------------------
    # Show final number of records in ChromaDB.
    # --------------------------------------------------------
    print(
        f"\nTotal items in ChromaDB: "
        f"{collection.count()}"
    )