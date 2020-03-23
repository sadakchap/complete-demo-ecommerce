from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import UserAddress
import re

User = get_user_model()

class UserAdminCreationForm(forms.ModelForm):
    password1 =  forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)  

    class Meta:
        model =  User
        fields = ('email', )
    
    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError('Email must be Unique!')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Both passwords must be same!")
        return super(UserAdminCreationForm, self).clean(*args, **kwargs)
    
    def save(self, commit=True):
        # user = super(UserAdminCreationForm, self).save(commit=False)
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password2'))
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'active', 'admin')

    def clean_password(self):
        return self.initial["password"] # always return initial value


class UserLoginForm(forms.Form):
    email       = forms.CharField()
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

class UserRegisterForm(forms.ModelForm):
    email       = forms.EmailField()
    password1   = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2   = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'first_name', 'last_name',)

    def clean_email(self):
        email   = self.cleaned_data.get('email')
        qs      = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError('Email already taken, perhaps Logging In!')
        return email

    def clean_password2(self):
        pwrd1 = self.cleaned_data.get('password1')
        pwrd2 = self.cleaned_data.get('password2')
        if pwrd1 and pwrd2 and pwrd1 != pwrd2:
            raise forms.ValidationError('Password must match!')
        return pwrd2


def phone_number_validator(regex=None, message=None):
    message = "Enter a valid number, select country code from dropdown, 10 digits are allowed"
    if (re.match(r'^\d{3}[-]?\d{3}[-]?\d{4}$', regex)):
        return regex
    else:
        raise forms.ValidationError(message)

class UserAddressForm(forms.ModelForm):
    COUNTRY_CODES = (
        ('+91', '+91'),
        ('+1', '+1'),
    )
    full_name   = forms.CharField(label="Full Name", error_messages={'required': 'Enter your Full Name.'})
    country_code = forms.CharField(max_length=4, widget=forms.Select(
        choices=COUNTRY_CODES), help_text='Choose from dropdown')
    phone       = forms.CharField(max_length=13, help_text='Enter phone number like "123-456-7890" ')
    pin_code    = forms.CharField(max_length=6, help_text='Enter valid pin code')  
    line_1      = forms.CharField(label="Street No.", max_length=255)
    line_2      = forms.CharField(label="Colony, Locality, Village", max_length=255)

    class Meta:
        model = UserAddress
        fields = ('full_name','country_code', 'phone', 'pin_code', 'line_1', 'line_2', 'landmark', 'city', 'state', 'address_type')
    
    def clean_phone(self):
        phone = phone_number_validator(self.cleaned_data.get('phone'))
        cc = self.cleaned_data.get('country_code')
        phone = cc + ' ' + phone
        return phone
    
    def clean_pin_code(self):
        cc = self.cleaned_data.get('country_code')
        value = self.cleaned_data.get('pin_code')
        if len(cc) == 2:
            # US Zip code has 5 didgits only
            print("going in")
            raw_string = r'^[0-9]{5}$'
            message = 'Enter a valid zip code of 5 digits only!'
        else:
            # Indian Pin code has 6 digits only, first number be 0
            raw_string = r'[1-9][0-9]{5}$'
            message = 'Enter a valid, not starting from 0, pin code of 6 digits only!'
        if (re.match(raw_string, value)):
            return value
        else:
            raise forms.ValidationError(message)
