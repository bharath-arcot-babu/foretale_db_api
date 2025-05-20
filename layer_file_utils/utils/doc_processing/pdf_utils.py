from typing import Union
import PyPDF2
import boto3
import io


# Initialize S3 client
s3_client = boto3.client('s3')

def extract_text_from_pdf(file_input: Union[str, io.BytesIO]) -> str:
    """
    Extract text from a PDF file while preserving structure.
    Handles both file paths and file-like objects.
    
    Args:
        file_input (Union[str, io.BytesIO]): Path to the PDF file or file-like object
    
    Returns:
        str: Extracted text with preserved structure
    """
    text = ""
    try:
        # Handle both file paths and file-like objects
        if isinstance(file_input, str):
            with open(file_input, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
        else:
            pdf_reader = PyPDF2.PdfReader(file_input)
        
        # Extract text from all pages
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
                    
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    return text
