from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(
    text: str,
    chunk_size: int = 300,
    chunk_overlap: int = 60,
    min_chunk_size: int = 100
) -> List[str]:
    """
    Split text into chunks using LangChain's RecursiveCharacterTextSplitter.
    
    Args:
        text (str): The input text to be chunked
        chunk_size (int): Maximum size of each chunk in characters
        chunk_overlap (int): Number of characters to overlap between chunks
        min_chunk_size (int): Minimum size of a chunk before merging with previous chunk
    
    Returns:
        List[str]: List of text chunks
    """
    if not text:
        return []
    
    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
        is_separator_regex=False
    )
    
    # Split the text
    chunks = text_splitter.split_text(text)
    
    # Filter out chunks that are too small
    chunks = [chunk for chunk in chunks if len(chunk) >= min_chunk_size]
    
    return chunks 