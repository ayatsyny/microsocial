# coding=utf-8
from django import template

register = template.Library()


@register.inclusion_tag('microsocial/tags/messages.html', takes_context=True)
def show_messages(context, show=True):
    return {'messages': context.get('messages') if show else None}


@register.inclusion_tag('microsocial/tags/form_field_errors.html')
def show_form_field_errors(field_errors, block_class=None):
    return {
        'errors': field_errors,
        'block_class': block_class,
    }
