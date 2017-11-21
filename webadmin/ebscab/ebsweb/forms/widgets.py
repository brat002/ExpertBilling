# -*- coding: utf-8 -*-

from django.forms import widgets


class DefaultClassMixin(object):
    default_class = None

    def __init__(self, *args, **kwargs):
        if self.default_class is not None:
            attrs = kwargs.get('attrs', {})
            class_ = attrs.get('class')
            if class_:
                merged_class = ' '.join(
                    set(class_.split() + self.default_class.split()))
            else:
                merged_class = self.default_class
            attrs['class'] = merged_class
            kwargs['attrs'] = attrs
        super(DefaultClassMixin, self).__init__(*args, **kwargs)


class TextInput(DefaultClassMixin, widgets.TextInput):
    default_class = 'form-control m-input'


class PasswordInput(DefaultClassMixin, widgets.PasswordInput):
    default_class = 'form-control m-input'


class EmailInput(DefaultClassMixin, widgets.EmailInput):
    default_class = 'form-control m-input'


class NumberInput(DefaultClassMixin, widgets.NumberInput):
    default_class = 'form-control m-input'


class Select(DefaultClassMixin, widgets.Select):
    default_class = 'form-control m-input'


class RadioSelect(DefaultClassMixin, widgets.RadioSelect):
    default_class = 'm-radio'
    template_name = 'ebsweb/forms/widgets/radio.html'
    option_template_name = 'ebsweb/forms/widgets/radio_option.html'


class Textarea(DefaultClassMixin, widgets.Textarea):
    default_class = 'form-control m-input'


class RadioSelectWithDetail(widgets.RadioSelect):
    option_template_name = 'ebsweb/forms/widgets/radio_option_with_detail.html'

    class Media:
        js = ('ebsweb/widgets/forms/tariff_select.js',)

    # TODO: not replace 'label', pass 'detail' and 'label'
    def create_option(self, *args, **kwargs):
        option = super(RadioSelectWithDetail, self).create_option(
            *args, **kwargs)
        label = args[2]
        if isinstance(label, dict):
            detail = label
        else:
            detail = {
                'label': label
            }
        del option['label']
        option['detail'] = detail
        return option


class TariffSelect(RadioSelectWithDetail):
    template_name = 'ebsweb/forms/widgets/tariff_select.html'
    option_template_name = 'ebsweb/forms/widgets/tariff_select_option.html'
