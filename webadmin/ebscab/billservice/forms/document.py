# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from billservice.models import Card, Document


class DocumentModelForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = '__all__'


class DocumentRenderForm(forms.Form):
    account = forms.IntegerField(required=False)
    transaction = forms.IntegerField(required=False)
    template = forms.IntegerField(label=_(u'Шаблон'), required=True)
    cards = forms.ModelMultipleChoiceField(
        queryset=Card.objects.all(), required=False)
