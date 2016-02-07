# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def duration_minutes(seconds):
    """ Returns the value rounded up to the nearest minute """
    if seconds % 60 != 0:
        return (seconds / 60) + 1
    else:
        return (seconds / 60)