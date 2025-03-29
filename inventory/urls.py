from django.urls import path
from .views import StoreListView, StoreCreateView, StoreUpdateView, StoreDeleteView

app_name = 'inventory'
urlpatterns = [
    path('stores/', StoreListView.as_view(), name='store_list'),
    path('store/new/', StoreCreateView.as_view(), name='store_create'),
    path('store/<int:pk>/edit/', StoreUpdateView.as_view(), name='store_edit'),
    path('store/<int:pk>/delete/', StoreDeleteView.as_view(), name='store_delete'),
]