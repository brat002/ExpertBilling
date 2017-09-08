# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from helpdesk.utils import attachment_path


class Attachment(models.Model):
    """
    Represents a file attached to a follow-up. This could come from an e-mail
    attachment, or it could be uploaded via the web interface.
    """

    followup = models.ForeignKey('helpdesk.FollowUp', on_delete=models.CASCADE)

    file = models.FileField(
        _('File'),
        upload_to=attachment_path,
    )

    filename = models.CharField(
        _('Filename'),
        max_length=100,
    )

    mime_type = models.CharField(
        _('MIME Type'),
        max_length=30,
    )

    size = models.IntegerField(
        _('Size'),
        help_text=_('Size of this file in bytes'),
    )

    def get_upload_to(self, field_attname):
        """ Get upload_to path specific to this item """
        if not self.id:
            return u''
        return u'helpdesk/attachments/%s/%s' % (
            self.followup.ticket.ticket_for_url,
            self.followup.id
        )

    def __unicode__(self):
        return u'%s' % self.filename

    class Meta:
        ordering = ['filename', ]
        verbose_name = _(u'attachment')
        verbose_name_plural = _(u'Attachments')
