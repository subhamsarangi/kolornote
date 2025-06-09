from django import template
import re

register = template.Library()


@register.filter
def format_checklist(value):
    value = re.sub(r"\[V\]", "✓", value)
    value = re.sub(r"\[ \]", "☐", value)
    return value
