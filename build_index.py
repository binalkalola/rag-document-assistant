# Import our own function from ingestion.py to extract text from PDFs
from ingestion import extract_text_from_pdf
# Import our own function from chunking.py to split text into chunks
from chunking import split_text_into_chunks
# Import os to work with files and folders
import os
# SentenceTransformer converts text into embeddings (numbers)
from sentence_transformers import SentenceTransformer
# chromadb is our vector database to store and search embeddings
import chromadb

# Load the embedding model once (this may take a few seconds the first time)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Create a ChromaDB client that saves data to disk (so it persists between runs)
chroma_client = chromadb.PersistentClient(path="chroma_db")

# A "collection" in ChromaDB is like a table - it holds our chunks and their embeddings
collection = chroma_client.get_or_create_collection(name="rag_documents")

# This function processes ALL PDFs in the documents folder
# and returns a single list containing chunks from every PDF, every page
def build_all_chunks(documents_folder):
    # This list will hold chunks from every PDF combined together
    all_chunks = []

    # Get a list of all files in the documents folder, but keep only PDF files
    # (this skips any non-PDF files that might accidentally be in the folder)
    pdf_files = [f for f in os.listdir(documents_folder) if f.endswith(".pdf")]
    # Loop through every PDF file found in the documents folder
    for filename in pdf_files:
        # Build the full path to this PDF (folder name + file name)
        pdf_path = os.path.join(documents_folder, filename)
        print(f"\nProcessing file: {pdf_path}")
        # Use our ingestion.py function to extract text, page by page
        pages = extract_text_from_pdf(pdf_path)
        # Now loop through each page of THIS pdf
        for page in pages:
            # Use our chunking.py function to split this page's text into chunks
            page_chunks = split_text_into_chunks(page["text"])

            # Loop through each chunk created from this page
            for chunk in page_chunks:
                # Store the chunk along with useful metadata:
                # which file it came from, and which page number
                all_chunks.append({
                    "text" : chunk,
                    "filename" : filename,
                    "page_number" : page["page_number"]
                })


    return all_chunks

# This function takes our list of chunks and stores them in ChromaDB
# along with their embeddings and metadata
def store_chunks_in_chromadb(chunks):
    # Loop through every chunk, keeping track of its position (index)
    for i, chunk in enumerate(chunks):
        # Convert this chunk's text into an embedding (a list of numbers)
        embedding = embedding_model.encode(chunk["text"]).tolist()
        # Add this chunk to the ChromaDB collection
        collection.add(
            ids=[str(i)],                     # a unique ID for this chunk (must be a string)
            embeddings=[embedding],           # the embedding we just created
            documents=[chunk["text"]],        # the actual chunk text
            metadatas=[{                      # extra info about this chunk
                "filename": chunk["filename"],
                "page_number": chunk["page_number"]
            }]
        )
        # Print progress every 10 chunks so we know it's working
        if i % 10 == 0:
            print(f"Stored chunk {i + 1} of {len(chunks)}")
    print(f"\nAll {len(chunks)} chunks stored in ChromaDB successfully!")
# This block runs only when this file is executed directly
if __name__ == "__main__":
    # Build chunks from all PDFs in the documents folder
    chunks = build_all_chunks("documents")

    # Print a summary
    print(f"\n{'='*50}")
    print(f"Total chunks created from all PDFs: {len(chunks)}")

    # Show the first chunk as a sample, to inspect it
    if chunks:
        print(f"\n--- Sample Chunk ---")
        print(f"From file: {chunks[0]['filename']}, Page: {chunks[0]['page_number']}")
        print(f"Text: {chunks[0]['text'][:300]}")
        # Now store all these chunks into ChromaDB with their embeddings
    
    print(f"\n{'='*50}")
    print("Creating embeddings and storing in ChromaDB...")
    store_chunks_in_chromadb(chunks)

    # Verify how many items are now in the collection
    print(f"\nTotal items in ChromaDB collection: {collection.count()}")