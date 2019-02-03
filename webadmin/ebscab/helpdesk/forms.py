# -*- coding: utf-8 -*-

from datetime import datetime

from autocomplete_light import shortcuts as autocomplete_light
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, Button, Field, Fieldset
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db.models import Q

from billservice.models import SystemUser, Account

from helpdesk.models import (
    Attachment,
    FollowUp,
    IgnoreEmail,
    PreSetReply,
    Queue,
    SavedSearch,
    Ticket,
    TicketCC
)
from helpdesk.settings import HAS_TAG_SUPPORT
from helpdesk.utils import send_templated_mail


class TicketTypeForm(forms.Form):
    queuetype = forms.ModelChoiceField(
        label=_('Queue'), queryset=Queue.objects.all())


class AssignToForm(forms.Form):
    systemuser = forms.ModelChoiceField(
        label=_('User'), queryset=SystemUser.objects.all())
    ticket = forms.ModelChoiceField(
        label=_('Ticket'),
        queryset=Ticket.objects.all(),
        widget=forms.widgets.HiddenInput
    )


class EditTicketForm(forms.ModelForm):

    id = forms.IntegerField(required=False, widget=forms.widgets.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-ticket_edit_form'
        self.helper.form_class = 'well form-horizontal ajax form-condensed'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                _(u'Редактировать заявку'),
                'id',
                'queue',
                'priority',
                'source',
                'status',
                'title',
                'owner',
                'notify_owner',
                'account',
                'assigned_to',
                'on_hold',
                'due_date',
                'submitter_email',
                'description',
                'hidden_comment',
                'created',
                'modified'

            ),

        )
        super(EditTicketForm, self).__init__(*args, **kwargs)

        self.fields['owner'] = forms.ModelChoiceField(
            queryset=User.objects.all(),
            required=False,
            label=_(u'Создал'),
            widget=autocomplete_light.ChoiceWidget('UserAutocomplete')
        )

        self.fields['account'] = forms.ModelChoiceField(
            queryset=Account.objects.all(),
            required=False,
            label=_(u'Аккаунт'),
            widget=autocomplete_light.ChoiceWidget(
                'AccountAutocomplete',
                attrs={
                    'class': 'span6 input-xlarge'
                }
            )
        )

        self.fields['due_date'].widget = forms.widgets.DateTimeInput(
            attrs={
                'class': 'datepicker'
            }
        )

        self.fields['description'].widget = forms.widgets.Textarea(
            attrs={
                'rows': 8,
                'class': 'input-large span9'
            }
        )
        self.fields['hidden_comment'].widget = forms.widgets.Textarea(
            attrs={
                'rows': 5,
                'class': 'input-large span9'
            }
        )

    class Meta:
        model = Ticket
        exclude = ('created', 'modified', 'status', 'on_hold', 'resolution',
                   'last_escalation')


class TicketForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-ticket_edit_form'
        self.helper.form_class = 'well form-horizontal ajax form-condensed'
        self.helper.form_method = 'post'
        self.helper.form_tag = False

        super(TicketForm, self).__init__(*args, **kwargs)

    queue = forms.ModelChoiceField(
        label=_('Queue'),
        required=True,
        queryset=Queue.objects.all()
    )

    title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(),
        label=_('Summary of the problem'),
    )

    owner = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_(u'Создал'),
        widget=autocomplete_light.ChoiceWidget('UserAutocomplete')
    )

    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=False,
        label=_(u'Аккаунт'),
        widget=autocomplete_light.ChoiceWidget(
            'AccountAutocomplete', attrs={'class': 'span6 input'})
    )

    assigned_to = forms.ModelChoiceField(
        required=False,
        queryset=SystemUser.objects.all(),
        widget=autocomplete_light.ChoiceWidget('SystemUserAutocomplete'),
        label=_(u'Исполнитель'),
    )

    due_date = forms.DateTimeField(
        label=_(u'Due Date'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    priority = forms.ChoiceField(
        choices=Ticket.PRIORITY_CHOICES,
        required=False,
        initial='3',
        label=_('Priority'),
        help_text=_('Please select a priority carefully. If unsure, leave it '
                    'as \'3\'.')
    )

    submitter_email = forms.EmailField(
        required=False,
        label=_('Submitter E-Mail Address'),
        help_text=_('This e-mail address will receive copies of all public '
                    'updates to this ticket.'),
    )

    body = forms.CharField(
        widget=forms.widgets.Textarea(attrs={
            'rows': 5,
            'class': 'input-large span9'
        }),
        label=_('Description of Issue'),
        required=True
    )

    hidden_comment = forms.CharField(
        label=_('Hidden comment'),
        required=False,
        widget=forms.widgets.Textarea(attrs={
            'rows': 3,
            'class': 'input-large span9'
        })
    )

    attachment = forms.FileField(
        required=False,
        label=_('Attach File'),
        help_text=_('You can attach a file such as a document or screenshot '
                    'to this ticket.')
    )

    if HAS_TAG_SUPPORT:
        tags = forms.CharField(
            max_length=255,
            required=False,
            widget=forms.TextInput(),
            label=_('Tags'),
            help_text=_('Words, separated by spaces, or phrases separated '
                        'by commas. These should communicate significant '
                        'characteristics of this ticket')
        )

    def save(self, user):
        """
        Writes and returns a Ticket() object
        """

        q = self.cleaned_data['queue']

        t = Ticket(
            title=self.cleaned_data['title'],
            submitter_email=self.cleaned_data['submitter_email'],
            account=self.cleaned_data['account'],
            created=datetime.now(),
            status=Ticket.OPEN_STATUS,
            queue=q,
            description=self.cleaned_data['body'],
            priority=self.cleaned_data['priority'],
            owner=self.cleaned_data['owner']
        )

        if HAS_TAG_SUPPORT:
            t.tags = self.cleaned_data['tags']

        if self.cleaned_data['assigned_to']:
            try:
                t.assigned_to = self.cleaned_data['assigned_to']
            except User.DoesNotExist:
                t.assigned_to = None
        t.save()

        f = FollowUp(
            ticket=t,
            title=_('Ticket Opened'),
            date=datetime.now(),
            public=False,
            comment=self.cleaned_data['body'],
            systemuser=user.account,
        )
        if self.cleaned_data['assigned_to']:
            f.title = _('Ticket Opened & Assigned to %(name)s') % {
                'name': t.get_assigned_to
            }

        f.save()

        files = []
        if self.cleaned_data['attachment']:
            import mimetypes
            file = self.cleaned_data['attachment']
            filename = file.name.replace(' ', '_')
            a = Attachment(
                followup=f,
                filename=filename,
                mime_type=(mimetypes.guess_type(filename)[0] or
                           'application/octet-stream'),
                size=file.size,
            )
            a.file.save(file.name, file, save=False)
            a.save()

            if file.size < getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
                # Only files smaller than 512kb (or as defined in
                # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
                files.append(a.file.path)

        context = {
            'ticket': t,
            'queue': q,
            'comment': f.comment,
        }

        messages_sent_to = []

        if t.submitter_email:
            send_templated_mail(
                'newticket_owner',
                context,
                recipients=t.submitter_email,
                sender=q.from_address,
                fail_silently=True,
                files=files,
            )
            messages_sent_to.append(t.submitter_email)

        if q.new_ticket_cc and q.new_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=q.new_ticket_cc,
                sender=q.from_address,
                fail_silently=True,
                files=files,
            )
            messages_sent_to.append(q.new_ticket_cc)

        if q.updated_ticket_cc and q.updated_ticket_cc != q.new_ticket_cc and \
                q.updated_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=q.updated_ticket_cc,
                sender=q.from_address,
                fail_silently=True,
                files=files,
            )

        return t


