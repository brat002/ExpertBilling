from django import forms
from ticket.models import Type

class AddTicket(forms.Form):
    def __init__(self, *args, **kwargs):
        #self.base_fields['']=
        self.base_fileds['user'] = forms.CharFiled(label = u'пользователь')
        self.base_fileds['theme'] = forms.CharField(label = u'Тема')
        self.base_fileds['type'] = forms.ChoiceFiled(label = u'тип', choices =Type.objects.values_list('id','name') )
        self.base_fileds['text'] = forms.CharFiled(label = u'текст', widget=forms.TextArea())
        self.base_fields['owner'] = forms.ChoiceFiled(label = u'Назначить исполнителя' )
        
        super(AddTicket, self).__init__()