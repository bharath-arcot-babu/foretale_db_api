from typing import List, Optional
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    """
    A template for building structured prompts with role, instructions, goal, and examples.
    """
    instructions: str
    goal: str
    output_format: str
    role: str = "assistant"
    examples: List[str] = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []


    def build_prompt_template_summarize_test_case(
        self,
        test_name: str,
        test_description: str,
        past_user_responses: str = ""
    ) -> str:
        """
        Builds a prompt for summarizing test case.
        
        Args:
            test_name: Name of the test case
            test_description: Description of the test case
            past_user_responses: Optional past user responses
            
        Returns:
            str: The complete formatted prompt
        """
        past_responses_section = f"\nHere is the list of past user responses in the descending order:\n{past_user_responses}" if past_user_responses else ""
        
        prompt = f"""
        {self.role}

        {self.goal}

        {self.instructions}

        {self.output_format}

        {self.examples}

        Here is the test case name, description and past user responses:
        Test Case Name: {test_name}
        Test Case Description: {test_description}
        Past User Responses (newline or ; is the separator):
        {past_responses_section}
        """
        return prompt

    def build_prompt_template_table_resolver(
        self,
        key_tables: str,
        database_tables: str,       
    ) -> str:
        """
        Builds a prompt for resolving business entities to database tables.
        
        Args:
            business_entities: List of business entities
            database_tables: List of database tables
            
        Returns:
            str: The complete formatted prompt
        """
        prompt = f"""
        {self.role}

        {self.goal}

        {self.instructions}

        {self.output_format}

        Here is the list of key tables:
        {key_tables}

        Here is the list of database tables:
        {database_tables}

        {self.examples}

        """
        return prompt
    
    def build_prompt_template_column_resolver(
        self,
        business_attributes: str,
        target_table_columns: str,       
    ) -> str:
        """
        Builds a prompt for resolving business entities to database tables.
        
        Args:
            business_attributes: List of business attributes
            target_table_columns: List of target table columns
            
        Returns:
            str: The complete formatted prompt
        """
        prompt = f"""
        {self.role}

        {self.goal}

        {self.instructions}

        {self.output_format}

        Here is the list of business attributes:
        {business_attributes}

        Here is the list of target table columns with primary/composite key columns:
        {target_table_columns}

        Here is the list of examples that are already resolved:
        {self.examples}

        """
        return prompt
    
    def build_prompt_template_generate_sql(
        self,
        test_summary: str,
        criteria: str,
        table_hints: str,
        column_hints: str,
        column_modifications: str,
        join_hints: str,
        schema_name: str,
        select_columns: str
    ) -> str:
        """
        Builds a prompt for generating SQL query.
        
        Args:
            test_case: Name of the test case
            test_description: Description of the test case
            criteria: Test criteria
            table_hints: Available tables
            column_hints: Available columns
            join_hints: Join conditions
            
        Returns:
            str: The complete formatted prompt
        """
        prompt = f"""
        {self.role}

        {self.instructions}

        {self.goal}

        {self.output_format}

        Here is the test case information:
        Test Summary: {test_summary}
        Target tables to be used for writing the SQL query: {table_hints}
        Target columns to be used for writing the SQL query: {column_hints}
        Join conditions to be used for writing the SQL query: {join_hints}
        Table schema name: {schema_name}
        
        """
        return prompt

    def build_prompt_template_validate_sql(
        self,
        sql_query: str,
        test_summary: str,
        criteria: str
    ) -> str:
        """
        Builds a prompt for validating SQL query.
        
        Args:
            sql_query: The SQL query to validate
            test_summary: Summary of the test case
            criteria: Criteria that the SQL query should satisfy
            
        Returns:
            str: The complete formatted prompt
        """
        prompt = f"""
        {self.role}

        {self.instructions}

        {self.goal}

        {self.output_format}

        Here is the SQL query to validate:
        SQL Query: {sql_query}

        Here is the test case information:
        Test Summary: {test_summary}
        Criteria: {criteria}

        {self.examples}
        """
        return prompt 
    

    def build_prompt_template_format_sql(
        self,
        sql_query: str
    ) -> str:
        """
        Builds a prompt for validating SQL query.
        
        Args:
            sql_query: The SQL query to validate
            
        Returns:
            str: The complete formatted prompt
        """
        prompt = f"""
        {self.role}

        {self.instructions}

        {self.goal}

        {self.output_format}

        Here is the SQL query to format:
        SQL Query: {sql_query}

        {self.examples}
        """
        return prompt 
    
    def build_prompt_template_apply_column_modifications(
        self,
        sql_query: str,
        column_with_data_profile: str
    ) -> str:
        """
        Builds a prompt for applying column modifications.
        
        Args:
            sql_query: The SQL query to modify
            column_with_data_profile: List of columns with data profile
            
        Returns:
            str: The complete formatted prompt
        """
        prompt = f"""
        {self.role}

        {self.instructions}

        {self.goal}

        {self.output_format}

        Here is the SQL query to modify:
        SQL Query: {sql_query}

        Here is the list of columns with data profile:
        Column with Data Profile: {column_with_data_profile}

        {self.examples}
        """
        return prompt 

