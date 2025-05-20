import pandas as pd
from typing import Union
import io

def extract_text_from_excel(file_input: Union[str, io.BytesIO]) -> str:
    """
    Extract text from Excel file while preserving structure.
    Handles both file paths and file-like objects.
    
    Args:
        file_input (Union[str, io.BytesIO]): Path to the Excel file or file-like object
    
    Returns:
        str: Extracted text with preserved structure
    """
    try:
        # Read Excel file
        if isinstance(file_input, str):
            df = pd.read_excel(file_input)
        else:
            df = pd.read_excel(file_input)
        
        # Convert DataFrame to text, preserving structure
        text = ""
        if isinstance(file_input, str):
            for sheet_name in pd.ExcelFile(file_input).sheet_names:
                sheet_df = pd.read_excel(file_input, sheet_name=sheet_name)
                text += f"\nSheet: {sheet_name}\n"
                text += sheet_df.to_string(index=False) + "\n\n"
        else:
            # For file-like objects, we need to read all sheets at once
            excel_file = pd.ExcelFile(file_input)
            for sheet_name in excel_file.sheet_names:
                sheet_df = pd.read_excel(excel_file, sheet_name=sheet_name)
                text += f"\nSheet: {sheet_name}\n"
                text += sheet_df.to_string(index=False) + "\n\n"
        
        return text
                    
    except Exception as e:
        raise Exception(f"Error extracting text from Excel: {str(e)}") 