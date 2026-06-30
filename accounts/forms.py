"""
accounts/forms.py
Registration and profile forms with Bootstrap 5 styling via crispy-forms.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field

from .models import User


class RegistrationForm(UserCreationForm):
    """Public registration form – always creates a CITIZEN account."""

    email      = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=50, required=True)
    last_name  = forms.CharField(max_length=50, required=True)
    phone      = forms.CharField(max_length=20, required=False)
    address    = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    class Meta:
        model  = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'phone', 'address', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('first_name', css_class='col-md-6'),
                Column('last_name',  css_class='col-md-6')),
            'username', 'email', 'phone', 'address',
            'password1', 'password2',
            Submit('submit', 'Create Account', css_class='btn btn-primary w-100 mt-2'),
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_CITIZEN
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Styled login form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username', 'password',
            Submit('submit', 'Sign In', css_class='btn btn-primary w-100 mt-2'),
        )


class ProfileForm(forms.ModelForm):
    """Allows users to update their own profile details."""

    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'address', 'avatar')
        widgets = {'address': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('first_name', css_class='col-md-6'),
                Column('last_name',  css_class='col-md-6')),
            'email', 'phone', 'address', 'avatar',
            Submit('submit', 'Save Changes', css_class='btn btn-primary'),
        )

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            from django.conf import settings
            import os
            if avatar.size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Avatar must be smaller than 5 MB.')
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
                raise forms.ValidationError('Only JPG, PNG, GIF, or WEBP images are allowed.')
        return avatar
