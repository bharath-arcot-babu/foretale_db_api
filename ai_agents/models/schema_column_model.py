from pydantic import BaseModel
from typing import Optional

class SchemaColumnInput(BaseModel):
    schema_name: str
    table_list: Optional[str] = None

    