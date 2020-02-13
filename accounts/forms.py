from django import forms
from django.contrib.auth import authenticate
# from .models import User, Profile
from django.contrib.auth import get_user_model

User = get_user_model()

class UserLoginForm(forms.Form):
    email   = forms.CharField()
    password    = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        email   = self.cleaned_data.get('email')
        pswd    = self.cleaned_data.get('password')
        if email and pswd:
            user_qs = User.objects.filter(email=email)
            if user_qs.exists():
                user = user_qs[0]
                if not user.check_password(pswd):
                    raise forms.ValidationError('Incorrect Password')
                if not user.is_active:
                    raise forms.ValidationError('User NOT active, Contact Us for more Information!')
            user = authenticate(username=email, password=pswd)
            if not user:
                raise forms.ValidationError('Email is not registered Yet!')
            return super(UserLoginForm, self).clean(*args, **kwargs)

