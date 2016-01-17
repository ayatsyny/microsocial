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
    url(
        r'^friends/', include([
            url(
                r'^$',
                views.FriendsView.as_view(),
                name='friends'
            ),
            url(
                r'^incoming/$',
                views.InInvitesView.as_view(),
                name='incoming'
            ),
            url(
                r'^outcoming/$',
                views.OutInvitesView.as_view(),
                name='outcoming'
            ),
        ]),
    ),
]
