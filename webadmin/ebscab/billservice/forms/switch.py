# -*- encoding: utf-8 -*-

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, HTML, Layout, Submit
from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from billservice.models import Switch


class SwitchForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-SwitchForm'
        self.helper.form_class = 'well form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse("switch_edit")
        self.helper.layout = Layout(
            Fieldset(
                _(u'Общее'),
                'id',
                'name',
                'comment',

            ),
            Fieldset(
                _(u'Данные техпаспорта'),
                'manufacturer',
                'model',
                'sn',
            ),
            Fieldset(
                _(u'Место установки'),
                'city',
                'street',
                'house',
                'place'
            ),
            Fieldset(
                _(u'SNMP'),
                'snmp_support',
                'snmp_version',
                'snmp_community',
            ),
            Fieldset(
                _(u'Управление портами'),
                HTML(_(u'Обратите внимание, что в текущей версии управление '
                       u'портами не реализовано')),
                'management_method',
                'username',
                'password',
                'enable_port',
                'disable_port',
            ),
            Fieldset(
                _(u'Сетевая идентификация'),
                'ports_count',
                'ipaddress',
                'macaddress',
            ),
            Fieldset(
                _(u'Option82'),
                'option82',
                'option82_auth_type',
                'option82_template',
                'identify',
                'secret',
                'remote_id'
            ),
            FormActions(
                Submit('save', _(u'Сохранить'), css_class="btn-primary")
            )

        )

        super(SwitchForm, self).__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs['class'] = 'input-xlarge span6'
        self.fields['comment'].widget.attrs['rows'] = 3
        self.fields['place'].widget.attrs['class'] = 'input-xlarge span6'
        self.fields['place'].widget.attrs['rows'] = 3
        self.fields['enable_port'].widget.attrs['class'] = 'input-xlarge span6'
        self.fields['enable_port'].widget.attrs['rows'] = 3

        self.fields['disable_port'].widget.attrs[
            'class'] = 'input-xlarge span6'
        self.fields['disable_port'].widget.attrs['rows'] = 3

    class Meta:
        model = Switch
        exclude = (
            'broken_ports',
            'disabled_ports',
            'monitored_ports',
            'protected_ports',
            'uplink_ports'
        )
