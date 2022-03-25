from django import forms
from django.contrib.auth.models import User
from . import models

class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = ['category_name']


class PolicyForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=models.Category.objects.all(),empty_label="Category Name", to_field_name="id")
    class Meta:
        model = models.Policy
        fields = ['policy_name', 'sum_assurance', 'premium']


class CustomerPolicyForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=models.Category.objects.all(),empty_label="Category Name", to_field_name="id")
    class Meta:
        model = models.PolicyRecord
        fields = ['sum_assurance', 'premium']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ['description']
        widgets = {
        'description': forms.Textarea(attrs={'rows': 6, 'cols': 30})
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = models.InsuranceEventRecord
        fields = ['description', 'policy']
        widgets = {
        'description': forms.Textarea(attrs={'rows': 3, 'cols': 30})
        }


class EventAnswerForm(forms.ModelForm):
    class Meta:
        model = models.InsuranceEventRecord
        fields = ['admin_comment']
        widgets = {
        'admin_comment': forms.Textarea(attrs={'rows': 3, 'cols': 30})
        }