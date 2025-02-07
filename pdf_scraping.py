import PyPDF2

# Open the PDF file in read-binary mode
def scrape_pdf(file) -> list[str]:
    pdf_reader = PyPDF2.PdfReader(file)
        
    # Get the number of pages in the PDF
    num_pages = len(pdf_reader.pages)
    
    # Initialize a string to hold the extracted text
    extracted_text = ''
    
    # Loop through each page and extract text
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        extracted_text += page.extract_text()
        
    # Split the text into paragraphs based on newlines or custom delimiters
    paragraphs = extracted_text.split('\n')

    # Clean up empty lines or unwanted characters
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # Define a minimum word count for a paragraph to be considered valid
    min_word_count = 8  # Adjust as needed

    # Filter out small paragraphs
    paragraphs = [p for p in paragraphs if len(p.split()) >= min_word_count]