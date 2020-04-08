from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='is_html')
@stringfilter
def is_html(value):
    from bs4 import BeautifulSoup
    return bool(
        BeautifulSoup(value, "html.parser").find()
    )