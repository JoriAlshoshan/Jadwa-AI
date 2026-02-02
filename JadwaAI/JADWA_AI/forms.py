from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Projects

class JadwaUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-input'})
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input'}),
            "password1": forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input'}),
            "password2": forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-input'}),
        }

class JadwaAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input'})
    )

class ProjectInformationForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ['project_name','Project_type','project_location','project_location_type','project_budget','project_duration','number_of_employees']
        widgets ={
            'project_name' : forms.TextInput(attrs={'class':'form-input'}),
            'Project_type' : forms.Select(attrs={'class':'form-select'}),
            'project_location' : forms.TextInput(attrs={'class':'form-input'}),
            'project_location_type' : forms.Select(attrs={'class':'form-select'}),
            'project_budget' : forms.NumberInput(attrs={'class':'form-input'}),
            'project_duration' : forms.NumberInput(attrs={'class':'form-input'}),
            'number_of_employees' : forms.NumberInput(attrs={'class':'form-input'})
        }
        labels ={
            'project_name' : 'project name:' ,
            'Project_type' : 'Project type:',
            'project_location' : 'project location:',
            'project_location_type' : 'project location type:',
            'project_budget' : 'project budget:',
            'project_duration' : 'project duration:',
            'number_of_employees' : 'number of employees:'
        }
        