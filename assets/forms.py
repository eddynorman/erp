from django import forms
from django.forms import modelformset_factory
from .models import Asset, AssetPurchase, DamagedAsset, DisposedAsset, AssetRepair

class CustomDateInput(forms.DateInput):
    input_type = 'date'

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'asset_type','category', 'department', 'initial_purchase_date', 'purchase_cost', 'quantity', 'initial_supplier']
        widgets = {
            'initial_purchase_date': CustomDateInput(),
        }
AssetFormSet = modelformset_factory(Asset, form=AssetForm, extra=2,) 
class AssetPurchaseForm(forms.ModelForm):
    class Meta:
        model = AssetPurchase
        fields = ['purchase_date', 'quantity', 'price', 'supplier']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'},format="dd/mm/yyyy"),
        }

class DamagedAssetForm(forms.ModelForm):
    class Meta:
        model = DamagedAsset
        fields = ['quantity', 'reason']

class AssetRepairForm(forms.ModelForm):
    class Meta:
        model = AssetRepair
        fields = ['quantity', 'cost', 'date','description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DisposedAssetForm(forms.ModelForm):
    class Meta:
        model = DisposedAsset
        fields = ['quantity', 'reason']
