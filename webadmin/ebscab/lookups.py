from billservice.models import Hardware
from selectable.base import ModelLookup
from selectable.decorators import login_required
from selectable.registry import registry


@login_required
class HardwareLookup(ModelLookup):
    model = Hardware
    search_fields = (
        'name__startswith',
        'model__startswith',
        'sn__startswith',
        'comment__icontains'
    )

    def get_query(self, request, term):
        return Hardware.objects.filter(accounthardware__isnull=True)

    def get_item_label(self, item):
        return u'%s %s sn:%s %s' % (
            item.name,
            item.model,
            item.sn,
            ('comment: %s' % item.comment) if item.comment else ''
        )

registry.register(HardwareLookup)
