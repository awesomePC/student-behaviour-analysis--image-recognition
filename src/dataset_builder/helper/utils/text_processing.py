
def is_html_text(txt):
    from bs4 import BeautifulSoup
    return bool(
        BeautifulSoup(txt, "html.parser").find()
    )