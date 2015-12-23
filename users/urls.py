# coding=utf-8
from django.conf.urls import patterns, include, url
from users import views

urlpatterns = [
    url(
        r'^profile/(?P<user_id>\d+)/$',
        views.UserProfileView.as_view(),
        name='user_profile'
    ),
]
