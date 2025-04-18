from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import *
from company.models import Branch,Department,Category

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'branch','address', 'contact_person', 'contact_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branch'].queryset = Branch.objects.all()
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save'))

class SalePointForm(forms.ModelForm):
    class Meta:
        model = SalePoint
        fields = ['name', 'branch','address', 'contact_person', 'contact_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branch'].queryset = Branch.objects.all()
    
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'address', 'contact_person', 'contact_number']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save'))

class ItemForm(forms.ModelForm):
    store = forms.ModelChoiceField(queryset=Store.objects.all(), required=True, help_text="Select a store for this item")
    class Meta:
        model = Item
        fields = ['name', 'bar_code','department','category','initial_stock','buying_price','selling_price','is_sellable','smallest_unit','minimum_stock','optimum_stock']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        branch = Branch.objects.first()
        self.fields['department'].queryset = branch.department_set.all()
        self.fields['category'].queryset = Category.objects.none()

        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['category'].queryset = Category.objects.filter(department=department_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['category'].queryset = Category.objects.filter(department=self.instance.department)

    def save(self, commit=True):
        item = super().save(commit=False)
        if commit:
            item.save()
            store = self.cleaned_data['store']
            quantity = item.initial_stock
            StoreItem.objects.create(store=store, item=item, quantity=quantity) 
            
        return item
    
    
class ItemKitForm(forms.ModelForm):
    class Meta:
        model = ItemKit
        fields = ['name', 'department', 'category', 'selling_price']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        branch = Branch.objects.first()
        self.fields['department'].queryset = branch.department_set.all()
        self.fields['category'].queryset = Category.objects.none()

        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['category'].queryset = Category.objects.filter(department=department_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['category'].queryset = Category.objects.filter(department=self.instance.department)

class ItemKitItemForm(forms.ModelForm):
    class Meta:
        model = ItemKitItem
        fields = ['item', 'quantity']

# Create an inline formset for managing items inside an Item Kit
ItemKitItemFormSet = inlineformset_factory(
    ItemKit, ItemKitItem, 
    form=ItemKitItemForm,
    extra=1,  # Allow adding extra items
    can_delete=True  # Allow deletion
)

class ItemUnitForm(forms.ModelForm):
    class Meta:
        model = ItemUnit
        fields = ['item', 'unit', 'smallest_units', 'buying_price', 'selling_price']
        
class AdjustmentForm(forms.ModelForm):
    class Meta:
        model = Adjustment
        fields = ['item', 'quantity', 'reason', 'user_responsible','in_store','store','sale_point']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 1}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['store'].queryset = Store.objects.filter(status='Active')
        self.fields['sale_point'].queryset = SalePoint.objects.filter(status='Active')
        
        # Make the store and sale_point fields not required in the form
        # (they'll be required based on the in_store value)
        self.fields['store'].required = False
        self.fields['sale_point'].required = False
        
        # Add some JavaScript to handle the in_store toggle
        self.fields['in_store'].widget.attrs.update({
            'onchange': 'toggleLocationFields(this.checked)'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        in_store = cleaned_data.get('in_store')
        store = cleaned_data.get('store')
        sale_point = cleaned_data.get('sale_point')
        
        if in_store and not store:
            self.add_error('store', 'Store is required when adjusting store inventory')
        
        if not in_store and not sale_point:
            self.add_error('sale_point', 'Sale point is required when adjusting sale point inventory')
            
        return cleaned_data
class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = ['department','user_responsible']
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        branch = Branch.objects.first()
        self.fields['department'].queryset = branch.department_set.all()
        

class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = ['department', 'user_responsible']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'user_responsible': forms.Select(attrs={'class': 'form-select'}),
        }

class RequisitionItemForm(forms.ModelForm):
    class Meta:
        model = RequisitionItem
        fields = ['item', 'unit', 'quantity', 'unit_cost', 'total_cost', 'available_stock']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select item-select'}),
            'unit': forms.Select(attrs={'class': 'form-select unit-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control unit-cost', 'readonly': 'readonly'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control total-cost', 'readonly': 'readonly'}),
            'available_stock': forms.NumberInput(attrs={'class': 'form-control available-stock', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Don't set an empty queryset - instead use all units but let JS filter them
        if self.instance and self.instance.item_id:
            self.fields['unit'].queryset = ItemUnit.objects.filter(item=self.instance.item)
        else:
            # Use all units instead of none - the JS will filter them appropriately
            self.fields['unit'].queryset = ItemUnit.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        unit = cleaned_data.get('unit')
        
        if item and unit:
            # Check if the unit belongs to the selected item
            if not ItemUnit.objects.filter(item=item, id=unit.id).exists():
                self.add_error('unit', 'Please select a valid unit for this item.')
        
        return cleaned_data
# Create the formset for RequisitionItem
RequisitionItemFormSet = inlineformset_factory(
    Requisition, 
    RequisitionItem,
    form=RequisitionItemForm,
    extra=1,
    can_delete=True
)

class RequisitionApprovalForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = ['approved', 'approved_by']
        widgets = {
            'approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'approved_by': forms.Select(attrs={'class': 'form-select'}),
        }

class ReceivingForm(forms.ModelForm):
    class Meta:
        model = Receiving
        fields = ['user_responsible','department','supplier','is_store','store','sale_point']
        widgets = {
            'is_store':forms.CheckboxInput(attrs={'class':'form-check-input is-store'}),
            'store':forms.Select(attrs={'class':'form-select store-select'}),
            'sale_point':forms.Select(attrs={'class':'form-select sale-point-select'})
        }
    
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        branch = Branch.objects.first()
        self.fields['department'].queryset = Department.objects.filter(branch=branch)
        self.fields['store'].queryset = Store.objects.all().filter(branch=branch)
        self.fields['sale_point'].queryset = SalePoint.objects.all().filter(branch=branch)
    
    def clean(self):
        cleaned_data = super().clean()
        is_store = cleaned_data.get('is_store')
        store = cleaned_data.get('store')
        sale_point = cleaned_data.get('sale_point')
        
        if is_store and not store:
            self.add_error('store',"If Is Store is checked you must select a store")
        else:
            if not sale_point and not is_store:
                self.add_error('sale_point',"If Is Store is Unchecked you must select a sale point")  

class ReceivedItemForm(forms.ModelForm):
    class Meta:
        model = ReceivedItem
        fields = ['item','unit','quantity','unit_price','total_cost']
        widgets = {
            'item':forms.Select(attrs={'class':'form-select item-select'}),
            'unit':forms.Select(attrs={'class':'form-select unit-select'}),
            'quantity':forms.NumberInput(attrs={'class':'form-input quantity-input'}),
            'unit_price':forms.NumberInput(attrs={'class':'form-input unit-price','readonly':'readonly'}),
            'total_cost':forms.NumberInput(attrs={'class':'form-input total-cost','readonly':'readonly'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Don't set an empty queryset - instead use all units but let JS filter them
        if self.instance and self.instance.item_id:
            self.fields['unit'].queryset = ItemUnit.objects.filter(item=self.instance.item)
        else:
            # Use all units instead of none - the JS will filter them appropriately
            self.fields['unit'].queryset = ItemUnit.objects.all()  
    
    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        unit = cleaned_data.get('unit')
        
        if item and unit:
            # Check if the unit belongs to the selected item
            if not ItemUnit.objects.filter(item=item, id=unit.id).exists():
                self.add_error('unit', 'Please select a valid unit for this item.')
        
        return cleaned_data   

ReceivedItemFormSet = inlineformset_factory(
    Receiving,ReceivedItem,
    form=ReceivedItemForm,
    extra=2,
    can_delete=True,
)    

        
# Add these to your existing forms.py file

class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['transfer_type', 'from_store', 'to_store', 'from_salepoint', 'to_salepoint', 'user_responsible', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_store'].required = False
        self.fields['to_store'].required = False
        self.fields['from_salepoint'].required = False
        self.fields['to_salepoint'].required = False

        # Add JavaScript to dynamically show/hide fields based on transfer type
        self.fields['transfer_type'].widget.attrs.update({
            'onchange': 'handleTransferTypeChange(this.value)'
        })

class TransferItemForm(forms.ModelForm):
    class Meta:
        model = TransferItem
        fields = ['item', 'unit', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = ItemUnit.objects.all()

        if 'item' in self.data:
            try:
                item_id = int(self.data.get('item'))
                self.fields['unit'].queryset = ItemUnit.objects.filter(item_id=item_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.item:
            self.fields['unit'].queryset = ItemUnit.objects.filter(item=self.instance.item)

TransferItemFormSet = forms.inlineformset_factory(
    Transfer, TransferItem, form=TransferItemForm,
    extra=1, can_delete=True
)

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['store', 'sale_point', 'requested_by', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class IssueItemForm(forms.ModelForm):
    class Meta:
        model = IssuedItem
        fields = ['item', 'unit', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].queryset = ItemUnit.objects.all()

        if 'item' in self.data:
            try:
                item_id = int(self.data.get('item'))
                self.fields['unit'].queryset = ItemUnit.objects.filter(item_id=item_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.item:
            self.fields['unit'].queryset = ItemUnit.objects.filter(item=self.instance.item)

IssueItemFormSet = forms.inlineformset_factory(
    Issue, IssuedItem, form=IssueItemForm,
    extra=1, can_delete=True
)

class IssueApprovalForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['approved_by', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
