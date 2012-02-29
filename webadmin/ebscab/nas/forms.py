from django.forms import ModelForm
from nas.models import Nas


class NasForm(ModelForm):
    class Meta:
        model = Nas