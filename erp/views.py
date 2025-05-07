from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    apps = [
        {'name': 'Company', 'link': '/company/', 'description': 'Manage company information'},
        {'name': 'Assets', 'link': '/assets/', 'description': 'Manage assets'},
        {'name': 'Inventory', 'link': '/inventory/', 'description': 'Manage inventory'},
        {'name': 'Sales', 'link': '/sales/', 'description': 'Manage sales'},
        {'name': 'Expenses', 'link': '/expenses/', 'description': 'Manage expenses'},
        {'name': 'Reports', 'link': '/reports/', 'description': 'Manage reports'},
    ]
    return render(request, 'erp/index.html', {'apps': apps})

@login_required
def sales_dashboard(request):
    return render(request, 'erp/sales_dashboard.html')

@login_required
def reports_dashboard(request):
    return render(request, 'erp/reports_dashboard.html')

@login_required
def users_dashboard(request):
    return render(request, 'erp/users_dashboard.html')
