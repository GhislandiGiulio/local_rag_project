import PyPDF2

# Open the PDF file in read-binary mode
def scrape_pdf(file) -> list[str]:
    import PyPDF2

    # Define the minimum word count for a paragraph to be considered valid
    MIN_WORD_COUNT = 8  

    pdf_reader = PyPDF2.PdfReader(file)
        
    # Get the number of pages
    num_pages = len(pdf_reader.pages)
    
    # List to store extracted paragraphs with page numbers
    paragraphs_with_pages = []

    # Loop through each page and extract text
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()
        
        if text:  # Ensure the page contains text
            # Split text into paragraphs based on newlines
            paragraphs = text.split("\n")
            
            # Clean up empty lines and unwanted characters
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            # Filter out short paragraphs
            valid_paragraphs = [p for p in paragraphs if len(p.split()) >= MIN_WORD_COUNT]
            
            # Store paragraphs with the associated page number
            for paragraph in valid_paragraphs:
                paragraphs_with_pages.append((paragraph, page_num + 1))
                
    return paragraphs_with_pages, num_pages