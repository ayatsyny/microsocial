# coding=utf-8
from django import forms
from microsocial.forms import BootstrapFormMixin
from users.models import User
from django.utils.translation import ugettext_lazy as _, ugettext


class RegistrationForm(forms.ModelForm, BootstrapFormMixin):
    # error_messages = {
    #     'duplicate_email': _("A user with that email already exists."),
    #     'password_mismatch': _("The two password fields didn't match."),
    # }
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

    # def clean_password2(self):
    #     password1 = self.cleaned_data.get("password1")
    #     password2 = self.cleaned_data.get("password2")
    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError(
    #             self.error_messages['password_mismatch'],
    #             code='password_mismatch',
    #         )
    #     return password2

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.confirned_registration = False
        if commit:
            user.save()
        return user
