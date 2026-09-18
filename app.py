# Streamlit library - used to build the web interface
import streamlit as st
# Import our existing retrieval function
from test_retrieval import retrieve_top_chunks
# Import our existing generation function
from generation import generate_answer

# Set the title that appears in the browser tab
st.set_page_config(page_title="RAG Document Assistant")

# Main heading shown on the page
st.title("📄 RAG Document Assistant")
st.write("Ask a question about the uploaded documents (Course Handbook, Student Guidelines, Syllabus, FAQ).")

# Create a text input box where the user can type their question
question = st.text_input("Enter your question:")

# Create a button - the code inside 'if' runs only when the button is clicked
if st.button("Get Answer"):
    # Check that the user actually typed something (not empty)
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        # Show a spinner (loading animation) while we process the question
        with st.spinner("Searching documents and generating answer..."):
            # Step 1: Retrieve the top matching chunks for this question
            results = retrieve_top_chunks(question, top_k=6)
            chunks_text_list = results["documents"][0]
            metadatas = results["metadatas"][0]

            # Step 2: Generate the answer using the LLM
            answer = generate_answer(question, chunks_text_list)

        # Display the answer on the page
        st.subheader("Answer")
        st.write(answer)

        # Only show sources if the LLM actually found an answer
        if "could not find" not in answer.lower():
            st.subheader("Sources")
            for i in range(len(metadatas)):
                filename = metadatas[i]["filename"]
                page = metadatas[i]["page_number"]
                st.write(f"- {filename}, Page {page}")