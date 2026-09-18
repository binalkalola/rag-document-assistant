# This function breaks a long piece of text into smaller overlapping chunks
# chunk_size = how many words go in one chunk
# overlap = how many words repeat between two consecutive chunks
def split_text_into_chunks(text,chunk_size=80, overlap=20):
    # Split the text into a list of individual words
    words = text.split()
    chunks = [] #This will store all the final chunks
    start = 0 #This tracks where the current chunk starts
    # Keep creating chunks until we reach the end of the words list
    while start < len(words):
        # The chunk ends after 'chunk_size' words from the start
        end = start + chunk_size
        # Take the words from start to end, and join them back into a sentence
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append(chunk_text)

        # Move the start forward, but go back a little (overlap) so
        # the next chunk shares some words with this one
        start = start + chunk_size - overlap
    return chunks
# Testing this function directly
if __name__ == "__main__":
    # A small sample text to test chunking (just for demonstration)
    sample_text = "This is a simple test. " * 50  # repeat a short sentence to create a longer text

    result = split_text_into_chunks(sample_text, chunk_size=20, overlap=5)

    print(f"Total chunks created: {len(result)}")
    print(f"\n--- Chunk 1 ---\n{result[0]}")
    print(f"\n--- Chunk 2 ---\n{result[1]}")