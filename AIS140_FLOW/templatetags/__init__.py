from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Custom filter to get dictionary item value
    Usage: {{ dict|get_item:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, 0)
    return 0
