from django import template
register = template.Library()

@register.filter
def dict_get(dictionary, key):
    if not dictionary:
        return 0
    return dictionary.get(str(key)) or 0