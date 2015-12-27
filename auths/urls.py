# coding=utf-8
from django.conf.urls import url, include
from auths import views

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
        r'^password-recovery$',
        views.PasswordRecoveryView.as_view(),
        name='password_recovery'
    ),
]