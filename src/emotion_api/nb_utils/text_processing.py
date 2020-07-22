
def is_html_text(txt):
    """
    Check is input text is html or not

    Args:
        txt (str): input text

    Returns:
        bool: Returns True if html else False.
    """
    from bs4 import BeautifulSoup
    return bool(
        BeautifulSoup(txt, "html.parser").find()
    )

def generate_unique_str(allow_dashes=True):
    """
    Generate unique string using uuid package

    Args:
        allow_dashes (bool, optional): If true use uuid4() otherwise use hex that will skip dash in names. Defaults to True.
    """
    import uuid

    if allow_dashes:
        unique_str = str(uuid.uuid4())
    else:
        unique_str = uuid.uuid4().hex
    return unique_str