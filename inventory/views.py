# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Store, Supplier, Item, Receiving, Issue, Requisition
from .forms import StoreForm, SupplierForm #, ItemForm, ReceivingForm, IssueForm, RequisitionForm

class StoreListView(ListView):
    model = Store
    template_name = 'store_list.html'
    context_object_name = 'stores'

class StoreCreateView(CreateView):
    model = Store
    form_class = StoreForm
    template_name = 'inventory/store_form.html'
    success_url = reverse_lazy('inventory/store_list')

class StoreUpdateView(UpdateView):
    model = Store
    form_class = StoreForm
    template_name = 'store_form.html'
    success_url = reverse_lazy('inventory/store_list')

class StoreDeleteView(DeleteView):
    model = Store
    template_name = 'store_confirm_delete.html'
    success_url = reverse_lazy('inventory/store_list')

class SupplierListView(ListView):
    model = Supplier
    template_name = 'supplier_list.html'
    context_object_name = 'suppliers'

class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supplier_form.html'
    success_url = reverse_lazy('supplier_list')
    
class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supplier_form.html'
    success_url = reverse_lazy('supplier_list')
    
class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier_list')
    

# Similar views for Supplier, Item, Receiving, Issue, Recquisition can be created.
