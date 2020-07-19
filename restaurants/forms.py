from django import forms

from restaurants.models import Client


class LoginForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Please enter your name to proceed"
