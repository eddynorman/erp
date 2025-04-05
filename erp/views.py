from django.shortcuts import render

def index(request):
    apps = [
        {'name': 'Company', 'link': '/company/'},
        {'name': 'Assets', 'link': '/assets/'},
        {'name': 'Inventory', 'link': '/inventory/'},
        {'name': 'Sales', 'link': '/sales/'},
        {'name': 'Expenses', 'link': '/expenses/'},
        {'name': 'Reports', 'link': '/reports/'},
    ]
    return render(request, 'erp/index.html', {'apps': apps})
