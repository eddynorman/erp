"""
Sales Management URLs

This module defines the URL patterns for the sales management system.
"""

from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),

    # Sale URLs
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/create/', views.sale_create, name='sale_create'),
    path('sales/<int:pk>/edit/', views.sale_edit, name='sale_edit'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:sale_pk>/items/add/', views.sale_item_add, name='sale_item_add'),
    path('sales/<int:sale_pk>/kits/add/', views.sale_kit_add, name='sale_kit_add'),
    path('sales/<int:sale_pk>/payments/add/', views.payment_add, name='payment_add'),

    # Return URLs
    path('returns/', views.return_list, name='return_list'),
    path('returns/create/', views.return_create, name='return_create'),
    path('returns/<int:pk>/edit/', views.return_edit, name='return_edit'),
    path('returns/<int:pk>/', views.return_detail, name='return_detail'),
    path('returns/<int:return_pk>/items/add/', views.return_item_add, name='return_item_add'),
    path('returns/<int:return_pk>/kits/add/', views.return_kit_add, name='return_kit_add'),

    # Discount URLs
    path('discounts/', views.discount_list, name='discount_list'),
    path('discounts/create/', views.discount_create, name='discount_create'),

    # Tax URLs
    path('taxes/', views.tax_list, name='tax_list'),
    path('taxes/create/', views.tax_create, name='tax_create'),

    # Sales Person URLs
    path('salespeople/', views.salesperson_list, name='salesperson_list'),
    path('salespeople/create/', views.salesperson_create, name='salesperson_create'),

    # API URLs
    path('api/items/<int:item_id>/price/', views.get_item_price, name='get_item_price'),
    path('api/kits/<int:kit_id>/price/', views.get_kit_price, name='get_kit_price'),
    path('api/items/<int:item_id>/stock/', views.get_item_stock, name='get_item_stock'),
    path('api/kits/<int:kit_id>/stock/', views.get_kit_stock, name='get_kit_stock'),

    # Dashboard URL
    path('', views.dashboard, name='dashboard'),
] 