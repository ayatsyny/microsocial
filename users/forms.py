# coding=utf-8
from django.contrib.auth.forms import PasswordChangeForm
from django.core import validators
from django import forms
from django.utils.translation import ugettext_lazy as _, ugettext
from microsocial.forms import BootstrapFormMixin
from users.models import User, UserWallPost


class UserPasswordChangeForm(PasswordChangeForm, BootstrapFormMixin):
    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        for field_name in ('old_password', 'new_password1', 'new_password2'):
            self.fields[field_name] = self.fields.pop(field_name)
            if field_name != 'old_password':
                self.fields[field_name].validators.extend([validators.MinLengthValidator(6),
                                                           validators.MaxLengthValidator(40)])


class UserChangeProfileForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = User
        fields = ('avatar', 'first_name', 'last_name', 'sex', 'birth_date', 'city', 'work_place', 'about_me',
                  'interests')
        widgets = {
            'about_me': forms.Textarea(attrs={'cols': 10, 'rows': 5}),
            'interests': forms.Textarea(attrs={'cols': 10, 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super(UserChangeProfileForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        self.fields['birth_date'].widget.attrs['placeholder'] = ugettext(u'Введите дату в формате ГГГГ-ММ-ДД')


class UserEmailChangeForm(forms.Form, BootstrapFormMixin):
    new_email = forms.EmailField(max_length=75, label=_(u'новый email'))
    password = forms.CharField(label=_(u'текущий пароль'), min_length=6, max_length=40, widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserEmailChangeForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)

    def clean_new_email(self):
        new_email = self.cleaned_data['new_email'].strip()
        if User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError(ugettext(u'Пользователь с таким email уже существует.'))
        return new_email

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError(ugettext(u'Введен неправильний пароль.'))
        return password

    def save(self, commit=True):
        self.user.email = self.cleaned_data['new_email']
        if commit:
            self.user.save()
        return self.user


# class MessageSendWallForm(forms.ModelForm, BootstrapFormMixin):
#     class Meta:
#         model = PostWall
#         fields = ('content',)
#         widgets = {
#             'content': forms.Textarea(attrs={'cols': 10, 'rows': 5}),
#         }
#
#     def __init__(self, user, author, *args, **kwargs):
#         self.user = user
#         self.author = author
#         super(MessageSendWallForm, self).__init__(*args, **kwargs)
#         BootstrapFormMixin.__init__(self)
#         self.fields['content'].widget.attrs['placeholder'] = ugettext(u'напишите на стене...')
#
#     def save(self, commit=True):
#         post = super(MessageSendWallForm, self).save(commit=False)
#         post.content = self.cleaned_data['content']
#         post.wall_owner = self.user
#         post.author = self.author
#         # self.Meta.model.content = self.cleaned_data['content']
#         # self.Meta.model.wall_owner = self.user.pk
#         # self.Meta.model.author = self.author
#         if commit:
#             post.save()
#         return post

class UserWallPostForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = UserWallPost
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': _(u'напишите на стене ...')})
        }

    def __init__(self, *args, **kwargs):
        super(UserWallPostForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)

    def clean_content(self):
        return self.cleaned_data['content'].strip()
