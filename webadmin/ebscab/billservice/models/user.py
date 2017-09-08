# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ebscab.fields import EncryptedTextField

from billservice.models.utils import validate_phone


class SystemUser(models.Model):
    username = models.CharField(max_length=255, unique=True)
    email = models.CharField(
        verbose_name=_(u'E-mail'), blank=True, default='', max_length=200)
    fullname = models.CharField(
        verbose_name=_(u'ФИО'), max_length=512, blank=True, default='')
    home_phone = models.CharField(
        validators=[validate_phone],
        verbose_name=_(u'Дом. телефон'),
        max_length=512,
        blank=True,
        default=''
    )
    mobile_phone = models.CharField(
        validators=[validate_phone],
        verbose_name=_(u'Моб. телефон'),
        help_text=_(u'В международном формате +71231231212'),
        max_length=512,
        blank=True,
        default=''
    )
    address = models.CharField(
        verbose_name=_(u'Адрес'),
        max_length=512,
        blank=True,
        default=''
    )
    job = models.CharField(
        verbose_name=_(u'Должность'),
        max_length=256,
        blank=True,
        default=''
    )
    last_ip = models.CharField(
        verbose_name=_(u'Последний IP'),
        max_length=64,
        blank=True,
        null=True
    )
    last_login = models.DateTimeField(
        verbose_name=_(u'Последний логин'),
        blank=True,
        null=True
    )
    description = models.TextField(
        verbose_name=_(u'Комментарий'),
        blank=True,
        default=''
    )
    created = models.DateTimeField(
        verbose_name=_(u'Создан'),
        blank=True,
        null=True,
        auto_now_add=True
    )
    status = models.BooleanField(
        verbose_name=_(u'Статус'), default=False)
    host = models.CharField(
        verbose_name=_(u'Разрешённые IP'),
        max_length=255,
        blank=True,
        null=True,
        default="0.0.0.0/0"
    )
    text_password = EncryptedTextField(
        verbose_name=_(u'Пароль'), blank=True, default='')
    passport = EncryptedTextField(
        verbose_name=_(u'№ паспорта'),
        max_length=512,
        blank=True,
        default=''
    )
    passport_details = models.CharField(
        verbose_name=_(u'Паспорт выдан'),
        max_length=512,
        blank=True,
        default=''
    )
    passport_number = models.CharField(
        verbose_name=_(u'Личный номер'),
        max_length=512,
        blank=True,
        default=''
    )
    unp = models.CharField(
        verbose_name=_(u'УНП'),
        max_length=1024,
        blank=True,
        default=''
    )
    im = models.CharField(
        verbose_name=_(u'ICQ/Skype'),
        max_length=512,
        blank=True,
        default=''
    )
    permissiongroup = models.ForeignKey(
        'billservice.PermissionGroup',
        blank=True,
        null=True,
        verbose_name=_(u"Группа доступа"),
        on_delete=models.CASCADE
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name=_(u"Суперадминистратор")
    )

    permcache = {}

    def __str__(self):
        return '%s' % self.username

    def __unicode__(self):
        return u'%s' % self.username

    def is_authenticated(self):
        """Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def get_absolute_url(self):
        return "%s?id=%s" % (reverse('systemuser_edit'), self.id)

    def save(self, *args, **kwargs):
        try:
            user = User.objects.get(username=self.username)
        except:
            user = User()
            user.username = self.username
            user.set_password(self.text_password)
        user.is_staff = True
        user.is_active = self.status
        user.first_name = self.fullname
        user.is_superuser = self.is_superuser
        user.save()
        super(SystemUser, self).save(*args, **kwargs)

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('systemuser_delete'), self.id)

    def has_perm(self, perm):
        app, internal_name = perm.split('.')
        r = self.status and (self.is_superuser or (
            (self.permissiongroup.permissions
             .filter(app=app, internal_name=internal_name)
             .exists()) if self.permissiongroup else False))
        return r

    def delete(self):
        return

    class Meta:
        ordering = ['username']
        verbose_name = _(u"Пользователь системы")
        verbose_name_plural = _(u"Пользователи системы")
        permissions = (
            ("systemuser_view", _(u"Просмотр администраторов")),
            ("get_model", _(u"Получение любой модели методом get_model")),
            ("actions_set", _(u"Установка IPN статуса на сервере доступаl")),
            ("documentrender", _(u"Серверный рендеринг документов")),
            ("testcredentials", _(u"Тестирование данных для сервера доступа")),
            ("getportsstatus", _(u"Получение статуса портов коммутатора")),
            ("setportsstatus", _(u"Установка статуса портов коммутатора")),
            ("list_log_files", _(u"Список лог-файлов биллинга")),
            ("view_log_files", _(u"Просмотр лог-файлов биллинга")),
            ("transactions_delete", _(u"Удаление проводок")),
            ("sp_info", _(u"Метод sp_info")),
            ("auth_groups", _(u"Просмотр груп доступа")),
            ("rawsqlexecution", _(u"Выполнение любого sql запроса"))
        )
