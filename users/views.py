from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import CustomGroup, GroupPermission, UserGroup, UserProfile
from .forms import (
    CustomUserCreationForm, CustomGroupForm, GroupPermissionForm,
    UserGroupForm, UserEditForm
)

@login_required
@permission_required('auth.view_user')
def user_list(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@login_required
@permission_required('auth.add_user')
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'User created successfully.')
            return redirect('users:user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/user_form.html', {'form': form})

@login_required
@permission_required('auth.change_user')
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('users:user_list')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'users/user_form.html', {'form': form})

@login_required
@permission_required('auth.delete_user')
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('users:user_list')
    return render(request, 'users/user_confirm_delete.html', {'user': user})

@login_required
@permission_required('auth.view_group')
def group_list(request):
    groups = CustomGroup.objects.all()
    return render(request, 'users/group_list.html', {'groups': groups})

@login_required
@permission_required('auth.add_group')
def group_create(request):
    if request.method == 'POST':
        form = CustomGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, 'Group created successfully.')
            return redirect('users:group_list')
    else:
        form = CustomGroupForm()
    return render(request, 'users/group_form.html', {'form': form})

@login_required
@permission_required('auth.change_group')
def group_edit(request, pk):
    group = get_object_or_404(CustomGroup, pk=pk)
    if request.method == 'POST':
        form = CustomGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group updated successfully.')
            return redirect('users:group_list')
    else:
        form = CustomGroupForm(instance=group)
    return render(request, 'users/group_form.html', {'form': form})

@login_required
@permission_required('auth.delete_group')
def group_delete(request, pk):
    group = get_object_or_404(CustomGroup, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Group deleted successfully.')
        return redirect('users:group_list')
    return render(request, 'users/group_confirm_delete.html', {'group': group})

@login_required
@permission_required('auth.change_group')
def group_permissions(request, pk):
    group = get_object_or_404(CustomGroup, pk=pk)
    if request.method == 'POST':
        form = GroupPermissionForm(request.POST)
        if form.is_valid():
            permissions = form.cleaned_data['permissions']
            group.group.permissions.set(permissions)
            messages.success(request, 'Group permissions updated successfully.')
            return redirect('users:group_list')
    else:
        form = GroupPermissionForm(initial={'permissions': group.group.permissions.all()})
    return render(request, 'users/group_permissions.html', {'form': form, 'group': group})

@login_required
@permission_required('auth.change_user')
def user_groups(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserGroupForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            UserGroup.objects.get_or_create(user=user, group=group)
            messages.success(request, 'User added to group successfully.')
            return redirect('users:user_list')
    else:
        form = UserGroupForm()
    return render(request, 'users/user_groups.html', {
        'form': form,
        'user': user,
        'user_groups': UserGroup.objects.filter(user=user)
    })
