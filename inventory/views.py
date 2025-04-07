# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, DetailView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages

from .models import *
from .forms import *
from company.models import Branch, Department, Category


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


class ItemKitCreateView(CreateView):
    model = ItemKit
    form_class = ItemKitForm
    template_name = 'inventory/itemkit_form.html'
    success_url = reverse_lazy('inventory:itemkit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ItemKitItemFormSet(self.request.POST)
        else:
            context['formset'] = ItemKitItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object  # Link items to ItemKit
            formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class ItemKitUpdateView(UpdateView):
    model = ItemKit
    form_class = ItemKitForm
    template_name = 'inventory/itemkit_form.html'
    success_url = reverse_lazy('inventory:itemkit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ItemKitItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = ItemKitItemFormSet(instance=self.object)  # Ensure instance is set correctly
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save()  # No need for commit=False unless you modify before saving
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)  # 🚀 Use this instead of redirect for consistency
        else:
            print("Formset errors:", formset.errors)
            return self.render_to_response(self.get_context_data(form=form))

class ItemKitListView(ListView):
    model = ItemKit
    template_name = 'inventory/itemkit_list.html'
    context_object_name = 'itemkits'

class ItemKitDetailView(DetailView):
    model = ItemKit
    template_name = 'inventory/itemkit_detail.html'

def deactivate_item_kit(request, pk):
    item_kit = get_object_or_404(ItemKit, pk=pk)
    item_kit.deactivate()
    return redirect('inventory:itemkit_list')

class ItemUnitCreateView(CreateView):
    model = ItemUnit
    form_class = ItemUnitForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:unit_list')

class ItemUnitUpdateView(UpdateView):
    model = ItemUnit
    form_class = ItemUnitForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:unit_list')

class ItemUnitListView(ListView):
    model = ItemUnit
    template_name = "inventory/units.html"
    context_object_name = 'units'

class ItemUnitDeleteView(DeleteView):
    model = ItemUnit
    template_name = 'inventory/gen_confirm_delete.html'
    success_url = reverse_lazy('inventory:unit_list')

class AdjustmentCreateView(CreateView):
    model = Adjustment
    form_class = AdjustmentForm
    template_name = 'inventory/gen_form.html'
    success_url = reverse_lazy('inventory:adjustment_list')

class AdjustmentListView(ListView):
    model = Adjustment
    template_name = 'inventory/adjustment_list.html'
    context_object_name = 'adjustments'

class RequisitionListView(ListView):
    model = Requisition
    template_name = 'inventory/requisition_list.html'
    context_object_name = 'requisitions'
    ordering = ['-date']

class RequisitionDetailView(DetailView):
    model = Requisition
    template_name = 'inventory/requisition_detail.html'
    context_object_name = 'requisition'
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["total_cost"] =sum
    #     return context
    

class RequisitionCreateView(CreateView):
    model = Requisition
    form_class = RequisitionForm
    template_name = 'inventory/requisition_form.html'
    success_url = reverse_lazy('inventory:requisition_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items_formset'] = RequisitionItemFormSet(self.request.POST)
        else:
            context['items_formset'] = RequisitionItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if items_formset.is_valid():
                items_formset.instance = self.object
                items_formset.save()
            else:
                return self.form_invalid(form)
                
        messages.success(self.request, 'Requisition created successfully.')
        return super().form_valid(form)

class RequisitionUpdateView(UpdateView):
    model = Requisition
    form_class = RequisitionForm
    template_name = 'inventory/requisition_form.html'
    success_url = reverse_lazy('inventory:requisition_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['items_formset'] = RequisitionItemFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['items_formset'] = RequisitionItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context['items_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if items_formset.is_valid():
                items_formset.instance = self.object
                items_formset.save()
            else:
                print("Formset errors:", items_formset.errors)
                print(items_formset)
                return self.form_invalid(form)
                
        messages.success(self.request, 'Requisition updated successfully.')
        return super().form_valid(form)

class RequisitionDeleteView(DeleteView):
    model = Requisition
    template_name = 'inventory/gen_confirm_delete.html'
    success_url = reverse_lazy('inventory:requisition_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Requisition deleted successfully.')
        return super().delete(request, *args, **kwargs)

class RequisitionApproveView(UpdateView):
    model = Requisition
    form_class = RequisitionApprovalForm
    template_name = 'inventory/requisition_approve.html'
    success_url = reverse_lazy('inventory:requisition_list')
    
    def form_valid(self, form):
        requisition = form.save(commit=False)
        if requisition.approved:
            requisition.approved_date = timezone.now()
        requisition.save()
        messages.success(self.request, 'Requisition approval status updated.')
        return super().form_valid(form)

# AJAX views for dynamic form handling
def get_item_details(request):
    item_id = request.GET.get('item_id')
    if item_id:
        item = get_object_or_404(Item, id=item_id)
        units = ItemUnit.objects.filter(item=item)
        
        # Return both unit data and their IDs
        return JsonResponse({
            'available_stock': item.total_stock(),
            'units': [{'id': unit.id, 'unit': str(unit.unit)} for unit in units]
        })
    return JsonResponse({'error': 'No item selected'})

def get_unit_price(request):
    unit_id = request.GET.get('unit_id')
    if not unit_id:
        return JsonResponse({'error': 'No unit selected'}, status=400)
    
    try:
        unit = ItemUnit.objects.get(id=unit_id)
        return JsonResponse({
            'buying_price': unit.buying_price,
        })
    except ItemUnit.DoesNotExist:
        return JsonResponse({'error': 'Unit not found'}, status=404)