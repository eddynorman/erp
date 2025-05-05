from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
app_name = "company"

urlpatterns = [
    #login and logout
    path("login/",auth_views.LoginView.as_view(),name="login"),
    path("logout/",auth_views.LogoutView.as_view(),name="logout"),
    #Company
    path("",views.CompanyView.as_view(),name="index"),
    path("create", views.CompanyCreateView.as_view(),name="company_create"),
    path("<int:pk>/edit",views.CompanyUpdateView.as_view(),name="company_update"),
    #Branch
    path("<int:company_id>/branch/new",views.BranchCreateView.as_view(),name="branch_create"),
    path("<int:branch_id>/branch/edit",views.BranchUpdateView.as_view(),name="branch_update"),
    #Department
    path("<int:branch_id>/department/new",views.DepartmentCreateView.as_view(),name="department_create"),
    path("<int:department_id>/department/edit",views.DepartmentUpdateView.as_view(),name="department_update"),
    path("<int:pk>/department/detail",views.DepartmentDetailView.as_view(),name="department_detail"),
    #Category
    path("<int:dept_id>/category/new",views.CategoryCreateView.as_view(),name="category_create"),
    path("<int:category_id>/category/edit",views.CategoryUpdateView.as_view(),name="category_update"),
    #Employee
    path("employees",views.EmployeeListView.as_view(),name="employee_list"),
    path("employees/new",views.EmployeeCreateView.as_view(),name="employee_create"),
    path("employees/<int:pk>/edit",views.EmployeeUpdateView.as_view(),name="employee_update"),
    path("employees/<int:pk>/delete",views.EmployeeDeactivateView.as_view(),name="employee_delete"),
    path('ajax/load-departments/', views.LoadDepartments.as_view(), name='ajax_load_departments'),
    path('employee/<int:pk>/add_user/', views.employee_add_user, name='employee_add_user'),
]
