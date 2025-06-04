from pydantic import BaseModel

class ColumnResolverInput(BaseModel):
    business_attributes: str
    target_table_columns: str
