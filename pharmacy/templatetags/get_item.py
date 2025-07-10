from django import template
import jdatetime
register = template.Library()

def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def jalali(value):
    if not value:
        return '-'
    try:
        return jdatetime.date.fromgregorian(date=value).strftime('%Y/%m/%d')
    except Exception:
        return str(value)

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key, 0)
    except AttributeError:
        return 0 