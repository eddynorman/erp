from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Home
    path('', views.HomeView.as_view(), name='dashboard'),
    
    # Store URLs
    path('stores/', views.store_list, name='store_list'),
    path('stores/create/', views.store_create, name='store_create'),
    path('stores/<int:pk>/', views.store_detail, name='store_detail'),
    path('stores/<int:pk>/edit/', views.store_edit, name='store_edit'),
    path('stores/<int:pk>/delete/', views.StoreDeleteView.as_view(), name='store_delete'),
    
    # Sale Point URLs
    path('sale-points/', views.SalePointListView.as_view(), name='sale_point_list'),
    path('sale-points/create/', views.SalePointCreateView.as_view(), name='sale_point_create'),
    path('sale-points/<int:pk>/', views.SalePointDetailView.as_view(), name='sale_point_detail'),
    path('sale-points/<int:pk>/edit/', views.SalePointUpdateView.as_view(), name='sale_point_edit'),
    path('sale-points/<int:pk>/delete/', views.SalePointDeleteView.as_view(), name='sale_point_delete'),
    
    # Supplier URLs
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    
    # Item URLs
    path('items/', views.item_list, name='item_list'),
    path('items/create/', views.item_create, name='item_create'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    
    # Item Unit URLs
    path('units/', views.ItemUnitListView.as_view(), name='unit_list'),
    path('units/create/', views.ItemUnitCreateView.as_view(), name='unit_create'),
    path('units/<int:pk>/edit/', views.ItemUnitUpdateView.as_view(), name='unit_edit'),
    path('units/<int:pk>/delete/', views.ItemUnitDeleteView.as_view(), name='unit_delete'),
    
    # Item Kit URLs
    path('kits/', views.ItemKitListView.as_view(), name='kit_list'),
    path('kits/create/', views.ItemKitCreateView.as_view(), name='kit_create'),
    path('kits/<int:pk>/', views.ItemKitDetailView.as_view(), name='kit_detail'),
    path('kits/<int:pk>/edit/', views.ItemKitUpdateView.as_view(), name='kit_edit'),
    path('kits/<int:pk>/delete/', views.ItemKitDeleteView.as_view(), name='kit_delete'),
    
    # Adjustment URLs
    path('adjustments/', views.AdjustmentListView.as_view(), name='adjustment_list'),
    path('adjustments/create/', views.adjustment_create, name='adjustment_create'),
    path('adjustments/<int:pk>/', views.AdjustmentDetailView.as_view(), name='adjustment_detail'),
    path('adjustments/<int:pk>/edit/', views.AdjustmentUpdateView.as_view(), name='adjustment_edit'),
    path('adjustments/<int:pk>/delete/', views.AdjustmentDeleteView.as_view(), name='adjustment_delete'),
    
    # Requisition URLs
    path('requisitions/', views.RequisitionListView.as_view(), name='requisition_list'),
    path('requisitions/create/', views.requisition_create, name='requisition_create'),
    path('requisitions/<int:pk>/', views.RequisitionDetailView.as_view(), name='requisition_detail'),
    path('requisitions/<int:pk>/edit/', views.RequisitionUpdateView.as_view(), name='requisition_edit'),
    path('requisitions/<int:pk>/delete/', views.RequisitionDeleteView.as_view(), name='requisition_delete'),
    
    # Receiving URLs
    path('receivings/', views.ReceivingListView.as_view(), name='receiving_list'),
    path('receivings/create/', views.receiving_create, name='receiving_create'),
    path('receivings/<int:pk>/', views.ReceivingDetailView.as_view(), name='receiving_detail'),
    path('receivings/<int:pk>/edit/', views.ReceivingUpdateView.as_view(), name='receiving_edit'),
    path('receivings/<int:pk>/delete/', views.ReceivingDeleteView.as_view(), name='receiving_delete'),
    
    # Issue URLs
    path('issues/', views.IssueListView.as_view(), name='issue_list'),
    path('issues/create/', views.issue_create, name='issue_create'),
    path('issues/<int:pk>/', views.IssueDetailView.as_view(), name='issue_detail'),
    path('issues/<int:pk>/edit/', views.IssueUpdateView.as_view(), name='issue_edit'),
    path('issues/<int:pk>/delete/', views.IssueDeleteView.as_view(), name='issue_delete'),
    
    # API Endpoints
    path('api/items/<int:item_id>/stock/', views.get_item_stock, name='api_item_stock'),
    path('api/items/low-stock/', views.get_low_stock_items, name='api_low_stock_items'),
    path('api/items/<int:item_id>/units/', views.get_item_units, name='api_item_units'),
]