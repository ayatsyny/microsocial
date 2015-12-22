# coding=utf-8
from django.db import models
from microsocial import settings
from django.utils.translation import ugettext_lazy as _


class Person(models.Model):
    SEX_MALE = 0
    SEX_FEMALE = 1
    SEX_CHOICES = (
        (SEX_MALE, _(u'мужской')),
        (SEX_FEMALE, _(u'женский')),
    )
    first_name = models.CharField(verbose_name=_(u'имя'), max_length=80)
    last_name = models.CharField(verbose_name=_(u'фамилия'), max_length=80, blank=True)
    sex = models.NullBooleanField(verbose_name=_(u'пол'), choices=SEX_CHOICES, default=None)
    birth_date = models.DateField(verbose_name=_(u'дата рождения'), blank=True)
    city = models.CharField(verbose_name=_(u'город'), max_length=80, blank=True)
    work_place = models.CharField(verbose_name=_(u'место работы'), max_length=120, blank=True)
    info_yourself = models.TextField(verbose_name=_(u'о себе'), max_length=500, blank=True)
    interests = models.TextField(verbose_name=_(u'интересы'), max_length=400, blank=True)
    image = models.ImageField(verbose_name=_(u'картинка'), default='img_default/avatar.jpg', upload_to='img', blank=True)
    friends = models.ManyToManyField('self', symmetrical=True, verbose_name=_(u'друзья'), blank=True)
    login = models.OneToOneField(settings.AUTH_USER_MODEL, default=None, verbose_name=_(u'логин'))

    class Meta:
        verbose_name = _(u'контактное лицо')
        verbose_name_plural = _(u'контактные лица')
        ordering = ('first_name', 'last_name')

    def __unicode__(self):
        return u'{} {}'.format(self.first_name, self.last_name)


class Message(models.Model):
    person = models.ForeignKey(Person, verbose_name=_(u'пользователь'), related_name='persons')
    created = models.DateTimeField(verbose_name=_(u'дата создания'), auto_now_add=True)
    body = models.TextField(verbose_name=_(u'сообщение'), max_length=600, blank=True)
