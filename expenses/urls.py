from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Expense CRUD
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # Expense actions
    path('expenses/<int:pk>/submit/', views.expense_submit, name='expense_submit'),
    path('expenses/<int:pk>/approve/', views.expense_approve, name='expense_approve'),
    path('expenses/<int:pk>/reject/', views.expense_reject, name='expense_reject'),
    path('expenses/bulk-action/', views.bulk_expense_action, name='bulk_expense_action'),
    
    # Attachments
    path('expenses/<int:expense_pk>/attachments/upload/', views.attachment_upload, name='attachment_upload'),
    path('attachments/<int:pk>/delete/', views.attachment_delete, name='attachment_delete'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    
    # Expense Types
    path('types/', views.expense_type_list, name='expense_type_list'),
    path('types/create/', views.expense_type_create, name='expense_type_create'),
    
    # Recurring Expenses
    path('recurring/', views.recurring_expense_list, name='recurring_expense_list'),
    path('recurring/create/', views.recurring_expense_create, name='recurring_expense_create'),
] 