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
                views.UserFriendsView.as_view(),
                name='user_friends'
            ),
            url(
                r'^incoming/$',
                views.UserIncomingView.as_view(),
                name='user_incoming'
            ),
            url(
                r'^outcoming/$',
                views.UserOutcomingView.as_view(),
                name='user_outcoming'
            ),
        ]),
    ),
    url(
        r'^api/friendship/$',
        views.FriendshipAPIView.as_view(),
        name='user_friendship_api'
    ),
]
