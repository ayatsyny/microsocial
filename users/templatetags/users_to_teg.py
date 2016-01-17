# coding=utf-8
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
def are_friend(user1, user2):
    return User.friendship.are_friends(user1, user2)
