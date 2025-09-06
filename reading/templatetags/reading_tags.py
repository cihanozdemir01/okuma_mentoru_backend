# reading/templatetags/reading_tags.py

from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Değeri argüman ile çarpar."""
    return value * arg

@register.filter
def div(value, arg):
    """Değeri argümana böler."""
    if arg == 0:
        return 0
    return value / arg