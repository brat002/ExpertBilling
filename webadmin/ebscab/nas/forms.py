from django.forms import ModelForm
import django.forms as forms
from nas.models import Nas, TrafficClass, TrafficNode, Switch


class NasForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    speed_vendor_1 = forms.IntegerField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xsmall"}))
    speed_attr_id1 = forms.IntegerField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xsmall"}))
    speed_value1 = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge"}))
    speed_vendor_2 = forms.IntegerField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xsmall"}))
    speed_attr_id2 = forms.IntegerField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xsmall"}))
    speed_value2 = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge"}))
    
    user_add_action = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))
    user_enable_action = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))
    user_disable_action = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))
    user_delete_action = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))
    vpn_speed_action =forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))
    ipn_speed_action = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))
    reset_action = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))
    subacc_disable_action = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))
    subacc_enable_action = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))
    subacc_add_action = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))
    subacc_delete_action = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))
    subacc_ipn_speed_action = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"class":"input-xlarge span9"}))

    
    class Meta:
        model = Nas
        
class TrafficClassForm(ModelForm):
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = TrafficClass
        
class TrafficNodeForm(ModelForm):
    traffic_class = forms.ModelChoiceField(queryset=TrafficClass.objects.all(), required=False, widget = forms.HiddenInput)
    id = forms.IntegerField(required=False, widget = forms.HiddenInput)
    class Meta:
        model = TrafficNode
        
class SwitchForm(ModelForm):
    class Meta:
        model = Switch
