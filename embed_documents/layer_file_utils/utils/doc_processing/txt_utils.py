from typing import Union
import io

def extract_text_from_txt(file_input: Union[str, io.BytesIO]) -> str:
    """
    Extract text from TXT file.
    Handles both file paths and file-like objects.
    
    Args:
        file_input (Union[str, io.BytesIO]): Path to the TXT file or file-like object
    
    Returns:
        str: Extracted text
    """
    try:
        # Read text file
        if isinstance(file_input, str):
            with open(file_input, 'r', encoding='utf-8') as file:
                text = file.read()
        else:
            text = file_input.getvalue().decode('utf-8')
        
        return text
                    
    except Exception as e:
        raise Exception(f"Error extracting text from TXT: {str(e)}") 