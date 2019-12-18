"""general utility functions for HTML Map templates"""


def safe_quotes(text, escape_single_quotes=False):
    """htmlify string"""
    if isinstance(text, str):
        safe_text = text.replace('"', "&quot;")
        if escape_single_quotes:
            safe_text = safe_text.replace("'", "&#92;'")
        return safe_text.replace('True', 'true')
    return text


def quote_filter(value):
    return safe_quotes(value.unescape())


def iframe_size_filter(value):
    if isinstance(value, str):
        return value

    return '%spx;' % value


def clear_none_filter(value):
    return dict(filter(lambda item: item[1] is not None, value.items()))
