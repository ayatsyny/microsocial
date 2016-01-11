# coding=utf-8
from django.contrib.auth import BACKEND_SESSION_KEY, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from users.forms import UserChangeProfileForm, UserPasswordChangeForm, UserEmailChangeForm, MessageSendWallForm
from users.models import User, PostWall
from django.contrib import messages
from django.utils.translation import ugettext as _


class UserProfileView(TemplateView):
    template_name = 'users/profile.html'

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(User, pk=kwargs.get('user_id'))
        self.qs = PostWall.objects.select_related('wall_owner', 'author').filter(wall_owner=self.instance.pk).order_by('-date_created',)
        self.form = MessageSendWallForm(self.instance, request.user, request.POST or None)
        paginator = Paginator(self.qs, 20)
        page = request.GET.get('page')
        try:
            self.post_wall = paginator.page(page)
        except PageNotAnInteger:
            self.post_wall = paginator.page(1)
        except EmptyPage:
            self.post_wall = paginator.page(paginator.num_pages)
        return super(UserProfileView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['user_profile'] = self.instance
        context['post_wall'] = self.post_wall
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        if self.form.is_valid():
            self.form.save()
            return redirect(request.path)
        return self.get(request, *args, **kwargs)


class UserSettingsView(TemplateView):
    template_name = 'users/settings.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        action = request.POST.get('action')
        self.profile_form = UserChangeProfileForm(
                (request.POST if action == 'profile' else None),
                (request.FILES if action == 'profile' else None),
                instance=request.user, prefix='profile'
        )
        self.password_form = UserPasswordChangeForm(request.user, (request.POST if action == 'password' else None),
                                                    prefix='password')
        self.email_form = UserEmailChangeForm(request.user, request.POST if action == 'email' else None, prefix='email')
        return super(UserSettingsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserSettingsView, self).get_context_data(**kwargs)
        context['profile_form'] = self.profile_form
        context['password_form'] = self.password_form
        context['email_form'] = self.email_form
        return context

    def post(self, request, *args, **kwargs):
        if self.profile_form.is_valid():
            self.profile_form.save()
            messages.success(request, _(u'Вы успешно изменили свой профиль.'))
            return redirect(request.path)
        elif self.password_form.is_valid():
            self.password_form.save()
            request.user.backend = request.session[BACKEND_SESSION_KEY]
            login(request, request.user)
            messages.success(request, _(u'Пароль успешно изменен.'))
            return redirect(request.path)
        elif self.email_form.is_valid():
            self.email_form.save()
            messages.success(request, _(u'Email успешно изменен.'))
            return redirect(request.path)
        return self.get(request, *args, **kwargs)