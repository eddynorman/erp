from django.urls import path
from  .views import *

app_name = 'assets'
urlpatterns = [
    path('', AssetListView.as_view(), name='asset_list'),
    path('<int:pk>/', AssetDetailView.as_view(), name='asset_detail'),
    path('add/', AddAssetView.as_view(), name='add_asset'),
    path('<int:asset_id>/purchase/', AddAssetPurchaseView.as_view(), name='add_asset_purchase'),
    path('<int:purchase_id>/edit/', EditPurchaseView.as_view(), name='edit_purchase'),
    path('<int:asset_id>/damaged/', MarkDamagedView.as_view(), name='mark_damaged'),
    path('<int:asset_id>/repair/', RepairAssetView.as_view(), name='repair_asset'),
    path('<int:asset_id>/dispose/', DisposeAssetView.as_view(), name='dispose_asset'),
    path("report/general/pdf/", GeneratePDFReportView.as_view(), name="general_pdf_report"),
    path("report//general/excel/", GenerateExcelReportView.as_view(), name="general_excel_report"),
    
]