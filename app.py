# ============================================================
# app.py
# RAG Document Assistant - Streamlit Application
# ============================================================

# Streamlit is used to create the web interface
import streamlit as st

# os is used for file and folder operations
import os

# Import retrieval function
from test_retrieval import retrieve_top_chunks

# Import LLM generation function
from generation import generate_answer

# Import indexing functions from build_index.py
from build_index import (
    build_all_chunks,
    store_chunks_in_chromadb,
    reset_collection,
    index_single_pdf,
    delete_document_from_chromadb
)


# ============================================================
# 1. STREAMLIT PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="RAG Document Assistant"
)

st.title("📄 RAG Document Assistant")

st.write(
    "Ask a question about the uploaded documents "
    "(Course Handbook, Student Guidelines, Syllabus, FAQ)."
)


# ============================================================
# 2. DOCUMENTS FOLDER
# ============================================================

# Create documents folder if it does not already exist.
os.makedirs(
    "documents",
    exist_ok=True
)


# ============================================================
# 3. FRESH INDEXING WHEN APP STARTS
# ============================================================

# Streamlit reruns the script many times.
# Therefore we use session_state so this block runs
# only once per Streamlit session.

if "initial_index_done" not in st.session_state:

    with st.spinner(
        "Preparing document index..."
    ):

        try:

            # ------------------------------------------------
            # Clear the old ChromaDB collection.
            #
            # This removes old embeddings from the previous
            # project/app run.
            # ------------------------------------------------
            reset_collection()

            # ------------------------------------------------
            # Read all PDFs currently present in documents/
            # ------------------------------------------------
            chunks = build_all_chunks(
                "documents"
            )

            # ------------------------------------------------
            # Create embeddings and store them in ChromaDB.
            # ------------------------------------------------
            if chunks:

                store_chunks_in_chromadb(
                    chunks
                )

            # Mark initialization as completed.
            st.session_state.initial_index_done = True

            st.success(
                f"Fresh index created successfully. "
                f"{len(chunks)} chunks indexed."
            )

        except Exception as e:

            st.error(
                f"Error while creating index: {e}"
            )


# ============================================================
# 4. PDF UPLOAD SECTION
# ============================================================

st.subheader(
    "📁 Upload PDF Documents"
)


uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True
)


# ============================================================
# 5. PROCESS NEW UPLOADED PDFS
# ============================================================

if uploaded_files:

    for uploaded_file in uploaded_files:

        # Complete path where the uploaded PDF will be saved.
        file_path = os.path.join(
            "documents",
            uploaded_file.name
        )

        # Check whether this PDF already exists.
        file_already_exists = os.path.exists(
            file_path
        )

        # ----------------------------------------------------
        # Save the PDF only if it is new.
        # ----------------------------------------------------
        if not file_already_exists:

            with open(
                file_path,
                "wb"
            ) as f:

                f.write(
                    uploaded_file.getbuffer()
                )

            st.success(
                f"{uploaded_file.name} uploaded successfully."
            )

            # ------------------------------------------------
            # Automatically index ONLY this new PDF.
            # ------------------------------------------------
            try:

                with st.spinner(
                    f"Indexing {uploaded_file.name}..."
                ):

                    chunk_count = index_single_pdf(
                        file_path
                    )

                st.success(
                    f"{uploaded_file.name} indexed successfully "
                    f"({chunk_count} chunks)."
                )

            except Exception as e:

                st.error(
                    f"Error indexing {uploaded_file.name}: {e}"
                )

        else:

            st.info(
                f"{uploaded_file.name} already exists."
            )


# ============================================================
# 6. SHOW CURRENT PDF FILES
# ============================================================

st.subheader(
    "📚 Current Documents"
)


pdf_files = [
    filename
    for filename in os.listdir("documents")
    if filename.lower().endswith(".pdf")
]


if pdf_files:

    for filename in pdf_files:

        # Create two columns:
        # left = filename
        # right = delete button
        col1, col2 = st.columns(
            [5, 1]
        )

        with col1:

            st.write(
                f"📄 {filename}"
            )

        with col2:

            delete_button = st.button(
                "🗑️ Delete",
                key=f"delete_{filename}"
            )

        # ====================================================
        # 7. DELETE PDF + ITS CHROMADB DATA
        # ====================================================

        if delete_button:

            file_path = os.path.join(
                "documents",
                filename
            )

            try:

                # ------------------------------------------------
                # First delete this PDF's embeddings/chunks
                # from ChromaDB.
                # ------------------------------------------------
                delete_document_from_chromadb(
                    filename
                )

                # ------------------------------------------------
                # Then delete the actual PDF file.
                # ------------------------------------------------
                if os.path.exists(file_path):

                    os.remove(
                        file_path
                    )

                st.success(
                    f"{filename} deleted successfully "
                    f"from PDF storage and ChromaDB."
                )

                # Refresh the Streamlit page.
                st.rerun()

            except Exception as e:

                st.error(
                    f"Error deleting {filename}: {e}"
                )

else:

    st.info(
        "No PDF documents found."
    )


# ============================================================
# 8. QUESTION INPUT
# ============================================================

st.subheader(
    "💬 Ask a Question"
)


question = st.text_input(
    "Enter your question:"
)


# ============================================================
# 9. GET ANSWER
# ============================================================

if st.button(
    "Get Answer"
):

    # Check whether the question is empty.
    if question.strip() == "":

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Searching documents and generating answer..."
        ):

            # ------------------------------------------------
            # Step 1:
            # Retrieve the most relevant document chunks.
            # ------------------------------------------------
            results = retrieve_top_chunks(
                question,
                top_k=6
            )

            # Extract retrieved document text.
            chunks_text_list = (
                results["documents"][0]
            )

            # Extract metadata for source display.
            metadatas = (
                results["metadatas"][0]
            )

            # ------------------------------------------------
            # Step 2:
            # Generate answer using retrieved context.
            # ------------------------------------------------
            answer = generate_answer(
                question,
                chunks_text_list
            )


        # ====================================================
        # 10. DISPLAY ANSWER
        # ====================================================

        st.subheader(
            "Answer"
        )

        st.write(
            answer
        )


        # ====================================================
        # 11. DISPLAY SOURCES
        # ====================================================

        # Show sources only when an actual answer was found.
        if "could not find" not in answer.lower():

            st.subheader(
                "Sources"
            )

            shown_sources = set()

            for metadata in metadatas:

                filename = metadata[
                    "filename"
                ]

                page = metadata[
                    "page_number"
                ]

                source = (
                    filename,
                    page
                )

                # Avoid showing the same
                # filename + page multiple times.
                if source not in shown_sources:

                    st.write(
                        f"- {filename}, Page {page}"
                    )

                    shown_sources.add(
                        source
                    )