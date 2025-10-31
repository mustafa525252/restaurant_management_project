from datetime import datetime

def format_datetime(dt):
    """
    Returns a user-friendly formatted string for a given datetime object.
    
    Example: 'January 1, 2023 at 10:30 AM'
    
    Args:
        dt (datetime or None): The datetime object to format.
    
    Returns:
        str: A formatted date-time string, or an empty string if None.
    """
    if dt is None:
        return ""  # Gracefully handle missing datetime

    if not isinstance(dt, datetime):
        raise TypeError("Expected a datetime object or None")

    # Format like: January 1, 2023 at 10:30 AM
    return dt.strftime("%B %d, %Y at %I:%M %p")
