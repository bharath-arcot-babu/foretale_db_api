from pydantic import BaseModel
from typing import Optional

class SchemaTableInput(BaseModel):
    schema_name: str
    table_list: Optional[str] = None

class SchemaTableOutput(BaseModel):
    table_name: str
    physical_table_name: str
    description: str
    
