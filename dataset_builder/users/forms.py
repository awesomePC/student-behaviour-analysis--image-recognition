from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

from .choices import USER_TYPE_CHOICES

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # show only specific fields
        selected_choices = ["candidate"]

        self.fields['user_type'].choices = [
            (k, v) for k, v in USER_TYPE_CHOICES if k in selected_choices
        ]

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 'user_type',
            'password1', 'password2', 'phone'
        ]


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name',)



#### more
# https://medium.com/@gajeshbhat/extending-and-customizing-django-allauth-eed206623a1a