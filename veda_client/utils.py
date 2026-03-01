"""
Utility functions for the Veda Platform API client.
"""

import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from .models import Individual, ValueItem


def format_datetime(dt: datetime) -> str:
    """
    Format a datetime object into a string compatible with the Veda server.

    Timezone-aware datetimes are converted to UTC and formatted with a 'Z' suffix.
    Naive datetimes are formatted without timezone info and without microseconds.

    Args:
        dt: The datetime object to format.

    Returns:
        ISO 8601 datetime string without microseconds, accepted by the Veda server.
    """
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        return dt.strftime("%Y-%m-%dT%H:%M:%S")


def hash_password(password: str) -> str:
    """
    Generate a hash for the password.
    
    Args:
        password: The plain text password.
        
    Returns:
        Hashed password.
    """
    # This is a placeholder; replace with actual hashing algorithm used by Veda
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def build_query_string(conditions: Dict[str, Any]) -> str:
    """
    Build a Veda query string from a dictionary of conditions.
    
    Args:
        conditions: Dictionary of field name to value mappings.
        
    Returns:
        Veda query string.
    """
    query_parts = []
    
    for field, value in conditions.items():
        if isinstance(value, str):
            # Use string comparison for string values
            query_parts.append(f"('{field}'=='{value}')")
        else:
            # Use direct comparison for other types
            query_parts.append(f"('{field}'=={value})")
    
    # Join with AND operator
    return " && ".join(query_parts)


def create_individual(uri: str, properties: Dict[str, List[Dict[str, Any]]]) -> Individual:
    """
    Create an Individual instance from a URI and property dictionary.
    
    Args:
        uri: The unique identifier (URI) of the individual.
        properties: Dictionary of property key to list of value item dictionaries.
        
    Returns:
        A new Individual instance.
    """
    individual = Individual(uri=uri)
    
    for key, values in properties.items():
        individual.set_property(key, values)
    
    return individual


def create_value_item(data: Any, type_: str, lang: Optional[str] = None) -> ValueItem:
    """
    Create a ValueItem instance.
    
    Args:
        data: The value data.
        type_: The data type.
        lang: Optional language code.
        
    Returns:
        A new ValueItem instance.
    """
    return ValueItem(data=data, type_=type_, lang=lang)


def extract_values(individual: Individual, property_key: str) -> List[Any]:
    """
    Extract all data values for a specific property from an individual.
    
    Args:
        individual: The Individual instance.
        property_key: The property key.
        
    Returns:
        List of data values.
    """
    return [item.data for item in individual.get_property(property_key)]
