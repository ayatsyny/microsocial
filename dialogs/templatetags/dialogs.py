# coding=utf-8
from django import template


register = template.Library()


@register.assignment_tag(takes_context=True)
def get_opponent(context, dialog):
    return dialog.get_opponent(context['user'])
