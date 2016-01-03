# coding=utf-8
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import login
from django.core.signing import Signer, BadSignature, TimestampSigner, SignatureExpired
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView, RedirectView
from auths.forms import RegistrationForm, LoginForm, PasswordRecoveryForm, NewPasswordForm
from microsocial import settings
from users.models import User
from django.utils.translation import ugettext as _


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
    return login(request, 'auths/login.html', 'login', authentication_form=LoginForm)


class PasswordRecoveryView(TemplateView):
    template_name = 'auths/password_recovery.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('main')
        self.form = PasswordRecoveryForm(request.POST or None)
        return super(PasswordRecoveryView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PasswordRecoveryView, self).get_context_data(**kwargs)
        context['form'] = self.form
        if 'pwd_recovery_user' in self.request.session:
            context['pwd_recovery_user'] = User.objects.get(pk=self.request.session.pop('pwd_recovery_user'))
        return context

    def post(self, request, *args, **kwargs):
        if self.form.is_valid():
            user = self.form.get_user()
            user.send_password_recovery_email()
            request.session['pwd_recovery_user'] = user.pk
            return redirect(request.path)
        return self.get(request, *args, **kwargs)


class PasswordRecoveryConfirmView(TemplateView):
    template_name = 'auths/password_recovery_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('main')
        try:
            data = TimestampSigner(salt='password-recovery-confirm').unsign(kwargs['token'], max_age=48*3600)
            user_id, last_login_hash = data.split(':')
        except (BadSignature, SignatureExpired, ValueError):
            raise Http404
        user = User.objects.get(pk=user_id)
        if user.get_last_login_hash() != last_login_hash:
            raise Http404
        if not user.confirned_registration:
            user.confirned_registration = True
            user.save(update_fields=('confirned_registration',))
        self.form = NewPasswordForm(user, request.POST or None)
        return super(PasswordRecoveryConfirmView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PasswordRecoveryConfirmView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        if self.form.is_valid():
            self.form.save()
            self.form.user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, self.form.user)
            messages.success(request, _(u'Вы успешно изменили пароль.'))
            return redirect('user_profile', user_id=self.form.user.pk, permanent=False)
        return self.get(request, *args, **kwargs)

