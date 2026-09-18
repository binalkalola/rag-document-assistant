# Import PdfReader from the pypdf library - this is used to open PDF files and read their pages
from pypdf import PdfReader
# Import the os library - used to check if files/folders exist and to build file paths safely
import os


# This function takes the path of ONE PDF file and extracts text from it, page by page
def extract_text_from_pdf(pdf_path):
    # Step 1: Check whether the given file path actually exists on disk
    if not os.path.exists(pdf_path):
        print(f"ERROR: file not found: {pdf_path}")
        return []  # Stop here and return an empty list since there is nothing to process

    # Step 2: Try to open the PDF using PdfReader
    # If the file is corrupted or not a valid PDF, this will raise an exception
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"ERROR: could not read '{pdf_path}'. It may be corrupted or unreadable.")
        print(f"Details: {e}")
        return []  # Stop here since the file could not be opened at all

    # Get the total number of pages in this PDF
    total_pages = len(reader.pages)
    print(f"file open successfully: {pdf_path}")
    print(f"Total pages found: {total_pages}\n")

    # This list will store the text extracted from each valid page,
    # along with that page's page number
    pages_data = []

    # Step 3: Loop through every page in the PDF one by one
    # enumerate(..., start=1) makes page numbering start from 1 instead of 0,
    # since real documents refer to "page 1" as the first page
    for page_num, page in enumerate(reader.pages, start=1):
        # Extract all text from the current page
        text = page.extract_text()

        # Check if the extracted text is empty or contains only blank spaces
        # This can happen if the page is a scanned image, since pypdf does not perform OCR
        if not text or text.strip() == "":
            print(f"WARNING: Page {page_num} has no extractable text (it may be a scanned image).")
            continue  # Skip this page and move on to the next one

        # If we reach here, valid text was found - store it in our list
        pages_data.append({
            "page_number": page_num,   # Which page this text came from
            "text": text                # The actual extracted text
        })
        print(f"Page {page_num}: extracted {len(text)} characters.")

    # After checking all pages, return the complete list of valid pages
    return pages_data


# This special block only runs when this file is executed directly
# (it will NOT run if this file is imported into another file later)
if __name__ == "__main__":
    # For now, we are testing with only ONE PDF, as suggested by the project guide
    test_pdf = os.path.join("documents", "Course_Handbook.pdf")

    # Call our function and store the result
    result = extract_text_from_pdf(test_pdf)

    # Print a summary of how many pages had valid text
    print(f"\n{'='*50}")
    print(f"Total pages with valid text: {len(result)}")

    # Show a small sample of the first page's text so we can visually inspect the output
    if result:
        print(f"\n--- Sample text from Page {result[0]['page_number']} ---")
        print(result[0]['text'][:400])