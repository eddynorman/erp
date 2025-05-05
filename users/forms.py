from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserCreationForm
from .models import CustomGroup, GroupPermission, UserGroup

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class CustomGroupForm(forms.ModelForm):
    class Meta:
        model = CustomGroup
        fields = ['group', 'description']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class GroupPermissionForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = GroupPermission
        fields = ['permissions']

class UserGroupForm(forms.ModelForm):
    class Meta:
        model = UserGroup
        fields = ['user', 'group']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 