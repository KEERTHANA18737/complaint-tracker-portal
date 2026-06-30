"""
complaints/forms.py
ModelForms for submitting, editing, and managing complaints.
"""

import os
from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field

from .models import Complaint, Category
from accounts.models import User


class ComplaintForm(forms.ModelForm):
    """Used by citizens to submit or edit a complaint."""

    class Meta:
        model  = Complaint
        fields = ('title', 'description', 'category', 'location',
                  'image', 'priority', 'latitude', 'longitude')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'latitude':    forms.HiddenInput(),
            'longitude':   forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['priority'].initial  = Complaint.PRIORITY_MEDIUM
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            Row(Column('category', css_class='col-md-6'),
                Column('priority', css_class='col-md-6')),
            'location',
            'latitude', 'longitude',
            'image',
            Submit('submit', 'Submit Complaint', css_class='btn btn-primary'),
        )

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'size'):
            if image.size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Image must be smaller than 5 MB.')
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
                raise forms.ValidationError(
                    f'Allowed image types: {", ".join(settings.ALLOWED_IMAGE_EXTENSIONS)}')
        return image


class StatusUpdateForm(forms.ModelForm):
    """Officers/Admins use this to change status, priority, assignment."""

    remarks = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text='Optional remarks about this status change.',
    )

    class Meta:
        model  = Complaint
        fields = ('status', 'priority', 'assigned_to')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(
            role__in=[User.ROLE_OFFICER, User.ROLE_ADMIN])
        self.fields['assigned_to'].required = False
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('status',      css_class='col-md-4'),
                Column('priority',    css_class='col-md-4'),
                Column('assigned_to', css_class='col-md-4')),
            'remarks',
            Submit('submit', 'Update Complaint', css_class='btn btn-warning'),
        )


class SearchForm(forms.Form):
    """Complaint search and filter form."""

    q          = forms.CharField(required=False, label='Search',
                                 widget=forms.TextInput(attrs={'placeholder': 'Title or location…'}))
    status     = forms.ChoiceField(required=False, choices=[('', 'All Statuses')] +
                                   Complaint.STATUS_CHOICES)
    priority   = forms.ChoiceField(required=False, choices=[('', 'All Priorities')] +
                                   Complaint.PRIORITY_CHOICES)
    category   = forms.ModelChoiceField(required=False, queryset=Category.objects.all(),
                                        empty_label='All Categories')
    officer    = forms.ModelChoiceField(required=False,
                                        queryset=User.objects.filter(
                                            role__in=[User.ROLE_OFFICER, User.ROLE_ADMIN]),
                                        empty_label='All Officers')
    sort       = forms.ChoiceField(required=False, choices=[
        ('-created_at', 'Newest'),
        ('created_at',  'Oldest'),
    ])
