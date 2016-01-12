# coding=utf-8
from django import template
from microsocial import settings

register = template.Library()


@register.filter
def get_avatar(user):
    try:
        return user.avatar.url
    except ValueError:
        return '{}users/img/avatar.jpg'.format(settings.STATIC_URL)
