# coding=utf-8
from django.contrib import messages
from django.core.mail import send_mail
from django.core.signing import Signer, BadSignature
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.views.generic import TemplateView, RedirectView
from auths.forms import RegistrationForm
from microsocial import settings
from users.models import User
from django.utils.translation import ugettext as _


signer = Signer(salt='registration-confirm')

def login_view(request):
    return render(request, 'auths/login.html')


# def register_confirm(request, activation_link):
#     try:
#          signer.unsign(activation_link)
#     except BadSignature:
#         raise Http404
#     else:
#         user_profile = get_object_or_404(UserProfile, activation_link=activation_link)
#         if user_profile.user.confirned_registration:
#             raise Http404
#         else:
#             user_profile.user.confirned_registration = True
#             user_profile.user.save()
#             messages.success(request, _(u'Авторизируйтесь пожалуйста'))
#             return redirect('login')


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

    # def post(self, request, *args, **kwargs):
    #     if self.form.is_valid():
    #         self.form.save()
    #         first_name = self.form.cleaned_data['first_name']
    #         email = self.form.cleaned_data['email']
    #         activation_link = signer.sign(first_name)
    #         user = User.objects.get(email=email)
    #         new_profile = UserProfile(user=user, activation_link=activation_link)
    #         new_profile.save()
    #         email_subject = _(u'Подтверждение регистрации')
    #         email_body = _(u'Cпасибо за регистрацию. Чтобы активировать свой аккаунт, нажмите на эту ссылку  ') + \
    #                      request.build_absolute_uri() + u'/{}/'.format(activation_link)
    #         send_mail(email_subject, email_body, 'admin@site.com', [email], fail_silently=False)
    #         return render_to_response('auths/successful_registration.html')
    #     return render(request, 'auths/registration.html', {'form': self.form})


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


class PasswordRecoveryView(TemplateView):
    template_name = 'auths/password_recovery.html'
