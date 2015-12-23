from django.shortcuts import render
from django.views.generic import TemplateView


def login_view(request):
    return render(request, 'auths/login.html')


class RegistrationView(TemplateView):
    template_name = 'auths/registration.html'


class PasswordRecoveryView(TemplateView):
    template_name = 'auths/password_recovery.html'
