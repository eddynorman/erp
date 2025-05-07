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
        {'name': 'Users', 'link': '/users/', 'description': 'Manage users'},
        {'name':'Attendance', 'link': '/attendance/', 'description': 'Manage attendance'},
    ]
    return render(request, 'erp/index.html', {'apps': apps})

