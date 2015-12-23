# coding=utf-8
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone


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
    birth_date = models.DateField(_(u'дата рождения'), blank=True)
    city = models.CharField(_(u'город'), max_length=80, blank=True)
    work_place = models.CharField(_(u'место работы'), max_length=120, blank=True)
    about_me = models.TextField(_(u'о себе'), max_length=1000, blank=True)
    interests = models.TextField(_(u'интересы'), max_length=1000, blank=True)
    image = models.ImageField(_(u'картинка'), default='img_default/avatar.jpg', upload_to='img', blank=True)
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
