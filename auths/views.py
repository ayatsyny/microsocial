# coding=utf-8
from django.contrib import messages
from django.core.mail import send_mail
from django.core.signing import Signer, BadSignature
from django.http import Http404
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.views.generic import TemplateView
from auths.forms import UserCreationForm
from auths.models import UserProfile
from users.models import User
from django.utils.translation import ugettext as _


signer = Signer(salt='registration-confirm')

def login_view(request):
    return render(request, 'auths/login.html')


def register_confirm(request, activation_link):
    try:
         signer.unsign(activation_link)
    except BadSignature:
        raise Http404
    else:
        user_profile = get_object_or_404(UserProfile, activation_link=activation_link)
        if user_profile.user.confirned_registration:
            raise Http404
        else:
            user_profile.user.confirned_registration = True
            user_profile.user.save()
            messages.success(request, _(u'Авторизируйтесь пожалуйста'))
            return redirect('login')


class RegistrationView(TemplateView):
    template_name = 'auths/registration.html'

    def dispatch(self, request, *args, **kwargs):
        self.form = UserCreationForm(request.POST or None)
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        if self.form.is_valid():
            self.form.save()
            first_name = self.form.cleaned_data['first_name']
            email = self.form.cleaned_data['email']
            activation_link = signer.sign(first_name)
            user = User.objects.get(email=email)
            new_profile = UserProfile(user=user, activation_link=activation_link)
            new_profile.save()
            email_subject = _(u'Подтверждение регистрации')
            email_body = _(u'Cпасибо за регистрацию. Чтобы активировать свой аккаунт, нажмите на эту ссылку  ') + \
                         request.build_absolute_uri() + u'/{}/'.format(activation_link)
            send_mail(email_subject, email_body, 'admin@site.com', [email], fail_silently=False)
            return render_to_response('auths/successful_registration.html')
        return render(request, 'auths/registration.html', {'form': self.form})


class PasswordRecoveryView(TemplateView):
    template_name = 'auths/password_recovery.html'
