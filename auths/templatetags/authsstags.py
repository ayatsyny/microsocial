# coding=utf-8
from django import template

register = template.Library()


@register.inclusion_tag('tags/messages.html')
def show_messages(context):
    return {'messages': context.get('messages')}


@register.inclusion_tag('tags/form_field_errors.html')
def show_form_field_errors(field_errors):
    return {'errors': field_errors}
