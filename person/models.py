# coding=utf-8
from django.db import models
from microsocial import settings


class Person(models.Model):
    SEX_MALE = 0
    SEX_FEMALE = 1
    SEX_CHOICES = (
        (SEX_MALE, u'мужской'),
        (SEX_FEMALE, u'женский'),
    )
    first_name = models.CharField(verbose_name=u'имя', max_length=80)
    last_name = models.CharField(verbose_name=u'фамилия', max_length=80, blank=True)
    sex = models.NullBooleanField(verbose_name=u'пол', choices=SEX_CHOICES, default=None)
    birth_date = models.DateField(verbose_name=u'дата рождения', blank=True)
    city = models.CharField(verbose_name=u'город', max_length=80, blank=True)
    work_place = models.CharField(verbose_name=u'место работы', max_length=120, blank=True)
    info_yourself = models.TextField(verbose_name=u'о себе', max_length=500, blank=True)
    interests = models.TextField(verbose_name=u'интересы', max_length=400, blank=True)
    image = models.ImageField(default='img_default/avatar.jpg', upload_to='img')
    friends = models.ManyToManyField('self', symmetrical=True)
    login_id = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='login')

    class Meta:
        verbose_name = u'контактное лицо'
        verbose_name_plural = u'контактные лица'
        ordering = ('first_name', 'last_name')

    def __unicode__(self):
        return u'{} {}'.format(self.first_name, self.last_name)


class Message(models.Model):
    person = models.ForeignKey(Person, verbose_name=u'пользователь', related_name='persons')
    created = models.DateTimeField(verbose_name=u'дата создания', auto_now_add=True)
    body = models.TextField(verbose_name=u'сообщение', max_length=600, blank=True)
