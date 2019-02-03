# -*- coding: utf-8 -*-

import datetime

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from dynamicmodel.models import DynamicModel
from ebscab.fields import IPAddressField, IPNetworkField, EncryptedTextField
from nas.models import Nas

from billservice.models.constants import ACCOUNT_STATUS, STATUS_CLASS
from billservice.models.managers import SoftDeletedDateManager
from billservice.models.utils import get_model, validate_phone


class AccountGroup(models.Model):
    name = models.CharField(max_length=512)

    def __unicode__(self):
        return u"%s" % self.name

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accountgroup_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Группа абонентов")
        verbose_name_plural = _(u"Группы абонентов")
        permissions = (
            ("accountgroup_view", _(u"Просмотр")),
        )


class Account(DynamicModel):
    """
    Если стоят галочки assign_vpn_ip_from_dhcp или assign_ipn_ip_from_dhcp,
    значит каждый раз при RADIUS запросе будет провереряться есть ли аренда и
    не истекла ли она.
    Если аренды нет или она истекла, то создаётся новая и пользователю
    назначается новый IP адрес.
    """
    username = models.CharField(
        verbose_name=_(u'Логин'), max_length=200, unique=True)
    password = EncryptedTextField(
        verbose_name=_(u'Пароль'), blank=True, default='')
    fullname = models.CharField(
        verbose_name=_(u'ФИО'), blank=True, default='', max_length=200)
    email = models.CharField(
        verbose_name=_(u'E-mail'), blank=True, default='', max_length=200)
    address = models.TextField(
        verbose_name=_(u'Адрес'), blank=True, default='')
    city = models.ForeignKey(
        'billservice.City',
        verbose_name=_(u'Город'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    postcode = models.CharField(
        verbose_name=_(u'Индекс'), max_length=255, blank=True, null=True)
    region = models.CharField(
        blank=True,
        verbose_name=_(u'Район'),
        max_length=255,
        default=''
    )
    street = models.CharField(
        max_length=255,
        verbose_name=_(u'Улица'),
        blank=True,
        null=True
    )
    house = models.CharField(
        max_length=255, verbose_name=_(u'Дом'), blank=True, null=True)
    house_bulk = models.CharField(
        verbose_name=_(u'Корпус'), blank=True, max_length=255)
    entrance = models.CharField(
        verbose_name=_(u'Подъезд'), blank=True, max_length=255)
    room = models.CharField(
        verbose_name=_(u'Квартира'), blank=True, max_length=255)
    status = models.IntegerField(
        verbose_name=_(u'Статус'),
        default=1,
        choices=(
            (1, _(u"Активен")),
            (2, _(u"Не активен, списывать периодические услуги")),
            (3, _(u"Не активен, не списывать периодические услуги")),
            (4, _(u"Пользовательская блокировка"))
        )
    )
    created = models.DateTimeField(
        verbose_name=_(u'Создан'),
        help_text=_(u'Начало оказания услуг'),
        default=''
    )
    # NOTE: baLance
    ballance = models.DecimalField(
        _(u'Баланс'), blank=True, default=0, decimal_places=2, max_digits=20)
    bonus_ballance = models.DecimalField(
        _(u'Бонусный баланс'), blank=True, default=0, decimal_places=2, max_digits=20)
    credit = models.DecimalField(
        verbose_name=_(u'Кредит'), decimal_places=2, max_digits=20, default=0)
    disabled_by_limit = models.BooleanField(
        blank=True, default=False, editable=False)
    balance_blocked = models.BooleanField(blank=True, default=False)
    allow_webcab = models.BooleanField(
        verbose_name=_(u"Разрешить пользоваться веб-кабинетом"),
        blank=True,
        default=True
    )
    allow_expresscards = models.BooleanField(
        verbose_name=_(u"Разрешить активацию карт экспресс-оплаты"),
        blank=True,
        default=True
    )
    passport = models.CharField(
        verbose_name=_(u'№ паспорта'), blank=True, max_length=64)
    passport_date = models.CharField(
        verbose_name=_(u'Выдан'), blank=True, max_length=64)
    passportdislocate = models.CharField(
        verbose_name=_(u'Адрес регистрации'), blank=True, max_length=1024)
    phone_h = models.CharField(
        validators=[validate_phone],
        verbose_name=_(u'Дом. телефон'),
        blank=True,
        max_length=64
    )
    phone_m = models.CharField(
        validators=[validate_phone],
        verbose_name=_(u'Моб. телефон'),
        help_text=_(u'В международном формате +71923453333'),
        blank=True,
        max_length=64
    )
    contactperson_phone = models.CharField(
        validators=[validate_phone],
        verbose_name=_(u'Тел. контактного лица'),
        blank=True,
        max_length=64
    )
    comment = models.TextField(blank=True)
    row = models.CharField(verbose_name=_(u'Этаж'), blank=True, max_length=6)
    elevator_direction = models.CharField(
        verbose_name=_(u'Направление от лифта'),
        blank=True,
        null=True,
        max_length=128
    )
    contactperson = models.CharField(
        verbose_name=_(u'Контактное лицо'), blank=True, max_length=256)
    passport_given = models.CharField(
        verbose_name=_(u'Кем выдан'), blank=True, null=True, max_length=128)
    contract = models.TextField(verbose_name=_(u'№ договора'), blank=True)
    systemuser = models.ForeignKey(
        'billservice.SystemUser',
        verbose_name=_(u'Менеджер'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    entrance_code = models.CharField(
        verbose_name=_(u'Код домофона'), blank=True, max_length=256)
    private_passport_number = models.CharField(
        verbose_name=_(u'Идент. номер'), blank=True, max_length=128)

    birthday = models.DateField(
        verbose_name=_(u'День рождения'), blank=True, null=True)

    deleted = models.DateTimeField(blank=True, null=True, db_index=True)
    promise_summ = models.IntegerField(
        _(u'Максимальный обещанный платёж'), blank=True, default=0)
    promise_min_ballance = models.IntegerField(
        _(u'Минимальный баланс для обещанного платежа'), blank=True, default=0)
    promise_days = models.IntegerField(
        _(u'Длительность обещанного платежа, дней'), blank=True, default=0)
    account_group = models.ForeignKey(
        'billservice.AccountGroup',
        verbose_name=_(u'Группа'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    disable_notifications = models.DateTimeField(
        verbose_name=_(u'Отключить SMS/Email уведомления'),
        blank=True,
        null=True
    )
    objects = SoftDeletedDateManager()

    @property
    def promise_sum_20(self):
        return (self.promise_summ
                if self.promise_summ > 0
                else settings.PROMISE_MAX_SUM)

    @property
    def promise_min_balance_20(self):
        return (self.promise_min_ballance
                if self.promise_min_ballance
                else settings.PROMISE_MIN_BALANCE)

    @property
    def promise_left_days_20(self):
        return self.promise_days or settings.PROMISE_LEFT_DAYS

    @property
    def allowed_transfer_sum_20(self):
        return 0 if self.ballance <= 0 else round(self.ballance, 2)

    @property
    def address_full(self):
        items = []
        if self.city:
            items.append(str(self.city))
        if self.street:
            items.append(ugettext(u'ул. {}'.format(self.street)))
        if self.house:
            items.append(ugettext(u'дом {}'.format(self.house)))
        if self.house_bulk:
            items.append(ugettext(u'корп. {}'.format(self.house_bulk)))
        if self.room:
            items.append(ugettext(u'кв. {}'.format(self.room)))
        return ', '.join(items)

    def get_actual_ballance(self):
        return self.ballance + self.credit

    def ballance_isnt_good(self):
        if self.ballance + self.credit <= 0:
            return True
        else:
            return False

    def delete(self):
        if not self.deleted:
            self.deleted = datetime.datetime.now()
            self.status = 3  # set suspendedperiod by trigger in db
            self.save()
            return
        super(Account, self).delete()

    def account_status(self):
        if self.status == 1:
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        try:
            user = User.objects.get(username=self.username)
        except:
            user = User()
            user.username = self.username
            user.set_password(self.password)
        user.is_staff = False
        user.is_active = self.deleted is not None
        user.first_name = self.fullname
        user.save()

        super(Account, self).save(*args, **kwargs)

    def get_last_promises_count(self):
        return (get_model('Transaction').objects
                .filter(account=self,
                        promise_expired=False,
                        type=get_model('TransactionType')
                        .objects.get(internal_name='PROMISE_PAYMENT'))
                .count())

    class Admin:
        ordering = ['user']

    def __unicode__(self):
        return '%s' % self.username

    def get_row_class(self):
        return STATUS_CLASS.get(self.status)

    class Meta:
        ordering = ['username']
        verbose_name = _(u"Аккаунт")
        verbose_name_plural = _(u"Аккаунты")
        permissions = (
            ("account_view", _(u"Просмотр")),
            ("get_tariff", _(u"Получить тариф для аккаунта")),
            ("cashier_view", _(u"Список аккаунтов для кассира"))
        )

    @property
    def ips(self):
        vpn_ips = []
        ipn_ips = []
        macs = []
        sas = SubAccount.objects.filter(account=self)
        for sa in sas:
            if sa.vpn_ip_address:
                vpn_ips.append(sa.vpn_ip_address)
            if sa.ipn_ip_address:
                ipn_ips.append(str(sa.ipn_ip_address))
            if sa.ipn_mac_address:
                macs.append(sa.ipn_mac_address)

        return '%s %s %s' % (', '.join(vpn_ips), ', '.join(ipn_ips), ', '.join(macs),)

    @models.permalink
    def change_password_url_ajax(self):
        return ('billservice.views.change_password', (), {})

    def is_authenticated(self):
        """Always return True. This is a way to tell if the user has
        been authenticated in templates.
        """
        return True

    def get_account_tariff(self):
        tariff = get_model('Tariff').objects.extra(
            where=['id=get_tarif(%s)'], params=[self.id])[:1]
        if tariff:
            return tariff[0]

    def get_accounttariff(self):
        accounttarif = (AccountTarif.objects
                        .filter(account=self,
                                datetime__lte=datetime.datetime.now())
                        .order_by("-datetime"))
        return accounttarif[0] if accounttarif else None

    def get_account_tariff_info(self):
        tariff_info = get_model('Tariff').objects.extra(
            where=['id=get_tarif(%s)'], params=[self.id])[:1]
        for tariff in tariff_info:
            return [tariff.id, tariff.name, ]
        return '', ''

    @property
    def tariff(self):
        try:
            name = get_model('Tariff').objects.extra(
                where=['id=get_tarif(%s)'], params=[self.id])[0].name
        except:
            name = _(u'Не назначен')
        return name

    def get_status(self):
        return dict(ACCOUNT_STATUS)[int(self.status)]

    def get_absolute_url(self):
        return "%s?id=%s" % (reverse('account_edit'), self.id)

    def get_addon_services(self):
        return (apps.get_model('billservice.AccountAddonService').objects
                .filter(account=self,
                        subaccount__isnull=True,
                        deactivated__isnull=True))


class AccountAddonService(models.Model):
    service = models.ForeignKey(
        'billservice.AddonService',
        null=True,
        verbose_name=_(u'Услуга'),
        on_delete=models.CASCADE
    )
    account = models.ForeignKey(
        'billservice.Account',
        verbose_name=_(u'Аккаунт'),
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    subaccount = models.ForeignKey(
        'billservice.SubAccount',
        verbose_name=_(u'Субаккаунт'),
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    cost = models.DecimalField(
        verbose_name=u'Стоимость',
        help_text=(u'Укажите, если хотите задать цену, отличную от указанной в '
                   u'услуге'),
        decimal_places=2,
        max_digits=15,
        blank=True,
        null=True
    )
    activated = models.DateTimeField(verbose_name=_(u'Активирована'))
    deactivated = models.DateTimeField(
        verbose_name=_(u'Отключена'), blank=True, null=True)
    action_status = models.BooleanField(default=False)
    speed_status = models.BooleanField(default=False)
    temporary_blocked = models.DateTimeField(
        verbose_name=_(u'Пауза до'), blank=True, null=True)
    last_checkout = models.DateTimeField(
        verbose_name=_(u'Последнее списание'), blank=True, null=True)

    def __unicode__(self):
        return u"%s" % (self.activated)

    class Meta:
        ordering = ['-activated', '-deactivated']
        verbose_name = _(u"Подключённая услуга")
        verbose_name_plural = _(u"Подключённые услуги")
        permissions = (
            ("accountaddonservice_view", _(u"Просмотр")),
        )

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accountaddonservice_delete'), self.id)

    def get_deactivate_url(self):
        return "%s?id=%s" % (reverse('accountaddonservice_deactivate'), self.id)


class AccountHardware(models.Model):
    account = models.ForeignKey(
        'billservice.Account', on_delete=models.CASCADE)
    hardware = models.ForeignKey(
        'billservice.Hardware',
        verbose_name=_(u"Устройство"),
        on_delete=models.CASCADE
    )
    datetime = models.DateTimeField(blank=True, verbose_name=_(u"Дата выдачи"))
    returned = models.DateTimeField(
        blank=True, verbose_name=_(u"Дата возврата"))
    comment = models.TextField(
        blank=True, default="", verbose_name=_(u"Комментарий"))

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accounthardware_delete'), self.id)

    def __unicode__(self):
        return u'%s-%s %s' % (self.id, self.account, self.hardware)

    class Meta:
        ordering = ['datetime']
        verbose_name = _(u"Устройство у абонента")
        verbose_name_plural = _(u"Устройства у абонентов")
        permissions = (
            ("accounthardware_view", _(u"Просмотр")),
        )


class AccountIPNSpeed(models.Model):
    """
    Класс описывает настройки скорости для пользователей с тарифными планами IPN
    После создания пользователя должна создваться запись в этой таблице
    """
    account = models.ForeignKey(
        to='billservice.Account', on_delete=models.CASCADE)
    speed = models.CharField(max_length=32, default='')
    state = models.BooleanField(blank=True, default=False)
    static = models.BooleanField(
        verbose_name=_(u"Статическая скорость"),
        help_text=_(u"Пока опция установлена, биллинг не будет менять для "
                    u"этого клиента скорость"),
        blank=True,
        default=False
    )
    datetime = models.DateTimeField(default='')

    def __unicode__(self):
        return u"%s %s" % (self.account, self.speed)

    class Admin:
        pass

    class Meta:
        verbose_name = _(u"Скорость IPN клиента")
        verbose_name_plural = _(u"Скорости IPN клиентов")


class AccountNotification(models.Model):
    account = models.ForeignKey(
        'billservice.Account', on_delete=models.CASCADE)
    notificationsettings = models.ForeignKey(
        'billservice.NotificationsSettings',
        on_delete=models.CASCADE
    )
    ballance_notification_count = models.IntegerField(blank=True, default=0)
    ballance_notification_last_date = models.DateTimeField(
        blank=True, null=True)
    payment_notification_last_date = models.DateTimeField(
        blank=True, null=True)


class AccountPrepaysRadiusTrafic(models.Model):
    """
    При подключении пользователю тарифного плана, у которого есть предоплаченный трафик
    в таблице должны создаваться записи
    В начале каждого расчётного периода пользователю должен заново начисляться трафик
    """
    account_tarif = models.ForeignKey(
        to='billservice.AccountTarif', on_delete=models.CASCADE)
    prepaid_traffic = models.ForeignKey(
        to='billservice.RadiusTraffic', null=True, on_delete=models.SET_NULL)
    size = models.FloatField(blank=True, default=0)
    direction = models.IntegerField()
    datetime = models.DateTimeField(auto_now_add=True)
    current = models.BooleanField(default=False)
    reseted = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s" % (self.prepaid_traffic)

    class Admin:
        pass

    def in_percents(self):
        a = self.size * 100 / self.prepaid_traffic.size
        return a

    class Meta:
        ordering = ['-datetime']
        verbose_name = _(u"Предоплаченый radius трафик ")
        verbose_name_plural = _(u"Предоплаченный radius трафик")
        permissions = (
            ("accountprepaysradiustraffic_view", _(u"Просмотр")),
        )


class AccountPrepaysTime(models.Model):
    account_tarif = models.ForeignKey(
        to='billservice.AccountTarif', on_delete=models.CASCADE)
    prepaid_time_service = models.ForeignKey(
        to='billservice.TimeAccessService', null=True, on_delete=models.SET_NULL)
    size = models.IntegerField(default=0, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    current = models.BooleanField(default=False)
    reseted = models.BooleanField(default=False)

    def in_percents(self):
        a = self.size * 100 / self.prepaid_time_service.prepaid_time
        return a

    class Admin:
        pass

    class Meta:
        ordering = ['-datetime']
        verbose_name = _(u"Предоплаченное время пользователя")
        verbose_name_plural = _(u"Предоплаченное время пользователей")
        permissions = (
            ("accountprepaystime_view", _(u"Просмотр")),
        )


class AccountPrepaysTrafic(models.Model):
    """
    При подключении пользователю тарифного плана, у которого есть предоплаченный трафик
    в таблице должны создаваться записи
    В начале каждого расчётного периода пользователю должен заново начисляться трафик
    """
    account_tarif = models.ForeignKey(
        to='billservice.AccountTarif', on_delete=models.CASCADE)
    prepaid_traffic = models.ForeignKey(
        to='billservice.PrepaidTraffic', null=True, on_delete=models.CASCADE)
    size = models.FloatField(blank=True, default=0, verbose_name=_(u'Остаток'))
    datetime = models.DateTimeField(
        auto_now_add=True, verbose_name=_(u'Начислен'))
    current = models.BooleanField(default=False, verbose_name=_(u'Текущий'))
    reseted = models.BooleanField(default=False, verbose_name=_(u'Сброшен'))

    def __unicode__(self):
        return u"%s" % (self.prepaid_traffic)

    class Admin:
        pass

    def in_percents(self):
        a = self.size * 100 / self.prepaid_traffic.size
        return a

    class Meta:
        ordering = ['-datetime']
        verbose_name = _(u"Предоплаченый трафик")
        verbose_name_plural = _(u"Предоплаченный трафик")
        permissions = (
            ("account_prepaystraffic_view", _(u"Просмотр")),
        )


class AccountSpeedLimit(models.Model):
    account = models.ForeignKey(
        'billservice.Account', on_delete=models.CASCADE)
    speedlimit = models.ForeignKey(
        'billservice.SpeedLimit', on_delete=models.CASCADE)


class AccountTarif(models.Model):
    account = models.ForeignKey(
        verbose_name=_(u'Пользователь'),
        to='billservice.Account',
        related_name='related_accounttarif',
        on_delete=models.CASCADE
    )
    prev_tarif = models.ForeignKey(
        to='billservice.Tariff',
        verbose_name=_(u'Предыдущий тарифный план'),
        blank=True,
        null=True,
        related_name="account_prev_tarif",
        on_delete=models.CASCADE
    )
    tarif = models.ForeignKey(
        to='billservice.Tariff',
        verbose_name=_(u'Тарифный план'),
        related_name="account_tarif",
        on_delete=models.CASCADE
    )
    datetime = models.DateTimeField(
        verbose_name=_(u'C даты'), default='', blank=True)
    periodical_billed = models.BooleanField(blank=True, default=False)

    class Admin:
        ordering = ['-datetime']
        list_display = ('account', 'tarif', 'datetime')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accounttariff_delete'), self.id)

    def __unicode__(self):
        return u"%s, %s" % (self.account, self.tarif)

    def save(self, *args, **kwargs):
        if not self.id:
            at = AccountTarif.objects.filter(
                account=self.account).order_by('-id')
            if at:
                print at[0]
                self.prev_tarif = at[0].tarif
        super(AccountTarif, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-datetime']
        verbose_name = _(u"Тариф аккаунта")
        verbose_name_plural = _(u"Тариф аккаунта")
        permissions = (
            ("accounttarif_view", _(u"Просмотр")),
        )


class BalanceHistory(models.Model):
    account = models.ForeignKey(
        'billservice.Account', verbose_name=_(u"Аккаунт"), on_delete=models.CASCADE)
    balance = models.DecimalField(
        max_digits=30, decimal_places=20, verbose_name=_(u"Баланс"))
    summ = models.DecimalField(
        max_digits=30, default=0, decimal_places=6, verbose_name=_(u"Сумма"))
    datetime = models.DateTimeField()

    class Meta:
        ordering = ['-datetime']
        verbose_name = _(u"История изменения баланса")
        verbose_name_plural = _(u"История изменения баланса")
        permissions = (
            ("balancehistory_view", _(u"Просмотр")),
        )


class SubAccount(models.Model):
    account = models.ForeignKey(
        'billservice.Account', related_name='subaccounts')
    username = models.CharField(
        verbose_name=_(u'Логин'), max_length=512, blank=True)
    password = EncryptedTextField(
        verbose_name=_(u'Пароль'), blank=True, default='')
    ipn_ip_address = IPNetworkField(blank=True, null=True, default='0.0.0.0')
    ipn_mac_address = models.CharField(blank=True, max_length=17, default='')
    vpn_ip_address = IPAddressField(
        blank=True, null=True, default='0.0.0.0')
    allow_mac_update = models.BooleanField(default=False)
    nas = models.ForeignKey(
        Nas, blank=True, null=True, on_delete=models.SET_NULL)
    ipn_added = models.BooleanField(
        verbose_name=_(u'Добавлен на NAS'), blank=True, default=False)
    ipn_enabled = models.BooleanField(
        verbose_name=_(u'Включен на NAS'), blank=True, default=False)
    ipn_sleep = models.BooleanField(
        verbose_name=_(u'Не менять IPN статус'), blank=True, default=False)
    ipn_queued = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_(u'Поставлен в очередь на изменение статуса')
    )
    need_resync = models.BooleanField(default=False)
    speed = models.TextField(blank=True)
    switch = models.ForeignKey(
        'billservice.Switch', blank=True, null=True, on_delete=models.SET_NULL)
    switch_port = models.IntegerField(blank=True, null=True)
    allow_dhcp = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разрешать получать IP адреса по DHCP")
    )
    allow_dhcp_with_null = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разрешать получать IP адреса по DHCP при нулевом "
                       u"балансе")
    )
    allow_dhcp_with_minus = models.BooleanField(
        blank=True,
        default=False,
        # TODO: fix typo
        verbose_name=_(u"Разрешать получать IP адреса по DHCP при "
                       u"отрицатеьлном балансе")
    )
    allow_dhcp_with_block = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разрешать получать IP адреса по DHCP при наличии "
                       u"блокировок по лимитам или балансу")
    )
    allow_vpn_with_null = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разрешать RADIUS авторизацию при нулевом балансе")
    )
    allow_vpn_with_minus = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разрешать RADIUS авторизацию при отрицательном "
                       u"балансе"))
    allow_vpn_with_block = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разрешать RADIUS авторизацию при наличии блокировок "
                       u"по лимитам или балансу"))
    allow_ipn_with_null = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разрешать IPN авторизацию при нулевом балансе")
    )
    allow_ipn_with_minus = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разрешать IPN авторизацию при отрицательном балансе")
    )
    allow_ipn_with_block = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разрешать IPN авторизацию при наличии блокировок "
                       u"по лимитам или балансу")
    )
    associate_pptp_ipn_ip = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Привязать PPTP/L2TP авторизацию к IPN IP")
    )
    associate_pppoe_ipn_mac = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Привязать PPPOE авторизацию к IPN MAC")
    )

    ipn_speed = models.TextField(
        blank=True, help_text=_(u"Не менять указанные настройки скорости"))
    vpn_speed = models.TextField(
        blank=True, help_text=_(u"Не менять указанные настройки скорости"))
    allow_addonservice = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разрешить самостоятельную активацию подключаемых "
                       u"услуг на этот субаккаунт")
    )
    vpn_ipinuse = models.ForeignKey(
        'billservice.IPInUse',
        blank=True,
        null=True,
        related_name='subaccount_vpn_ipinuse_set',
        on_delete=models.SET_NULL
    )
    ipn_ipinuse = models.ForeignKey(
        'billservice.IPInUse',
        blank=True,
        null=True,
        related_name='subaccount_ipn_ipinuse_set',
        on_delete=models.SET_NULL
    )
    vpn_ipv6_ip_address = IPAddressField(blank=True, null=True)
    vpn_ipv6_ipinuse = models.ForeignKey(
        'billservice.IPInUse',
        blank=True,
        null=True,
        related_name='subaccount_vpn_ipv6_ipinuse_set',
        on_delete=models.SET_NULL
    )
    vlan = models.IntegerField(blank=True, null=True)
    allow_mac_update = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_(u"Разрешить самостоятельно обновлять MAC адрес "
                       u"через веб-кабинет")
    )
    ipv4_ipn_pool = models.ForeignKey(
        'billservice.IPPool',
        blank=True,
        default=None,
        null=True,
        related_name='subaccount_ipn_ippool_set',
        on_delete=models.SET_NULL
    )
    ipv4_vpn_pool = models.ForeignKey(
        'billservice.IPPool',
        blank=True,
        default=None,
        null=True,
        related_name='subaccount_vpn_ippool_set',
        on_delete=models.SET_NULL
    )
    ipv6_vpn_pool = models.ForeignKey(
        'billservice.IPPool',
        blank=True,
        default=None,
        null=True,
        related_name='subaccount_ipv6_vpn_ippool_set',
        on_delete=models.SET_NULL
    )
    sessionscount = models.IntegerField(
        verbose_name=_(u"Одноверменных RADIUS сессий на субаккаунт"),
        blank=True,
        default=0
    )

    speed_units = models.CharField(
        default='Kbps',
        verbose_name=_(u'Единицы измерения скорости'),
        max_length=32,
        choices=(
            ('Kbps', 'Kbps'),
            ('Mbps', 'Mbps')
        ),
        blank=True,
        null=True
    )
    priority = models.IntegerField(
        verbose_name=_(u'Приоритет'), default=8)
    max_tx = models.IntegerField(
        verbose_name=_(u'Max Tx'), default=0)
    max_rx = models.IntegerField(
        verbose_name=_(u'Max Rx'), default=0)
    burst_tx = models.IntegerField(
        verbose_name=_(u'Burst Tx'), default=0)
    burst_rx = models.IntegerField(
        verbose_name=_(u'Burst Rx'), default=0)
    burst_treshold_tx = models.IntegerField(
        verbose_name=_(u'Burst treshold Tx'), default=0)
    burst_treshold_rx = models.IntegerField(
        verbose_name=_(u'Burst treshold Rx'), default=0)
    burst_time_tx = models.IntegerField(
        verbose_name=_(u'Burst time Tx (s)'), default=0)
    burst_time_rx = models.IntegerField(
        verbose_name=_(u'Burst time Rx (s)'), default=0)
    min_tx = models.IntegerField(
        verbose_name=_(u'Min Tx'), default=0)
    min_rx = models.IntegerField(
        verbose_name=_(u'Min Rx'), default=0)

    def __unicode__(self):
        return u"%s" % self.username

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('subaccount_delete'), self.id)

    class Meta:
        ordering = ['-username']
        verbose_name = _(u"Субаккаунт")
        verbose_name_plural = _(u"Субаккаунт")
        permissions = (
            ("subaccount_view", _(u"Просмотр")),
            ("getmacforip", _(u"Получение mac адреса по IP")),
        )

    def save(self, *args, **kwargs):
        if self.vpn_ipinuse:

            if str(self.vpn_ip_address) not in \
                    ['0.0.0.0', '0.0.0.0/32', '', None]:

                if self.ipv4_vpn_pool:

                    if str(self.vpn_ipinuse.ip) != str(self.vpn_ip_address):
                        obj = get_model('IPInUse').objects.get(
                            id=self.vpn_ipinuse.id)
                        obj.disabled = datetime.datetime.now()
                        obj.save()

                        obj = get_model('IPInUse')(pool=self.ipv4_vpn_pool,
                                                   ip=self.vpn_ip_address,
                                                   datetime=datetime.datetime.now())
                        obj.save()
                        self.vpn_ipinuse = obj

                else:
                    obj = self.vpn_ipinuse
                    obj.disabled = datetime.datetime.now()
                    obj.save()
                    self.vpn_ipinuse = None

            elif str(self.vpn_ip_address) in \
                    ['', '0.0.0.0', '0.0.0.0/32', '', None]:
                obj = self.vpn_ipinuse
                obj.disabled = datetime.datetime.now()
                obj.save()

                self.vpn_ipinuse = None

        elif str(self.vpn_ip_address) not in \
                ['', '0.0.0.0', '0.0.0.0/32', '', None] and self.ipv4_vpn_pool:
            ip = get_model('IPInUse')(pool=self.ipv4_vpn_pool,
                                      ip=self.vpn_ip_address,
                                      datetime=datetime.datetime.now())
            ip.save()
            self.vpn_ipinuse = ip

        if self.vpn_ipv6_ipinuse:

            if str(self.vpn_ipv6_ip_address) not in ['', '::', ':::', None]:

                if self.ipv6_vpn_pool:

                    if str(self.vpn_ipv6_ipinuse.ip) != \
                            str(self.vpn_ipv6_ip_address):
                        obj = get_model('IPInUse').objects.get(
                            id=self.vpn_ipv6_ipinuse.id)
                        obj.disabled = datetime.datetime.now()
                        obj.save()

                        obj = get_model('IPInUse').objects.create(
                            pool=self.ipv6_vpn_pool,
                            ip=self.vpn_ipv6_ip_address,
                            datetime=datetime.datetime.now())
                        obj.save()
                        self.vpn_ipv6_ipinuse = obj
                else:
                    obj = self.vpn_ipv6_ipinuse
                    obj.disabled = datetime.datetime.now()
                    obj.save()
                    self.vpn_ipv6_ipinuse = None

            elif str(self.vpn_ipv6_ip_address) in ['', '::', ':::', None]:

                obj = self.vpn_ipv6_ipinuse
                obj.disabled = datetime.datetime.now()
                obj.save()

                self.vpn_ipv6_ipinuse = None

        elif str(self.vpn_ipv6_ip_address) not in ['', '::', ':::', None] and \
                self.ipv6_vpn_pool:

            ip = get_model('IPInUse')(pool=self.ipv6_vpn_pool,
                                      ip=self.vpn_ipv6_ip_address,
                                      datetime=datetime.datetime.now())
            ip.save()

            self.vpn_ipv6_ipinuse = ip

        if self.ipn_ipinuse:

            if str(self.ipn_ip_address) not in ['0.0.0.0', '0.0.0.0/32', '', None]:

                if self.ipv4_ipn_pool:

                    if str(self.ipn_ipinuse.ip) != str(self.ipn_ip_address):
                        obj = get_model('IPInUse').objects.get(
                            id=self.ipn_ipinuse.id)
                        obj.disabled = datetime.datetime.now()
                        obj.save()

                        obj = get_model('IPInUse')(
                            pool=self.ipv4_ipn_pool,
                            ip=self.ipn_ip_address,
                            datetime=datetime.datetime.now()
                        )
                        obj.save()
                        self.ipn_ipinuse = obj
                else:
                    obj = self.ipn_ipinuse
                    obj.disabled = datetime.datetime.now()
                    obj.save()
                    self.ipn_ipinuse = None

            elif str(self.ipn_ip_address) in \
                    ['', '0.0.0.0', '0.0.0.0/32', '', None]:

                obj = get_model('IPInUse').objects.get(id=self.ipn_ipinuse.id)
                obj.disabled = datetime.datetime.now()
                obj.save()
                self.ipn_ipinuse = None

        elif str(self.ipn_ip_address) not in \
                ['', '0.0.0.0', '0.0.0.0/32', '', None] and self.ipv4_ipn_pool:

            ip = get_model('IPInUse')(pool=self.ipv4_ipn_pool,
                                      ip=self.ipn_ip_address,
                                      datetime=datetime.datetime.now())
            ip.save()
            self.ipn_ipinuse = ip

        self.ipn_ip_address = self.ipn_ip_address or '0.0.0.0'
        self.vpn_ip_address = self.vpn_ip_address or '0.0.0.0'

        super(SubAccount, self).save(*args, **kwargs)


class City(models.Model):
    name = models.CharField(max_length=320)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Город")
        verbose_name_plural = _(u"Города")
        permissions = (
            ("city_view", _(u"Просмотр")),
        )


class Street(models.Model):
    name = models.CharField(max_length=320)
    city = models.ForeignKey('billservice.City', on_delete=models.CASCADE)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Улица")
        verbose_name_plural = _(u"Улицы")
        permissions = (
            ("street_view", _(u"Просмотр")),
        )


class House(models.Model):
    name = models.CharField(max_length=320)
    street = models.ForeignKey('billservice.Street', on_delete=models.CASCADE)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Дом")
        verbose_name_plural = _(u"Дома")
        permissions = (
            ("house_view", _(u"Просмотр")),
        )
