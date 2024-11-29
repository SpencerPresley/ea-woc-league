"""
Base models for NHL game data structures.

This module provides base models and validators used across the game data models.
"""

from typing import Dict

from pydantic import BaseModel, ConfigDict, model_validator


class NumericValidatorBase(BaseModel):
    """
    Base model that handles common numeric validation and data cleaning tasks.
    
    Provides configuration for number coercion, string handling, and dash-to-None conversion.
    """
    
    model_config = ConfigDict(
        populate_by_name=True,
        coerce_numbers_to_str=True,
        str_to_lower=True,
        str_strip_whitespace=True,
    )

    @model_validator(mode="before")
    @classmethod
    def handle_dashes(cls, data: Dict) -> Dict:
        """
        Convert '--' string values to None in the input data.
        
        Args:
            data: The input data to clean
            
        Returns:
            The cleaned data with '--' converted to None
        """
        if not isinstance(data, dict):
            return data
            
        for key, value in data.items():
            if value == "--":
                data[key] = None
        return data 