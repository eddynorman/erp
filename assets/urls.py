from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    # Asset management
    path('', views.AssetListView.as_view(), name='asset_list'),
    path('add/', views.AddAssetView.as_view(), name='add_asset'),
    path('<int:pk>/', views.AssetDetailView.as_view(), name='asset_detail'),
    path('<int:pk>/edit/', views.EditAssetView.as_view(), name='edit_asset'),
    path('<int:pk>/delete/', views.DeleteAssetView.as_view(), name='delete_asset'),
    
    # Asset purchases
    path('<int:asset_id>/purchase/add/', views.AddAssetPurchaseView.as_view(), name='add_purchase'),
    path('purchase/<int:pk>/edit/', views.EditPurchaseView.as_view(), name='edit_purchase'),
    
    # Asset status management
    path('<int:asset_id>/damage/', views.MarkDamagedView.as_view(), name='mark_damaged'),
    path('<int:asset_id>/repair/', views.RepairAssetView.as_view(), name='repair_asset'),
    path('<int:asset_id>/dispose/', views.DisposeAssetView.as_view(), name='dispose_asset'),
    
    # Asset location
    path('<int:asset_id>/location/add/', views.AddLocationView.as_view(), name='add_location'),
    
    # Asset warranty
    path('<int:asset_id>/warranty/add/', views.AddWarrantyView.as_view(), name='add_warranty'),
    
    # Asset insurance
    path('<int:asset_id>/insurance/add/', views.AddInsuranceView.as_view(), name='add_insurance'),
    
    # Maintenance management
    path('<int:asset_id>/maintenance/schedule/add/', views.AddMaintenanceScheduleView.as_view(), name='add_maintenance_schedule'),
    path('<int:asset_id>/maintenance/record/add/', views.AddMaintenanceRecordView.as_view(), name='add_maintenance_record'),
    
    # Document management
    path('<int:asset_id>/document/add/', views.AddDocumentView.as_view(), name='add_document'),
    
    # Asset transfer
    path('<int:asset_id>/transfer/', views.TransferAssetView.as_view(), name='transfer_asset'),
    
    # Reports
    path('reports/pdf/', views.GeneratePDFReportView.as_view(), name='generate_pdf_report'),
    path('reports/excel/', views.GenerateExcelReportView.as_view(), name='generate_excel_report'),
    
    # API endpoints
    path('api/asset/<int:asset_id>/details/', views.get_asset_details, name='asset_details_api'),
    path('api/maintenance/due/', views.get_maintenance_due_assets, name='maintenance_due_api'),
]