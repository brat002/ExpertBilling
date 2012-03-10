from django.forms import ModelForm
from nas.models import Nas, TrafficClass, TrafficNode, Switch


class NasForm(ModelForm):
    class Meta:
        model = Nas
        
class TrafficClassForm(ModelForm):
    class Meta:
        model = TrafficClass
        
class TrafficNodeForm(ModelForm):
    class Meta:
        model = TrafficNode
        
class SwitchForm(ModelForm):
    class Meta:
        model = Switch
