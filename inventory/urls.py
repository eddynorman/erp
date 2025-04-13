from django.urls import path
from .views import *

app_name = 'inventory'
urlpatterns = [
    path('',HomeView.as_view(), name='home'),
    
    path('stores/', StoreListView.as_view(), name='store_list'),
    path('store/new/', StoreCreateView.as_view(), name='store_create'),
    path('store/<int:pk>/details/', StoreDetailView.as_view(), name='store_detail'),
    path('store/<int:pk>/edit/', StoreUpdateView.as_view(), name='store_edit'),
    path('store/<int:pk>/delete/', StoreDeleteView.as_view(), name='store_delete'),
    
    path('salepoints/',SalePointListView.as_view(),name='salepoint_list'),
    path('salepoint/new/', SalePointCreateView.as_view(), name='salepoint_create'),
    path('salepoint/<int:pk>/details/', SalePointDetailView.as_view(), name='salepoint_detail'),
    path('salepoint/<int:pk>/edit/', SalePointUpdateView.as_view(), name='salepoint_edit'),
    path('salepoint/<int:pk>/delete/', SalePointDeleteView.as_view(), name='salepoint_delete'),
    
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
    path('adjustment/new/<int:item_id>/', AdjustmentCreateView.as_view(), name='adjustment_create_for_item'),
    #path('adjustment/new/<int:item_id>/', AdjustmentCreateView.as_view(), name='adjustment_create_for_item'),

   
    # Requisition URLs
    path('requisitions/', RequisitionListView.as_view(), name='requisition_list'),
    path('requisitions/new/', RequisitionCreateView.as_view(), name='requisition_create'),
    path('requisitions/<int:pk>/', RequisitionDetailView.as_view(), name='requisition_detail'),
    path('requisitions/<int:pk>/edit/', RequisitionUpdateView.as_view(), name='requisition_update'),
    path('requisitions/<int:pk>/delete/', RequisitionDeleteView.as_view(), name='requisition_delete'),
    path('requisitions/<int:pk>/approve/', RequisitionApproveView.as_view(), name='requisition_approve'),
    
    # Receiving URLS
    path('receivings/', ReceivingListView.as_view(), name='receiving_list'),
    path('receivings/new/', ReceivingCreateView.as_view(), name='receiving_create'),
    path('receivings/<int:pk>/', ReceivingDetailView.as_view(), name='receiving_detail'),
    path('receivings/<int:pk>/edit/', ReceivingUpdateView.as_view(), name='receiving_update'),
    path('receivings/<int:pk>/delete/', ReceivingDeleteView.as_view(), name='receiving_delete'),
    
    # Transfer URLs
    path('transfers/', TransferListView.as_view(), name='transfer_list'),
    path('transfers/new/', TransferCreateView.as_view(), name='transfer_create'),
    path('transfers/<int:pk>/', TransferDetailView.as_view(), name='transfer_detail'),
    path('transfers/<int:pk>/edit/', TransferUpdateView.as_view(), name='transfer_update'),
    path('transfers/<int:pk>/complete/', complete_transfer, name='transfer_complete'),

    # Issue URLs
    path('issues/', IssueListView.as_view(), name='issue_list'),
    path('issues/new/', IssueCreateView.as_view(), name='issue_create'),
    path('issues/<int:pk>/', IssueDetailView.as_view(), name='issue_detail'),
    path('issues/<int:pk>/edit/', IssueUpdateView.as_view(), name='issue_update'),
    path('issues/<int:pk>/approve/', IssueApproveView.as_view(), name='issue_approve'),
    path('issues/<int:pk>/complete/', complete_issue, name='issue_complete'),
    path('issues/<int:pk>/reject/', reject_issue, name='issue_reject'),
    
    # Add these to your urlpatterns list
    path('store/<int:pk>/add-item/', add_store_item, name='add_store_item'),
    path('store/<int:pk>/update-item/',update_store_item, name='update_store_item'),

    # AJAX URLs
    path('ajax/get-item-details/', get_item_details, name='get-item-details'),
    path('ajax/get-unit-price/', get_unit_price, name='get-unit-price'),
]