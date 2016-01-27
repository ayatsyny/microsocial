# coding=utf-8
from django.conf.urls import url

from dialogs import views

urlpatterns = [
    url(
        r'^messages/$',
        views.DialogView.as_view(),
        name='messages'
    ),
    url(
        r'^messages/(?P<user_id>\d+)/$',
        views.DialogView.as_view(),
        name='messages'
    ),
]