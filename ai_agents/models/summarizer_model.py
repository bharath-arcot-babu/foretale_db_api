from pydantic import BaseModel

class SummarizerInput(BaseModel):
    test_case: str
    test_description: str
    past_user_responses: str

class SummarizerOutput(BaseModel):
    summary: str
    key_tables: list[str]
    key_columns: list[str]
    key_criteria: list[str]
    ambiguities: list[str]
    select_columns: list[str]
    technical_ambiguities: list[str]
    column_modifications: list[str]

