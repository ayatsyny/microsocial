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


class SearchUserForm(forms.Form, BootstrapFormMixin):
    name = forms.CharField(label=_(u'имя ы фамилия'), required=False, max_length=70, widget=forms.TextInput(attrs={'placeholder': u'Имя, Фамилия'}))
    sex = forms.TypedChoiceField(label=_(u'пол'), choices=[('0', u'все'), ('1', _(u'мужской')), ('2', _(u'женский'))], coerce=int, required=False)
    birth_date = forms.IntegerField(label=_(u'год рождения'), min_value=1880, required=False)
    birth_date_end = forms.IntegerField(label=_(u'год рождения'), min_value=1881, required=False)
    city = forms.CharField(label=_(u'город'), max_length=80, required=False)
    work_place = forms.CharField(label=_(u'место работы'), max_length=120, required=False)
    about_me = forms.CharField(label=_(u'о себе'), max_length=1000, widget=forms.TextInput(attrs={'rows': 1}), required=False)
    interests = forms.CharField(label=_(u'интересы'), max_length=1000, widget=forms.TextInput(attrs={'rows': 1}), required=False)

    def __init__(self, *args, **kwargs):
        super(SearchUserForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)

    def clean(self):
        if self.cleaned_data['name']:
            char = ' '
            if self.cleaned_data['name'].find(',') != -1:
                char = ','
            temp = [item.strip() for item in self.cleaned_data['name'].strip().split(char)]
            if len(temp) == 2:
                self.cleaned_data['first_name'], self.cleaned_data['last_name'] = temp[:2]
            elif len(temp) == 1:
                if User.objects.filter(first_name__contains=temp[0]).exists():
                    self.cleaned_data['first_name'] = temp[0]
                elif User.objects.filter(last_name__contains=temp[0]).exists():
                    self.cleaned_data['last_name'] = temp[0]
                else:
                    self.cleaned_data['first_name'] = temp[0]
        for key, value in self.cleaned_data.items():
            if not value or key == 'name':
                del self.cleaned_data[key]
        return self.cleaned_data

