# coding=utf-8
from collections import OrderedDict

from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordChangeForm
from django.core import validators
from django.core.exceptions import ValidationError
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


class LoginForm(AuthenticationForm, BootstrapFormMixin):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)

    def clean(self):
        has_error = False
        try:
            super(LoginForm, self).clean()
        except forms.ValidationError:
            has_error = True
        if has_error or self.errors or (self.user_cache and not self.user_cache.confirned_registration):
            raise forms.ValidationError(ValueError(ugettext(u'Неправильний email или пароль.')))


class PasswordRecoveryForm(forms.Form, BootstrapFormMixin):
    email = forms.EmailField(label=_(u'email'))

    def __init__(self, *args, **kwargs):
        super(PasswordRecoveryForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        self._user = None

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            self._user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(_(u'Пользователя с таким email не существует.'))
        return email

    def get_user(self):
        return self._user


class NewPasswordForm(SetPasswordForm, BootstrapFormMixin):
    def __init__(self, *args, **kwargs):
        super(NewPasswordForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        for field_name in ('new_password1', 'new_password2'):
            self.fields[field_name].validators.extend([validators.MinLengthValidator(6),
                                                      validators.MaxLengthValidator(40)])


class ChangeOldPasswordForm(PasswordChangeForm, BootstrapFormMixin):
    def __init__(self, *args, **kwargs):
        super(ChangeOldPasswordForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        for field_name in ('old_password', 'new_password1', 'new_password2'):
            self.fields[field_name].validators.extend([validators.MinLengthValidator(6),
                                                      validators.MaxLengthValidator(40)])
            self.fields[field_name].label = _(u'новый пароль')
        self.fields['old_password'].label = _(u'текущий пароль')

ChangeOldPasswordForm.base_fields = OrderedDict(
    (k, PasswordChangeForm.base_fields[k])
    for k in ['old_password', 'new_password1', 'new_password2']
)


class ChangeProfileForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = User
        exclude = ('email', 'confirned_registration', 'is_staff', 'is_active', 'date_joined', 'password', 'last_login',
                   'is_superuser', 'groups', 'user_permissions')
        widgets = {                   # виджеты для полей
                'about_me': forms.Textarea(attrs={'cols': 10, 'rows': 5}),
                'interests': forms.Textarea(attrs={'cols': 10, 'rows': 5}),
            }

    def __init__(self, *args, **kwargs):
        super(ChangeProfileForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)

    def save(self, commit=True):
        user = super(ChangeProfileForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class ChangeEmailForm(forms.ModelForm, BootstrapFormMixin):
    new_email = forms.EmailField(label=_(u'новый email'))
    password = forms.CharField(label=_(u'текущий пароль'), min_length=6, max_length=40, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)
        labels = {
            'email': _(u'текущий email'),
        }

    def __init__(self, *args, **kwargs):
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        self._user = getattr(self, 'instance', None)
        if self._user and self._user.pk:
            self.fields['email'].widget.attrs['readonly'] = True

    def clean(self):
        data = super(ChangeEmailForm, self).clean()
        new_email = data.get('new_email')
        password = data.get('password')
        if new_email and password:
            if User.objects.filter(email=new_email).exists():
                raise self.add_error('new_email', ValidationError(ugettext(u'Пользователь с таким email уже существует.'),
                                                              code='duplicate_email'))
            if not self._user.check_password(password):
                raise self.add_error('password', ValidationError(ugettext(u'Пароли не верний.'), code='incorect_password'))

    def save(self, commit=True):
        self._user.email = self.cleaned_data['new_email']
        if commit:
            self._user.save(update_fields=('email',))
        return self._user
