# coding=utf-8
from django.conf.urls import patterns, include, url
from users import views
from users.views import UserSettingsView

urlpatterns = [
    url(
        r'^profile/(?P<user_id>\d+)/$',
        views.UserProfileView.as_view(),
        name='user_profile'
    ),
    url(
        r'^settings/$',
        UserSettingsView.as_view(),
        name='user_settings'
    ),
]
