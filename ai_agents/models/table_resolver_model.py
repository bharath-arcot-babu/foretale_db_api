from pydantic import BaseModel

class TableResolverInput(BaseModel):
    business_entities: str
    database_tables: str

class TableResolverOutput(BaseModel):
    business_entity: str
    target_table_name: str