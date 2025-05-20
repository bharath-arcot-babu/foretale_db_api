def clean_text_for_embeddings(text: str) -> str:
    """
    Clean text to improve embedding quality.
    
    Args:
        text (str): Input text to clean
    
    Returns:
        str: Cleaned text
    """
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove special characters that might affect embeddings
    # Keep basic punctuation for semantic meaning
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    
    return text.strip() 