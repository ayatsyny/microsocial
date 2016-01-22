# coding=utf-8
from django.utils import timezone
from django import template
from microsocial.settings import STATIC_URL

register = template.Library()


@register.filter
def get_avatar(user):
    try:
        return user.avatar.url
    except ValueError:
        return '{}users/img/avatar.jpg'.format(STATIC_URL)


@register.filter
def are_year_user(date):
    return timezone.now().year - date.year


@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()
