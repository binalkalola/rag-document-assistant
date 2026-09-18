# We need the same embedding model that we used to create chunk embeddings
from sentence_transformers import SentenceTransformer
# We need chromadb to connect to our existing saved database
import chromadb

# Load the SAME embedding model used before
# (questions and chunks must use the same model to be comparable)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to the SAME ChromaDB folder where we already stored our chunks
chroma_client = chromadb.PersistentClient(path="chroma_db")

# Get the SAME collection (not creating a new one, just connecting to existing data)
collection = chroma_client.get_or_create_collection(name="rag_documents")

# This function takes a question, embeds it, and finds the most similar chunks
def retrieve_top_chunks(question, top_k=3):
    # Convert the question into an embedding, same way we did for chunks
    question_embedding = embedding_model.encode(question).tolist()

    # Ask ChromaDB to find the most similar chunks to this question
    results = collection.query(
        query_embeddings=[question_embedding], 
        n_results=top_k
    )
    return results
# This function nicely prints the retrieved chunks, showing filename and page
# This function nicely prints the retrieved chunks, showing filename and page
def print_results(question, results):
    print(f"\n{'='*60}")
    print(f"QUESTION: {question}")
    print(f"{'='*60}")

    # ChromaDB returns results as nested lists, so we access the first (and only) query's results
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Loop through each retrieved chunk and print it clearly
    for i in range(len(documents)):
        print(f"\n--- Result {i + 1} ---")
        print(f"File: {metadatas[i]['filename']}, Page: {metadatas[i]['page_number']}")
        print(f"Text: {documents[i][:300]}")
# This block runs only when this file is executed directly
if __name__ == "__main__":
    # A list of test questions to check if retrieval works correctly
    # These are based on facts we know exist in our PDFs
    test_questions = [
        "How do I submit my assignments?",
        "What is the minimum attendance requirement?",
        "How many books can I borrow from the library?",
        "What time does the hostel gate close?",
        "What topics are covered in the AI course syllabus?"
    ]

    # Loop through each test question and check the retrieved results
    for question in test_questions:
        results = retrieve_top_chunks(question, top_k=4)
        print_results(question, results)