# coding=utf-8
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from microsocial.forms import BootstrapFormMixin
from users.models import User
from django.utils.translation import ugettext_lazy as _, ugettext


class RegistrationForm(forms.ModelForm, BootstrapFormMixin):
    password1 = forms.CharField(label=_(u'пароль'), required=True, min_length=6, max_length=40,
                                widget=forms.PasswordInput, initial='password')
    password2 = forms.CharField(label=_(u'повтор пароля'), min_length=6, max_length=40,
                                widget=forms.PasswordInput, initial='password')

    class Meta:
        model = User
        fields = ('first_name', 'email')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)

    def clean(self):
        data = super(RegistrationForm, self).clean()
        if 'password1' not in self.errors and 'password2' not in self.errors:
            if data['password1'] != data['password2']:
                self.add_error('password1', ugettext(u'Пароли не совпадают.'))

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(ugettext(u'Пользователь с таким email уже существует.'))
        return email

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.confirned_registration = False
        if commit:
            user.save()
        return user


class AuthenticationForm(forms.ModelForm, BootstrapFormMixin):
    password = forms.CharField(label=_(u'пароль'), required=True, min_length=6, max_length=40,
                               widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        UserModel = get_user_model()
        self.email_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        if self.fields['email'].label is None:
            self.fields['email'].label = capfirst(self.email_field.verbose_name)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user_cache = authenticate(email=email,
                                           password=password)
            if self.user_cache is None:
                # self.add_error('password', ValidationError(ugettext(u'Пожалуйста, введите правильный %(email)s и пароль. '), code='invalid_login'))
                raise forms.ValidationError(
                     ugettext(u'Пожалуйста, введите правильный %(email)s и пароль. '), code='invalid_login',
                )
        else:
            raise forms.ValidationError(
                     ugettext(u'Пожалуйста, введите правильный %(email)s и пароль. '), code='invalid_login',
            )
            #     self.confirm_login_allowed(self.user_cache)
        # return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class PasswordResetForm(forms.Form, BootstrapFormMixin):
    email = forms.EmailField(label=_('email'), max_length=254)

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        self.user_cache = None

    def clean_email(self):
        cleaned_data = super(PasswordResetForm, self).clean()
        email = cleaned_data.get('email')
        if email:
            if not User.objects.filter(email=email).exists():
                raise forms.ValidationError(ugettext(u'Пользователь с таким email не существует.'))
            else:
                self.user_cache = User.objects.get(email=email)

    def get_user(self):
        if self.user_cache:
            return self.user_cache
        return None


class SetPasswordForm(forms.Form, BootstrapFormMixin):
    password1 = forms.CharField(label=_(u'пароль'), min_length=6, max_length=40,
                                    widget=forms.PasswordInput)
    password2 = forms.CharField(label=_(u'повтор пароля'), min_length=6, max_length=40,
                                    widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)

    def clean(self):
        data = super(SetPasswordForm, self).clean()
        if 'password1' not in self.errors and 'password2' not in self.errors:
            if data['password1'] != data['password2']:
                self.add_error('password1', ugettext(u'Пароли не совпадают.'))

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['password1'])
        if commit:
            self.user.save()
        return self

