# OpenAI library works with NVIDIA's API too, since NVIDIA is OpenAI-compatible
from openai import OpenAI
# os is used to read environment variables (like our API key)
import os
# load_dotenv reads the .env file and makes its values available to our program
from dotenv import load_dotenv

# Load the variables from our .env file (this reads NVIDIA_API_KEY)
load_dotenv()

# Create a client to talk to NVIDIA's API
# base_url tells it to use NVIDIA's servers instead of OpenAI's

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)


# This function builds the prompt that we will send to the LLM
# It combines the retrieved chunks (evidence) with the user's question
def build_prompt(question, chunks_text_list):
    # Join all retrieved chunks into one block of text, separated by lines
    context = "\n\n".join(chunks_text_list)

    # Build the final prompt with clear instructions for the LLM

    prompt = f"""Answer the question using ONLY the context provided below.
If the answer is not found in the context, say "I could not find that information in the documents."
Do not use any outside knowledge.

Context:
{context}

Question: {question}

Answer:"""

    return prompt

# This function sends the prompt to the LLM and returns the answer
def generate_answer(question, chunks_text_list):
    # Build the prompt using our function from Part 2
    prompt = build_prompt(question, chunks_text_list)

    # Send the prompt to the LLM using NVIDIA's API
    # Wrap the API call in try/except so the app doesn't crash if the API fails
    try:

        response = client.chat.completions.create(
            model="meta/muse-glimmer-30b",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,  # limit the answer length (keeps cost/time low)
            temperature=0.2      # low temperature = more focused, less random answers
        )

    except Exception as e:
        # If the API call fails (no internet, wrong key, server down, etc.)
        # return a clear message instead of crashing
        print(f"ERROR: LLM API call failed. Details: {e}")
        return "Sorry, I could not generate an answer right now due to a technical issue. Please try again later."


    # Some reasoning models put the answer in 'content', others in 'reasoning_content'
    message = response.choices[0].message
    answer = message.content

    # If content is empty, try to extract the answer from reasoning_content instead
    if not answer:
        reasoning = message.reasoning_content or ""
        # The actual answer is usually the last part of the reasoning text
        answer = reasoning.strip().split("\n")[-1]
    

    return answer

# This block runs only when this file is executed directly
if __name__ == "__main__":
   # We need the same retrieval function from our test_retrieval.py file
    from test_retrieval import retrieve_top_chunks

    # A sample question to test the full pipeline
    question = "What is the minimum attendance requirement?"

    # Step 1: Retrieve the top matching chunks for this question
    results = retrieve_top_chunks(question, top_k=4)

    # Extract just the text of the chunks (we don't need metadata for generation)
    chunks_text_list = results["documents"][0]

    # Step 2: Generate an answer using the LLM, based on those chunks
    answer = generate_answer(question, chunks_text_list)

    # Print everything to see the full flow

    print(f"Question: {question}")
    print(f"\nAnswer: {answer}")

    