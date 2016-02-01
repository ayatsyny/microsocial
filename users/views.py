# coding=utf-8
import datetime
from django.contrib.auth import BACKEND_SESSION_KEY, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, View
from users.forms import UserChangeProfileForm, UserPasswordChangeForm, UserEmailChangeForm, UserWallPostForm, SearchForm
from users.models import User, FriendInvite, FriendInfo
from django.contrib import messages
from django.utils.translation import ugettext as _


class MyPaginator(View):
    def get_paginator(self, qs):
        paginator = Paginator(qs, 20)
        page = self.request.GET.get('page')
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return items


class UserProfileView(TemplateView, MyPaginator):
    template_name = 'users/profile.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.pk == int(kwargs['user_id']):
            self.user = request.user
        else:
            self.user = get_object_or_404(User, pk=kwargs['user_id'])
        self.wall_post_form = UserWallPostForm(request.POST or None)
        return super(UserProfileView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['profile_user'] = self.user
        # context['wall_posts'] = self.get_wall_posts()
        context['wall_posts'] = self.get_paginator(self.user.wall_posts.select_related('author'))
        context['wall_post_form'] = self.wall_post_form
        if self.request.user != self.user:
            context['is_my_friend'] = User.friendship.are_friends(self.request.user, self.user)
        return context

    def post(self, request, *args, **kwargs):
        if self.wall_post_form.is_valid():
            post = self.wall_post_form.save(commit=False)
            post.user = self.user
            post.author = request.user
            post.save()
            FriendInfo.friendinfom.add_post_wall(post.author.pk, post.user.pk, post)
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


class UserFriendsView(TemplateView, MyPaginator):
    template_name = 'users/friends_friends.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserFriendsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserFriendsView, self).get_context_data(**kwargs)
        context['friends_menu'] = 'friends'
        context['items'] = self.get_paginator(self.request.user.friends.all())
        return context


class UserIncomingView(TemplateView, MyPaginator):
    template_name = 'users/friends_incoming.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserIncomingView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserIncomingView, self).get_context_data(**kwargs)
        context['friends_menu'] = 'incoming'
        context['items'] = self.get_paginator(self.request.user.in_friend_invites.all())
        return context


class UserOutcomingView(TemplateView, MyPaginator):
    template_name = 'users/friends_outcoming.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserOutcomingView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserOutcomingView, self).get_context_data(**kwargs)
        context['friends_menu'] = 'outcoming'
        context['items'] = self.get_paginator(self.request.user.out_friend_invites.all())
        return context


class FriendshipAPIView(View):
    @method_decorator(login_required)
    @method_decorator(require_POST)
    def dispatch(self, request, *args, **kwargs):
        method_name = '_action_{}'.format(request.POST.get('action', ''))
        if not hasattr(self, method_name):
            raise Http404
        default_url = getattr(self, method_name)()
        return redirect(request.POST.get('next') or default_url or 'main')

    def _get_user_from_post_field(self, field_name):
        try:
            return User.objects.get(pk=self.request.POST.get(field_name))
        except (User.DoesNotExist, ValueError):
            pass

    def _action_add_to_friends(self):
        user = self._get_user_from_post_field('user_id')
        if user:
            try:
                r = FriendInvite.objects.add(self.request.user, user)
            except ValueError, e:
                messages.warning(self.request, e)
            else:
                if r == 1:
                    messages.success(self.request, _(u'Заявка успешно отправлена и ожидает рассмотрения.'))
                elif r == 2:
                    messages.success(self.request, _(u'Пользователь успешно добавлен в друзья.'))
                    return 'user_friends'
        return 'user_outcoming'

    def _action_delete_from_friends(self):
        user = self._get_user_from_post_field('user_id')
        if user:
            if User.friendship.delete(self.request.user, user):
                messages.success(self.request, _(u'Пользователь успешно удален из друзей.'))
        return 'user_friends'

    def _action_approve(self):
        user = self._get_user_from_post_field('user_id')
        if user:
            try:
                r = FriendInvite.objects.approve(user, self.request.user)
            except ValueError, e:
                messages.warning(self.request, e)
            else:
                if r:
                    messages.success(self.request, _(u'Заявка успешно подтверждена. Пользователь добавлен в друзья.'))
        return 'user_incoming'

    def _action_reject(self):
        user = self._get_user_from_post_field('user_id')
        if user:
            FriendInvite.objects.reject(user, self.request.user)
            messages.success(self.request, _(u'Заявка успешно отклонена.'))
        return 'user_incoming'

    def _action_cancel_outcoming(self):
        user = self._get_user_from_post_field('user_id')
        if user:
            FriendInvite.objects.filter(from_user=self.request.user, to_user=user).delete()
            messages.success(self.request, _(u'Заявка успешно отменена.'))
        return 'user_outcoming'


class SearchView(TemplateView):
    template_name = 'users/search.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.form = SearchForm(request.GET or None)
        return super(SearchView, self).dispatch(request, *args, **kwargs)

    def get_filtered_qs(self, qs):
        self.form.is_valid()
        if not hasattr(self.form, 'cleaned_data'):
            return qs
        if self.form.cleaned_data.get('name'):
            query = None
            for val in self.form.get_values_list('name'):
                q = Q(first_name__icontains=val) | Q(last_name__icontains=val)
                if query is None:
                    query = q
                else:
                    query |= q
            if query:
                qs = qs.filter(query)
        if self.form.cleaned_data.get('sex'):
            qs = qs.filter(sex=self.form.cleaned_data['sex'])
        if self.form.cleaned_data.get('by_from'):
            qs = qs.filter(birth_date__gte=datetime.datetime(self.form.cleaned_data['by_from'], 1, 1))
        if self.form.cleaned_data.get('by_to'):
            qs = qs.filter(birth_date__lt=datetime.datetime(self.form.cleaned_data['by_to'] + 1, 1, 1))
        for field_name in ('city', 'work_place', 'about_me', 'interests'):
            query = None
            for val in self.form.get_values_list(field_name):
                q = Q(**{'{}__icontains'.format(field_name): val})
                if query is None:
                    query = q
                else:
                    query |= q
            if query:
                qs = qs.filter(query)
        return qs

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['form'] = self.form
        qs = self.get_filtered_qs(User.objects.all())
        paginator = Paginator(qs, 20)
        page = self.request.GET.get('page')
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        context['items'] = items
        return context


class NewsView(TemplateView, MyPaginator):
    template_name = 'users/news.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super(NewsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NewsView, self).get_context_data(**kwargs)
        context['items'] = self.get_paginator(self.user.news.all())
        return context
