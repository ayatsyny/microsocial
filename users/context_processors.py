# coding=utf-8
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

FRIEND_MENU = (
    ('friends', {'url': reverse_lazy('friends'), 'title': _(u'Друзья')}),
    ('incoming', {'url': reverse_lazy('incoming'), 'title': _(u'Входящие заявки')}),
    ('outcoming', {'url': reverse_lazy('outcoming'), 'title': _(u'Исходящие заявки')}),
)


def friend_menu(request):
    return {
        'FRIEND_MENU': FRIEND_MENU,
    }

