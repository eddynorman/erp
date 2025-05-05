from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/profile/', views.user_profile, name='user_profile'),
    path('users/<int:pk>/groups/', views.user_groups, name='user_groups'),
    
    # Group management
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('groups/<int:pk>/permissions/', views.group_permissions, name='group_permissions'),
] 