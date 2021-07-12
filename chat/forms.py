from django import forms
from django.db import models
from django.db.models import fields
from django import forms
from .models import Group

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("__all__")
        widgets = {
            "password" : forms.PasswordInput(),
        }