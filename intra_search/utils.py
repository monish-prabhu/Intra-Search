import re


def get_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def sanitize(text):
    """
    1. Removes URLs from text
    """
    return re.sub(r"http\S+", "", text)


def sanitize_filename(input_string, char="_"):
    """
    Replace invalid characters with char (default="_")

    """
    invalid_chars_pattern = r'[<>:"/\\|?*.\']'
    sanitized_string = re.sub(invalid_chars_pattern, char, input_string)
    sanitized_string = sanitized_string.strip(char)
    return sanitized_string
