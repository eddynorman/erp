"""
Sales Management Views

This module defines the views for managing sales in the ERP system.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum, F, Q
from .models import (
    Customer, Sale, SaleItem, SaleKit, Payment, Return,
    ReturnItem, ReturnKit, Discount, Tax, SalesPerson
)
from .forms import (
    CustomerForm, SaleForm, SaleItemForm, SaleKitForm, PaymentForm,
    ReturnForm, ReturnItemForm, ReturnKitForm, DiscountForm, TaxForm,
    SalesPersonForm
)
from inventory.models import Item, ItemKit, SalePoint, SalePointItem
from company.models import Employee, Branch
import json

# Customer Views
@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    paginator = Paginator(customers, 10)
    page = request.GET.get('page')
    customers = paginator.get_page(page)
    return render(request, 'sales/customer_list.html', {'customers': customers})

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'sales/customer_form.html', {'form': form, 'title': 'Create Customer'})

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'sales/customer_form.html', {'form': form, 'title': 'Edit Customer'})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    sales = Sale.objects.filter(customer=customer).order_by('-date')
    return render(request, 'sales/customer_detail.html', {
        'customer': customer,
        'sales': sales
    })

# Sale Views
@login_required
def sale_list(request):
    sales = Sale.objects.all().order_by('-date')
    paginator = Paginator(sales, 10)
    page = request.GET.get('page')
    sales = paginator.get_page(page)
    return render(request, 'sales/sale_list.html', {'sales': sales})

@login_required
@transaction.atomic
def sale_create(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.invoice_number = generate_invoice_number()
            sale.save()
            messages.success(request, 'Sale created successfully')
            return redirect('sale_edit', pk=sale.pk)
    else:
        form = SaleForm()
    return render(request, 'sales/sale_form.html', {'form': form, 'title': 'Create Sale'})

@login_required
@transaction.atomic
def sale_edit(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sale updated successfully')
            return redirect('sale_detail', pk=sale.pk)
    else:
        form = SaleForm(instance=sale)
    
    items = sale.saleitem_set.all()
    kits = sale.salekit_set.all()
    payments = sale.payment_set.all()
    
    return render(request, 'sales/sale_edit.html', {
        'form': form,
        'sale': sale,
        'items': items,
        'kits': kits,
        'payments': payments
    })

@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    items = sale.saleitem_set.all()
    kits = sale.salekit_set.all()
    payments = sale.payment_set.all()
    return render(request, 'sales/sale_detail.html', {
        'sale': sale,
        'items': items,
        'kits': kits,
        'payments': payments
    })

@login_required
@transaction.atomic
def sale_item_add(request, sale_pk):
    sale = get_object_or_404(Sale, pk=sale_pk)
    if request.method == 'POST':
        form = SaleItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.sale = sale
            item.save()
            
            # Update stock
            sale_point = sale.sale_point
            stock = SalePointItem.objects.get_or_create(
                sale_point=sale_point,
                item=item.item,
                defaults={'quantity': 0}
            )[0]
            stock.quantity -= item.quantity
            stock.save()
            
            messages.success(request, 'Item added successfully')
            return redirect('sale_edit', pk=sale.pk)
    else:
        form = SaleItemForm()
    return render(request, 'sales/sale_item_form.html', {'form': form, 'sale': sale})

@login_required
@transaction.atomic
def sale_kit_add(request, sale_pk):
    sale = get_object_or_404(Sale, pk=sale_pk)
    if request.method == 'POST':
        form = SaleKitForm(request.POST)
        if form.is_valid():
            kit = form.save(commit=False)
            kit.sale = sale
            kit.save()
            
            # Update stock for all items in the kit
            sale_point = sale.sale_point
            for kit_item in kit.kit.itemkititem_set.all():
                stock = SalePointItem.objects.get_or_create(
                    sale_point=sale_point,
                    item=kit_item.item,
                    defaults={'quantity': 0}
                )[0]
                stock.quantity -= kit_item.quantity * kit.quantity
                stock.save()
            
            messages.success(request, 'Kit added successfully')
            return redirect('sale_edit', pk=sale.pk)
    else:
        form = SaleKitForm()
    return render(request, 'sales/sale_kit_form.html', {'form': form, 'sale': sale})

@login_required
@transaction.atomic
def payment_add(request, sale_pk):
    sale = get_object_or_404(Sale, pk=sale_pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.sale = sale
            payment.save()
            messages.success(request, 'Payment added successfully')
            return redirect('sale_edit', pk=sale.pk)
    else:
        form = PaymentForm()
    return render(request, 'sales/payment_form.html', {'form': form, 'sale': sale})

# Return Views
@login_required
def return_list(request):
    returns = Return.objects.all().order_by('-date')
    paginator = Paginator(returns, 10)
    page = request.GET.get('page')
    returns = paginator.get_page(page)
    return render(request, 'sales/return_list.html', {'returns': returns})

@login_required
@transaction.atomic
def return_create(request):
    if request.method == 'POST':
        form = ReturnForm(request.POST)
        if form.is_valid():
            return_obj = form.save(commit=False)
            return_obj.return_number = generate_return_number()
            return_obj.save()
            messages.success(request, 'Return created successfully')
            return redirect('return_edit', pk=return_obj.pk)
    else:
        form = ReturnForm()
    return render(request, 'sales/return_form.html', {'form': form, 'title': 'Create Return'})

@login_required
@transaction.atomic
def return_edit(request, pk):
    return_obj = get_object_or_404(Return, pk=pk)
    if request.method == 'POST':
        form = ReturnForm(request.POST, instance=return_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Return updated successfully')
            return redirect('return_detail', pk=return_obj.pk)
    else:
        form = ReturnForm(instance=return_obj)
    
    items = return_obj.returnitem_set.all()
    kits = return_obj.returnkit_set.all()
    
    return render(request, 'sales/return_edit.html', {
        'form': form,
        'return_obj': return_obj,
        'items': items,
        'kits': kits
    })

@login_required
def return_detail(request, pk):
    return_obj = get_object_or_404(Return, pk=pk)
    items = return_obj.returnitem_set.all()
    kits = return_obj.returnkit_set.all()
    return render(request, 'sales/return_detail.html', {
        'return_obj': return_obj,
        'items': items,
        'kits': kits
    })

@login_required
@transaction.atomic
def return_item_add(request, return_pk):
    return_obj = get_object_or_404(Return, pk=return_pk)
    if request.method == 'POST':
        form = ReturnItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.return_obj = return_obj
            item.save()
            
            # Update stock
            sale_point = return_obj.sale.sale_point
            stock = SalePointItem.objects.get_or_create(
                sale_point=sale_point,
                item=item.item,
                defaults={'quantity': 0}
            )[0]
            stock.quantity += item.quantity
            stock.save()
            
            messages.success(request, 'Item added successfully')
            return redirect('return_edit', pk=return_obj.pk)
    else:
        form = ReturnItemForm()
    return render(request, 'sales/return_item_form.html', {'form': form, 'return_obj': return_obj})

@login_required
@transaction.atomic
def return_kit_add(request, return_pk):
    return_obj = get_object_or_404(Return, pk=return_pk)
    if request.method == 'POST':
        form = ReturnKitForm(request.POST)
        if form.is_valid():
            kit = form.save(commit=False)
            kit.return_obj = return_obj
            kit.save()
            
            # Update stock for all items in the kit
            sale_point = return_obj.sale.sale_point
            for kit_item in kit.kit.itemkititem_set.all():
                stock = SalePointItem.objects.get_or_create(
                    sale_point=sale_point,
                    item=kit_item.item,
                    defaults={'quantity': 0}
                )[0]
                stock.quantity += kit_item.quantity * kit.quantity
                stock.save()
            
            messages.success(request, 'Kit added successfully')
            return redirect('return_edit', pk=return_obj.pk)
    else:
        form = ReturnKitForm()
    return render(request, 'sales/return_kit_form.html', {'form': form, 'return_obj': return_obj})

# Discount and Tax Views
@login_required
def discount_list(request):
    discounts = Discount.objects.all().order_by('-created_at')
    return render(request, 'sales/discount_list.html', {'discounts': discounts})

@login_required
def discount_create(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discount created successfully')
            return redirect('discount_list')
    else:
        form = DiscountForm()
    return render(request, 'sales/discount_form.html', {'form': form, 'title': 'Create Discount'})

@login_required
def tax_list(request):
    taxes = Tax.objects.all().order_by('-created_at')
    return render(request, 'sales/tax_list.html', {'taxes': taxes})

@login_required
def tax_create(request):
    if request.method == 'POST':
        form = TaxForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tax created successfully')
            return redirect('tax_list')
    else:
        form = TaxForm()
    return render(request, 'sales/tax_form.html', {'form': form, 'title': 'Create Tax'})

# Sales Person Views
@login_required
def salesperson_list(request):
    salespeople = SalesPerson.objects.all().order_by('-created_at')
    return render(request, 'sales/salesperson_list.html', {'salespeople': salespeople})

@login_required
def salesperson_create(request):
    if request.method == 'POST':
        form = SalesPersonForm(request.POST)
        if form.is_valid():
            salesperson = form.save(commit=False)
            salesperson.update_stats()
            messages.success(request, 'Sales Person created successfully')
            return redirect('salesperson_list')
    else:
        form = SalesPersonForm()
    return render(request, 'sales/salesperson_form.html', {'form': form, 'title': 'Create Sales Person'})

# Helper Functions
def generate_invoice_number():
    """Generate a unique invoice number"""
    prefix = 'INV'
    date = timezone.now().strftime('%Y%m%d')
    last_invoice = Sale.objects.filter(invoice_number__startswith=f'{prefix}{date}').order_by('-invoice_number').first()
    
    if last_invoice:
        last_number = int(last_invoice.invoice_number[-4:])
        new_number = last_number + 1
    else:
        new_number = 1
    
    return f'{prefix}{date}{new_number:04d}'

def generate_return_number():
    """Generate a unique return number"""
    prefix = 'RET'
    date = timezone.now().strftime('%Y%m%d')
    last_return = Return.objects.filter(return_number__startswith=f'{prefix}{date}').order_by('-return_number').first()
    
    if last_return:
        last_number = int(last_return.return_number[-4:])
        new_number = last_number + 1
    else:
        new_number = 1
    
    return f'{prefix}{date}{new_number:04d}'

# API Views
@login_required
def get_item_price(request, item_id):
    """Get the selling price of an item"""
    item = get_object_or_404(Item, pk=item_id)
    return JsonResponse({'price': float(item.selling_price)})

@login_required
def get_kit_price(request, kit_id):
    """Get the selling price of a kit"""
    kit = get_object_or_404(ItemKit, pk=kit_id)
    return JsonResponse({'price': float(kit.selling_price)})

@login_required
def get_item_stock(request, item_id):
    """Get the current stock of an item in a sale point"""
    item = get_object_or_404(Item, pk=item_id)
    sale_point_id = request.GET.get('sale_point_id')
    if sale_point_id:
        stock = SalePointItem.objects.filter(
            item=item,
            sale_point_id=sale_point_id
        ).first()
        return JsonResponse({'stock': stock.quantity if stock else 0})
    return JsonResponse({'stock': 0})

@login_required
def get_kit_stock(request, kit_id):
    """Get the current stock of all items in a kit in a sale point"""
    kit = get_object_or_404(ItemKit, pk=kit_id)
    sale_point_id = request.GET.get('sale_point_id')
    if sale_point_id:
        stock_info = {}
        for kit_item in kit.itemkititem_set.all():
            stock = SalePointItem.objects.filter(
                item=kit_item.item,
                sale_point_id=sale_point_id
            ).first()
            stock_info[kit_item.item.name] = stock.quantity if stock else 0
        return JsonResponse(stock_info)
    return JsonResponse({})
