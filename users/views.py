# coding=utf-8
from django.contrib.auth import BACKEND_SESSION_KEY, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from users.forms import UserChangeProfileForm, UserPasswordChangeForm, UserEmailChangeForm, UserWallPostForm
from users.models import User, FriendInvite
from django.contrib import messages
from django.utils.translation import ugettext as _


class MyPaginator(View):
    def get_paginator(self, qs):
        paginator = Paginator(qs, 2)
        page = self.request.GET.get('page')
        try:
            paginators = paginator.page(page)
        except PageNotAnInteger:
            paginators = paginator.page(1)
        except EmptyPage:
            paginators = paginator.page(paginator.num_pages)
        return paginators


class UserProfileView(TemplateView, MyPaginator):
    template_name = 'users/profile.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.pk == int(kwargs['user_id']):
            self.user = request.user
        else:
            self.user = get_object_or_404(User, pk=kwargs['user_id'])
        self.wall_post_form = UserWallPostForm(request.POST or None)
        return super(UserProfileView, self).dispatch(request, *args, **kwargs)

    # def get_wall_posts(self, qs):
    #     paginator = qs
    #     page = self.request.GET.get('page')
    #     try:
    #         wall_posts = paginator.page(page)
    #     except PageNotAnInteger:
    #         wall_posts = paginator.page(1)
    #     except EmptyPage:
    #         wall_posts = paginator.page(paginator.num_pages)
    #     return wall_posts

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['profile_user'] = self.user
        context['wall_posts'] = self.get_paginator(self.user.wall_posts.select_related('author'))
        context['wall_post_form'] = self.wall_post_form
        return context

    def post(self, request, *args, **kwargs):
        if 'del' in request.POST:
            try:
                User.friendship.delete(self.user, request.user)
            except ValueError, e:
                messages.warning(request, e)
            else:
                messages.success(request, _(u'Удаление друга успешно выполнено.'))
            return redirect(request.path)
        if 'add' in request.POST:
            try:
                temp = FriendInvite.object.add(request.user, self.user)
            except ValueError, e:
                messages.warning(request, e)
            else:
                if temp == 1:
                    messages.success(request, _(u' Заявка успешна создана.'))
                elif temp == 2:
                    messages.success(request, _(u' Добавления друга успешно выполнено.'))
            return redirect(request.path)
        if self.wall_post_form.is_valid():
            post = self.wall_post_form.save(commit=False)
            post.user = self.user
            post.author = request.user
            post.save()
            messages.success(request, _(u'Сообщение успешно опубликовано.'))
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


class FriendsView(TemplateView, MyPaginator):
    template_name = 'users/friends/friends.html'

    def get_context_data(self, **kwargs):
        context = super(FriendsView, self).get_context_data(**kwargs)
        context['friends'] = self.get_paginator(self.request.user.friends.prefetch_related('friends'))
        context['friend_menu_key'] = 'friends'
        return context

    def post(self, request, *args, **kwargs):
        if 'del' in request.POST:
            try:
                User.friendship.delete(request.user, request.POST.get('id_user'))
            except ValueError, e:
                messages.warning(request, e)
            else:
                messages.success(request, _(u'Удаление друга успешно выполнено.'))
            return redirect(request.path)
        return self.get(request, *args, **kwargs)


class InInvitesView(TemplateView, MyPaginator):
    template_name = 'users/friends/ininvites.html'

    def get_context_data(self, **kwargs):
        context = super(InInvitesView, self).get_context_data(**kwargs)
        context['friends'] = self.get_paginator(self.request.user.in_friend_invites.select_related('to_user'))
        # context['friends'] = self.request.user.in_friend_invites.select_related('to_user')
        context['friend_menu_key'] = 'incoming'
        return context

    def post(self, request, *args, **kwargs):
        if 'approve' in request.POST:
            try:
                FriendInvite.object.approve(request.POST.get('id_user'), request.user)
            except ValueError, e:
                messages.warning(request, e)
            else:
                messages.success(request, _(u'Потверждения заявки успешно выполнено.'))
            return redirect(request.path)
        elif 'reject' in request.POST:
            FriendInvite.object.reject(request.POST.get('id_user'), request.user)
            messages.success(request, _(u'Отклонения заявки успешно выполнено.'))
            return redirect(request.path)
        return self.get(request, *args, **kwargs)


class OutInvitesView(TemplateView, MyPaginator):
    template_name = 'users/friends/outinvites.html'

    def get_context_data(self, **kwargs):
        context = super(OutInvitesView, self).get_context_data(**kwargs)
        context['friends'] = self.get_paginator(self.request.user.out_friend_invites.select_related('from_user'))
        # context['outinvites'] = self.request.user.out_friend_invites.select_related('from_user')
        context['friend_menu_key'] = 'outcoming'
        return context

    def post(self, request, *args, **kwargs):
        if 'reject' in request.POST:
            FriendInvite.object.reject(request.user, request.POST.get('id_user'))
            messages.success(request, _(u'Отмена заявки успешно выполнено.'))
            return redirect(request.path)
        return self.get(request, *args, **kwargs)
