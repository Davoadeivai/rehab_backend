from django import template

register = template.Library()

@register.filter
def split_string(value, delimiter=','):
    """Split a string by the given delimiter and return a list."""
    return value.split(delimiter)
