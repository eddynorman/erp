# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Store, Supplier, Item, Receiving, Issue, Requisition
from .forms import StoreForm, SupplierForm , ItemForm #, ReceivingForm, IssueForm, RequisitionForm
from company.models import Department,Category


class HomeView(View):
    def get(self, request):
        return render(request, 'inventory/index.html')
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
    
class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/store_form.html'
    success_url = reverse_lazy('inventory:item_list')

class ItemListView(ListView):
    model = Item
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/store_form.html'
    success_url = reverse_lazy('inventory:item_list')

class ItemDeleteView(DeleteView):
    model = Item
    template_name = 'inventory/store_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_list')

class LoadCategories(View):
    def get(self, request):
        department_id = request.GET.get('department_id')
        categories = Category.objects.filter(department=department_id).values('id', 'category_name')
        return JsonResponse(list(categories), safe=False)
# Similar views for Supplier, Item, Receiving, Issue, Recquisition can be created.
