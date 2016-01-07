# coding=utf-8
from django.conf.urls import url, include
from django.contrib.auth.views import logout
from auths import views
from microsocial import settings

urlpatterns = [
    url(
        r'^login$',
        views.login_view,
        name='login'
    ),
    url(
        r'^registration/', include([
            url(
                r'^$',
                views.RegistrationView.as_view(),
                name='registration'
            ),
            url(
                r'^(?P<token>.+)/$',
                views.RegistrationConfirmView.as_view(),
                name='registration_confirm'
            ),
        ])
    ),
    url(
        r'^password-recovery/', include([
            url(
                r'^$',
                views.PasswordRecoveryView.as_view(),
                name='password_recovery'
            ),
            url(
                r'^(?P<token>.+)/$',
                views.PasswordRecoveryConfirmView.as_view(),
                name='password_recovery_confirm'
            ),
        ]),
    ),
    url(
        r'^logout/$',
        logout,
        {'next_page': settings.LOGIN_URL},
        name='logout'
    ),
    # url(
    #     r'^settings/$',
    #     SettingsView.as_view(),
    #     name='settings'
    # ),
]
