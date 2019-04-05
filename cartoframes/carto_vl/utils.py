def temp_ignore_warnings(func):
    """Temporarily ignores warnings like
    those emitted by the carto python sdk"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """wrapper around func to filter/reset warnings"""
        with catch_warnings():
            filterwarnings('ignore')
            evaled_func = func(*args, **kwargs)
        return evaled_func
    return wrapper


def safe_quotes(text, escape_single_quotes=False):
    """htmlify string"""
    if isinstance(text, str):
        safe_text = text.replace('"', "&quot;")
        if escape_single_quotes:
            safe_text = safe_text.replace("'", "&#92;'")
        return safe_text.replace('True', 'true')
    return text
