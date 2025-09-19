"""
Custom template filters for SPCM
"""
from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add_float(value, arg):
    """Add two float values"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value):
    """Convert decimal to percentage"""
    try:
        return float(value) * 100
    except (ValueError, TypeError):
        return 0
