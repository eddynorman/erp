"""
Sales Management Admin

This module defines the admin interface for the sales management system.
"""

from django.contrib import admin
from .models import (
    Customer, Sale, SaleItem, SaleKit, Payment, Return,
    ReturnItem, ReturnKit, Discount, Tax, SalesPerson
)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'credit_limit', 'balance', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

class SaleKitInline(admin.TabularInline):
    model = SaleKit
    extra = 1

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'sale_point', 'sales_person', 'total_amount', 'payment_status', 'date')
    list_filter = ('payment_status', 'payment_method', 'date')
    search_fields = ('invoice_number', 'customer__name', 'sales_person__name')
    readonly_fields = ('invoice_number', 'created_at', 'updated_at')
    inlines = [SaleItemInline, SaleKitInline, PaymentInline]

class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 1

class ReturnKitInline(admin.TabularInline):
    model = ReturnKit
    extra = 1

@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ('return_number', 'sale', 'customer', 'total_amount', 'status', 'date')
    list_filter = ('status', 'date')
    search_fields = ('return_number', 'sale__invoice_number', 'customer__name')
    readonly_fields = ('return_number', 'created_at', 'updated_at')
    inlines = [ReturnItemInline, ReturnKitInline]

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SalesPerson)
class SalesPersonAdmin(admin.ModelAdmin):
    list_display = ('employee', 'branch', 'total_sales', 'total_returns', 'net_sales')
    list_filter = ('branch',)
    search_fields = ('employee__name', 'branch__name')
    readonly_fields = ('created_at', 'updated_at')
