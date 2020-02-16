from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField

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

