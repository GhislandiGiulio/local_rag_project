import PyPDF2
import re
import hashlib

def __calculate_sha256(file):
    
    sha256_hash = hashlib.sha256()
    # read the file in chunks to avoid memory issues with large files
    for chunk in iter(lambda: file.read(4096), b""):
        sha256_hash.update(chunk)
        
    return sha256_hash.hexdigest()


def scrape_pdf(file) -> tuple[list, int, str]:
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
                
    return paragraphs_with_pages, num_pages, __calculate_sha256(file)


def new_scrape_pdf(file) -> tuple[list, int, str]:
    """
    Extracts text from a PDF file and stores it in a list of tuples,
    where each tuple contains the text and its corresponding page number.
    The function also returns the total number of pages and a SHA-256 hash
    of the PDF file.

    :param file: A file object containing the PDF file
    :return: A tuple containing the list of (paragraph, page_num), the total number of pages, and the SHA-256 hash
    """

    MIN_WORD_COUNT = 5  # Minimum words for a valid paragraph
    MAX_WORD_COUNT = 15  # Maximum words before splitting
    reader = PyPDF2.PdfReader(file)
    num_pages = len(reader.pages)  # Get total pages
    
    paragraphs_with_pages = []  # List of (paragraph, page_num)
    
    # Loop through pages to extract text
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if not text:
            continue  # Skip empty pages

        text = re.sub(r'\s+', ' ', text).strip()  # Normalize spaces

        # Split text into chunks based on full stops and newlines
        def custom_split(text):
            raw_sentences = re.split(r'(?<=\.) |[\n]', text)  # Split at full stops or newlines
            paragraphs = []
            buffer = []

            for sentence in raw_sentences:
                words = sentence.split()
                buffer.append(sentence)

                # If sentence has more than 5 words, consider breaking here
                if len(words) > 5 or sum(len(s.split()) for s in buffer) > MAX_WORD_COUNT:
                    paragraphs.append(" ".join(buffer))
                    buffer = []

            if buffer:  # Add remaining sentences
                paragraphs.append(" ".join(buffer))

            return paragraphs

        paragraphs = custom_split(text)

        # Filter out very short paragraphs and ensure max word count is respected
        valid_paragraphs = [
            p.strip() for p in paragraphs
            if MIN_WORD_COUNT <= len(p.split()) <= MAX_WORD_COUNT
        ]

        # Store paragraphs with their respective page numbers
        for paragraph in valid_paragraphs:
            paragraphs_with_pages.append((paragraph, page_num))

    # Compute SHA-256 hash
    pdf_hash = __calculate_sha256(file)

    return paragraphs_with_pages, num_pages, pdf_hash