class PublicTicketForm(forms.Form):
    queue = forms.ChoiceField(
        label=_('Queue'),
        required=True,
        choices=()
    )

    title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(),
        label=_('Summary of your query')
    )

    submitter_email = forms.EmailField(
        required=False,
        label=_('Your E-Mail Address'),
        help_text=_('We will e-mail you when your ticket is updated.')
    )

    body = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 100}),
        label=_('Description of your issue'),
        required=True,
        help_text=_('Please be as descriptive as possible, including any '
                    'details we may need to address your query.')
    )

    priority = forms.ChoiceField(
        choices=Ticket.PRIORITY_CHOICES,
        required=True,
        initial='3',
        label=_('Urgency'),
        help_text=_('Please select a priority carefully.'),
    )

    attachment = forms.FileField(
        required=False,
        label=_('Attach File'),
        help_text=_('You can attach a file such as a document or screenshot '
                    'to this ticket.')
    )

    def save(self, owner=None):
        """
        Writes and returns a Ticket() object
        """

        q = Queue.objects.get(id=int(self.cleaned_data['queue']))

        t = Ticket(
            title=self.cleaned_data['title'],
            owner=owner,
            submitter_email=self.cleaned_data['submitter_email'],
            created=datetime.now(),
            status=Ticket.OPEN_STATUS,
            queue=q,
            description=self.cleaned_data['body'],
            priority=self.cleaned_data['priority'],
            account=owner.account
        )

        t.save()

        f = FollowUp(
            ticket=t,
            title=_('Ticket Opened Via Web'),
            date=datetime.now(),
            public=True,
            comment=self.cleaned_data['body'],
            account=owner.account
        )

        f.save()

        files = []
        if self.cleaned_data['attachment']:
            import mimetypes
            file = self.cleaned_data['attachment']
            filename = file.name.replace(' ', '_')
            a = Attachment(
                followup=f,
                filename=filename,
                mime_type=mimetypes.guess_type(
                    filename)[0] or 'application/octet-stream',
                size=file.size,
            )
            a.file.save(file.name, file, save=False)
            a.save()

            if file.size < \
                    getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
                # Only files smaller than 512kb (or as defined in
                # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
                files.append(a.file.path)

        context = {
            'ticket': t,
            'queue': q,
        }

        messages_sent_to = []

        send_templated_mail(
            'newticket_owner',
            context,
            recipients=t.submitter_email,
            sender=q.from_address,
            fail_silently=True,
            files=files
        )
        messages_sent_to.append(t.submitter_email)

        if q.new_ticket_cc and q.new_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=q.new_ticket_cc,
                sender=q.from_address,
                fail_silently=True,
                files=files
            )
            messages_sent_to.append(q.new_ticket_cc)

        if q.updated_ticket_cc and q.updated_ticket_cc != q.new_ticket_cc and \
                q.updated_ticket_cc not in messages_sent_to:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=q.updated_ticket_cc,
                sender=q.from_address,
                fail_silently=True,
                files=files
            )

        return t


class UserSettingsForm(forms.Form):
    login_view_ticketlist = forms.BooleanField(
        label=_('Show Ticket List on Login?'),
        help_text=_('Display the ticket list upon login? Otherwise, the '
                    'dashboard is shown.'),
        required=False
    )

    email_on_ticket_change = forms.BooleanField(
        label=_('E-mail me on ticket change?'),
        help_text=_('If you\'re the ticket owner and the ticket is changed '
                    'via the web by somebody else, do you want to receive '
                    'an e-mail?'),
        required=False
    )

    email_on_ticket_assign = forms.BooleanField(
        label=_('E-mail me when assigned a ticket?'),
        help_text=_('If you are assigned a ticket via the web, do you want '
                    'to receive an e-mail?'),
        required=False
    )

    email_on_ticket_apichange = forms.BooleanField(
        label=_('E-mail me when a ticket is changed via the API?'),
        help_text=_('If a ticket is altered by the API, do you want to '
                    'receive an e-mail?'),
        required=False
    )

    tickets_per_page = forms.IntegerField(
        label=_('Number of tickets to show per page'),
        help_text=_('How many tickets do you want to see on the Ticket '
                    'List page?'),
        required=False,
        min_value=1,
        max_value=1000
    )

    use_email_as_submitter = forms.BooleanField(
        label=_('Use my e-mail address when submitting tickets?'),
        help_text=_('When you submit a ticket, do you want to automatically '
                    'use your e-mail address as the submitter address? You '
                    'can type a different e-mail address when entering the '
                    'ticket if needed, this option only changes the default.'),
        required=False
    )


class EmailIgnoreForm(forms.ModelForm):

    class Meta:
        model = IgnoreEmail
        fields = '__all__'


class TicketCCForm(forms.ModelForm):

    class Meta:
        model = TicketCC
        exclude = ('ticket',)


class FollowUpForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.widgets.HiddenInput)
    preset_reply = forms.ModelChoiceField(
        queryset=PreSetReply.objects.all(),
        label=_("Use a Pre-set Reply"),
        required=False
    )
    followup_type = forms.ChoiceField(
        choices=(
            ('comment', 'Comment'),
            ('files', 'Add Files'),
            ('new_status', 'New status')
        ),
        widget=forms.widgets.HiddenInput
    )
    file = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-followup_form'
        self.helper.form_class = 'well form-horizontal ajax form-condensed'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.form_action = reverse("followup_edit")
        ft = kwargs.get('initial', {}).get('followup_type')
        if not ft or ft == 'comment':
            fs = Fieldset(
                '',
                'id',
                'followup_type',
                'ticket',
                Field('preset_reply', css_class='input-large span6'),
                'comment',
                'public'
            )
        elif ft == 'files':
            fs = Fieldset(
                '',
                'id',
                'followup_type',
                'ticket',
                'comment',
                'file',
                'public'
            )
        elif ft == 'new_status':
            fs = Fieldset(
                '',
                'id',
                'followup_type',
                'ticket',
                Field('new_status', css_class='input-large span6'),
                Field('preset_reply', css_class='input-large span6'),
                'comment'
            )
        self.helper.layout = Layout(
            fs,
            FormActions(
                Submit('save', _(u'Add'), css_class="btn-primary"),
                Button('close',
                       _(u'Close'),
                       css_class="btn-inverse close-dialog")
            )
        )
        super(FollowUpForm, self).__init__(*args, **kwargs)

        self.fields['ticket'].widget = forms.widgets.HiddenInput()
        self.fields['comment'].widget = forms.widgets.Textarea(attrs={
            'rows': 5,
            'class': 'input-large span6'
        })

        if not ft or ft == 'comment':
            self.fields['file'].widget = forms.widgets.HiddenInput()
            self.fields['new_status'].widget = forms.widgets.HiddenInput()
        elif ft == 'files':
            self.fields['preset_reply'].widget = forms.widgets.HiddenInput()
            self.fields['new_status'].widget = forms.widgets.HiddenInput()
        elif ft == 'new_status':
            self.fields['file'].widget = forms.widgets.HiddenInput()

    class Meta:
        model = FollowUp
        exclude = ('date', 'user', 'title', 'systemuser', 'account')


class FilterForm(forms.Form):

    date_start = forms.DateTimeField(
        label=_(u'Создана с'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    date_end = forms.DateTimeField(
        label=_(u'Создана по'),
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={
            'class': 'datepicker'
        })
    )
    queue = forms.ModelMultipleChoiceField(
        queryset=Queue.objects.all(), required=False)
    status = forms.MultipleChoiceField(
        choices=Ticket.STATUS_CHOICES_FORM,
        required=False,
        label=_(u'Статус')
    )
    priority = forms.ChoiceField(
        choices=Ticket.PRIORITY_CHOICES_FORM,
        required=False,
        label=_(u'Приоритет')
    )

    owner = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label=_(u'Подал заявку'),
        widget=autocomplete_light.ChoiceWidget(
            'UserAutocomplete',
            attrs={
                'class': 'span6 input'
            }
        )
    )

    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=False,
        label=_(u'Аккаунт'),
        widget=autocomplete_light.ChoiceWidget(
            'AccountAutocomplete',
            attrs={
                'class': 'span6 input'
            }
        )
    )
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=SystemUser.objects.all(), required=False)
    keywords = forms.CharField(
        label=_(u'Фраза'),
        help_text=_(u'Поиск по тексту заголовков и заявок'),
        required=False
    )
    filter_name = forms.CharField(label=_(u'Имя фильтра'), required=False)
    share_filter = forms.BooleanField(
        label=_(u'Расшарить фильтр'), required=False)
    saved_query = forms.ModelChoiceField(
        label=_(u'Сохранённые фильтры'),
        required=False,
        queryset=SavedSearch.objects.filter(Q(shared=True))
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-followup_form'
        self.helper.form_class = 'well form-horizontal ajax form-condensed'
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.form_action = reverse("followup_edit")
        ft = kwargs.get('initial', {}).get('followup_type')

        self.helper.layout = Layout(
            Fieldset(
                _(u'Параметры поиска'),
                'date_start',
                'date_end',
                'queue',
                'status',
                'priority',
                'owner',
                'account',
                'assigned_to',
                Field('keywords', css_class='input-large span6')
            ),

            Div(
                Submit('search',
                       _(u'Найти заявки'),
                       css_class="btn-primary btn-large "),
                css_class='form-actions-center'),

            Fieldset(
                _(u'Сохранить запрос'),
                'filter_name',
                'share_filter',
                Div(Submit('save',
                           _(u'Сохранить и выполнить фильтр'),
                           css_class="btn-primary btn-large "),
                    css_class='form-actions-center'),


            ),
            Fieldset(
                _(u'Использовать сохранённый запрос'),
                'saved_query',
                Div(Submit('run', _(u'Выполнить'),
                           css_class="btn-primary btn-large "),
                    css_class='form-actions-center'),
            ),
        )
        super(FilterForm, self).__init__(*args, **kwargs)


class RunSubmitQuery(forms.Form):
    saved_query = forms.ModelChoiceField(
        label=_(u'Сохранённые фильтры'),
        required=False,
        queryset=SavedSearch.objects.filter(Q(shared=True))
    )
