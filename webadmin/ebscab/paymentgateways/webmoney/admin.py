from django.contrib import admin
from models import Payment


class PaymentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['id', 'sys_invs_no', 'sys_trans_no', 'amount']
    list_filter = ['created']
    ordering = ['-created']
    search_fields = ['id']

admin.site.register(Payment, PaymentAdmin)
