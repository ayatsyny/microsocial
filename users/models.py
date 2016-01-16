# coding=utf-8
import hashlib
import os
from django.contrib.sites.models import Site
from django.core.signing import Signer, TimestampSigner
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from microsocial.settings import MEDIA_URL


def get_ids_from_users(*users):
    return [user.pk if isinstance(user, User) else int(user) for user in users]


class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class UserFriendShipManager(models.Manager):
    def are_friends(self, user1, user2):
        user1_id, user2_id = get_ids_from_users(user1, user2)
        return self.filter(pk=user1_id, friends__pk=user2_id).exists()

    def add(self, user1, user2):
        user1_id, user2_id = get_ids_from_users(user1, user2)
        if user1_id == user2_id:
            raise ValueError(_(u'Нельзя самого себе добавить в друзья'))
        if not self.are_friends(user1_id, user2_id):
            through_model = self.model.friends.through
            through_model.objects.bulk_create([
                through_model(from_user_id=user1_id, to_user_id=user2_id),
                through_model(from_user_id=user2_id, to_user_id=user1_id),
            ])
            FriendInvite.objects.filter(
                Q(from_user_id=user1_id, to_user_id=user2_id) | Q(from_user_id=user2_id, to_user_id=user1_id)
            ).delete()
            return True

    def delete(self, user1, user2):
        user1_id, user2_id = get_ids_from_users(user1, user2)
        if self.are_friends(user1_id, user2_id):
            through_model = self.model.friends.through
            through_model.objects.filter(
                Q(from_user_id=user1_id, to_user_id=user2_id) | Q(from_user_id=user2_id, to_user_id=user1_id)
            ).delete()
            return True


def get_avatar_fn(instance, filename):
    id_str = str(instance.pk)
    return 'avatars/{sub_dir}/{id}_{rand}{ext}'.format(
        sub_dir=id_str.zfill(2)[-2:],
        id=id_str,
        rand=get_random_string(8, 'abcdefghijklmnopqrstuvwxyz0123456789'),
        ext=os.path.splitext(filename)[1],
    )


class User(AbstractBaseUser, PermissionsMixin):
    SEX_NONE = 0
    SEX_MALE = 1
    SEX_FEMALE = 2
    SEX_CHOICES = (
        (SEX_NONE, _('-------')),
        (SEX_MALE, _(u'мужской')),
        (SEX_FEMALE, _(u'женский')),
    )
    email = models.EmailField('email', unique=True)
    first_name = models.CharField(_(u'имя'), max_length=30)
    last_name = models.CharField(_(u'фамилия'), max_length=30, blank=True)
    sex = models.SmallIntegerField(_(u'пол'), choices=SEX_CHOICES, default=SEX_NONE)
    birth_date = models.DateField(_(u'дата рождения'), null=True, blank=True)
    city = models.CharField(_(u'город'), max_length=80, blank=True)
    work_place = models.CharField(_(u'место работы'), max_length=120, blank=True)
    about_me = models.TextField(_(u'о себе'), max_length=1000, blank=True)
    interests = models.TextField(_(u'интересы'), max_length=1000, blank=True)
    avatar = models.ImageField(_(u'аватар'), upload_to=get_avatar_fn, blank=True)
    confirned_registration = models.BooleanField(_('confirmed registration'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin ' 'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    friends = models.ManyToManyField('self', symmetrical=True, verbose_name=_(u'друзья'), blank=True)

    class Meta:
        verbose_name = _(u'контактное лицо')
        verbose_name_plural = _(u'контактные лица')
        ordering = ('first_name', 'last_name')

    def __unicode__(self):
        return u'{} {}'.format(self.first_name, self.last_name)

    objects = UserManager()
    friendship = UserFriendShipManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        return u'{}{}'.format(MEDIA_URL, 'img_default/avatar.jpg')

    def get_last_login_hash(self):
        return hashlib.md5(self.last_login.strftime('%Y-%m-%d-%H-%M-%S-%f')).hexdigest()[:8]

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def send_registration_email(self):
        url = 'http://{}{}'.format(
            Site.objects.get_current().domain,
            reverse('registration_confirm', kwargs={'token': Signer(salt='registration-confirm').sign(self.pk)})
        )
        self.email_user(
            ugettext(u'Подтвердите регистрацию на Microsocial'),
            ugettext(u'Для подтверждения перейдите по ссылке: {}'.format(url))
        )

    def send_password_recovery_email(self):
        data = '{}:{}'.format(self.pk, self.get_last_login_hash())
        url = 'http://{}{}'.format(
            Site.objects.get_current().domain,
            reverse('password_recovery_confirm', kwargs={
                'token': TimestampSigner(salt='password-recovery-confirm').sign(data)
            })
        )
        self.email_user(
            ugettext(u'Подтвердите восстановления пароля на Microsocial'),
            ugettext(u'Для подтверждения перейдите по ссылке: {}'.format(url)),
            ugettext(u'Внимание данная ссылка будет действовать 48 часов')
        )


class UserWallPost(models.Model):
    user = models.ForeignKey(User, verbose_name=_(u'владелец стены'), related_name='wall_posts',)
    author = models.ForeignKey(User, verbose_name=_(u'автор'), related_name='+',)
    content = models.TextField(_(u'текст'), max_length=5000)
    created = models.DateTimeField(_(u'дата'), auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)


class FriendInviteManager(models.Manager):
    def is_pending(self, from_user, to_user):
        from_user_id, to_user_id = get_ids_from_users(from_user, to_user)
        return self.filter(from_user_id=from_user_id, to_user_id=to_user_id).exists()

    def add(self, from_user, to_user):
        from_user_id, to_user_id = get_ids_from_users(from_user, to_user)
        if from_user_id == to_user_id:
            raise ValueError(_(u'Нельзя самого себе добавить в друзья'))
        if User.friendship.are_friends(from_user_id, to_user_id):
            raise ValueError(_(u'Ви уже друзья.'))
        if self.is_pending(from_user_id, to_user_id):
            raise ValueError(_(u'Заявка уже создана и ожидает рассмотрения.'))
        if self.is_pending(to_user_id, from_user_id):
            User.friendship.add(from_user_id, to_user_id)
            return 2
        self.create(from_user_id=from_user_id, to_user_id=to_user_id)
        return 1

    def approve(self, from_user, to_user):
        from_user_id, to_user_id = get_ids_from_users(from_user, to_user)
        if not self.is_pending(from_user_id, to_user_id):
            raise ValueError(_(u'Заявка не существует.'))
        User.friendship.add(from_user, to_user)

    def reject(self, from_user, to_user):
        from_user_id, to_user_id = get_ids_from_users(from_user, to_user)
        self.filter(from_user_id=from_user_id, to_user_id=to_user_id).delete()


class FriendInvite(models.Model):
    from_user = models.ForeignKey(User, related_name='out_friend_invites')
    to_user = models.ForeignKey(User, related_name='in_friend_invites')

    objects = FriendInviteManager()

    class Meta:
        unique_together = ('from_user', 'to_user')

