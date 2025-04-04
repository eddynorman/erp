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
]