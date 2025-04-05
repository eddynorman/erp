from django.urls import path
from .views import *

app_name = 'inventory'
urlpatterns = [
    path('',HomeView.as_view(), name='home'),
    path('stores/', StoreListView.as_view(), name='store_list'),
    path('store/new/', StoreCreateView.as_view(), name='store_create'),
    path('store/<int:pk>/edit/', StoreUpdateView.as_view(), name='store_edit'),
    path('store/<int:pk>/delete/', StoreDeleteView.as_view(), name='store_delete'),
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('supplier/new/', SupplierCreateView.as_view(), name='supplier_create'),
    path('supplier/<int:pk>/edit/', SupplierUpdateView.as_view(), name='supplier_edit'),
    path('supplier/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier_delete'),
    path('items/', ItemListView.as_view(), name='item_list'),
    path('item/new/', ItemCreateView.as_view(), name='item_create'),
    path('item/<int:pk>/edit/', ItemUpdateView.as_view(), name='item_edit'),
    path('item/<int:pk>/delete/', ItemDeleteView.as_view(), name='item_delete'),
    path('item/new/load-categories/',LoadCategories.as_view(), name='ajax_load_categories'),
    path('itemkits/new/load-categories/',LoadCategories.as_view(), name='ajax_load_categories'),
    path('itemkits/', ItemKitListView.as_view(), name='itemkit_list'),
    path('itemkits/new/', ItemKitCreateView.as_view(), name='itemkit_add'),
    path('itemkits/<int:pk>/details/', ItemKitDetailView.as_view(), name='itemkit_detail'),
    path('itemkits/<int:pk>/edit/', ItemKitUpdateView.as_view(), name='itemkit_edit'),
    path('itemkits/<int:pk>/deactivate/', deactivate_item_kit, name='itemkit_deactivate'),
    path('units/', ItemUnitListView.as_view(), name='unit_list'),
    path('units/new/', ItemUnitCreateView.as_view(), name='unit_create'),
    path('units/<int:pk>/edit/', ItemUnitUpdateView.as_view(), name='unit_edit'),
    path('units/<int:pk>/delete/', ItemUnitDeleteView.as_view(), name='unit_delete'),
    path('adjustments/', AdjustmentListView.as_view(), name='adjustment_list'),
    path('adjustments/new/', AdjustmentCreateView.as_view(), name='adjustment_create'),
]