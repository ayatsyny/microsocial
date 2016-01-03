# coding=utf-8
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.views import login, logout_then_login
from django.core.signing import Signer, BadSignature, TimestampSigner, SignatureExpired
from django.core.urlresolvers import reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, RedirectView
from django.core.urlresolvers import reverse
from auths.forms import RegistrationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from microsocial import settings
from users.models import User
from django.utils.translation import ugettext as _


def logout_view(request):
    return logout_then_login(request)


class RegistrationView(TemplateView):
    template_name = 'auths/registration.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('main')
        self.form = RegistrationForm(request.POST or None)
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        context['form'] = self.form
        if 'registered_user_id' in self.request.session:
            context['registered_user'] = User.objects.get(pk=self.request.session.pop('registered_user_id'))
        return context

    def post(self, request, *args, **kwargs):
        if self.form.is_valid():
            user = self.form.save()
            user.send_registration_email()
            # todo send email
            request.session['registered_user_id'] = user.pk
            return redirect(request.path)
        return self.get(request, *args, **kwargs)


class RegistrationConfirmView(RedirectView):
    url = reverse_lazy(settings.LOGIN_URL)
    permanent = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            raise Http404
        try:
            user_id = Signer(salt='registration-confirm').unsign(kwargs['token'])
        except BadSignature:
            raise Http404
        user = User.objects.get(pk=user_id)
        if user.confirned_registration:
            raise Http404
        user.confirned_registration = True
        user.save(update_fields=('confirned_registration',))
        messages.success(request, _(u'Ваша регистрация успешно подтверждена. Можете войти.'))
        return super(RegistrationConfirmView, self).dispatch(request, *args, **kwargs)


def login_view(request):
    if request.user.is_authenticated():
        return redirect('main')
    response = login(request, 'auths/login.html', 'login', authentication_form=AuthenticationForm)
    return response


class PasswordRecoveryView(TemplateView):
    template_name = 'auths/password_recovery.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('main')
        self.form = PasswordResetForm(request.POST or None)
        return super(PasswordRecoveryView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PasswordRecoveryView, self).get_context_data(**kwargs)
        context['form'] = self.form
        if 'change_password_user_id' in self.request.session:
            context['change_password_user_id'] = User.objects.get(pk=self.request.session['change_password_user_id'])
        return context

    def post(self, request, *args, **kwargs):
        if self.form.is_valid():
            user = self.form.get_user()
            user.send_recovery_email()
            request.session['change_password_user_id'] = user.pk
            return redirect('password_recovery')
        return self.get(request, *args, **kwargs)


class ChangePasswordView(TemplateView):
    template_name = 'auths/password_change.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            user_last_login = TimestampSigner(salt='password-recovery-confirm').unsign(kwargs['token'], max_age=60*60*48)
        except (BadSignature, SignatureExpired):
            raise Http404
        user = None
        if 'change_password_user_id' in self.request.session:
                user = User.objects.get(pk=self.request.session['change_password_user_id'])
        if unicode(user.last_login) != unicode(user_last_login):
            raise Http404
        if not user.confirned_registration:
            user.confirned_registration = True
            user.save(update_fields=('confirned_registration',))
        self.form = SetPasswordForm(request.POST or None, user=user)
        return super(ChangePasswordView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ChangePasswordView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        if self.form.is_valid():
            self.form.save()
            password = self.form.cleaned_data['password1']
            user = auth.authenticate(username=self.form.user.email, password=password)
            if user is not None and user.is_active:
                messages.success(request, _(u'Вы успешно изменили пароль.'))
                auth.login(request, user)
            else:
                print('The username and password were incorrect.')
            return redirect('user_profile', user_id=self.form.user.pk, permanent=False)
        return self.get(request, *args, **kwargs)
