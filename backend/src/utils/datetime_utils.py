from datetime import datetime

def parse_datetime(value):
    """
    Converts a string or Unix timestamp to a datetime object.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):  # Handle Unix timestamps
        return datetime.fromtimestamp(value)
    if isinstance(value, str):  # Handle ISO 8601 strings
        try:
            # Remove 'Z' and treat as UTC
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"  # Replace Z with UTC offset
            return datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(f"Invalid datetime string format: {value}")
    raise TypeError(f"Unsupported datetime format: {type(value)}")
