from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.forms import UserCreationForm

from .models import *
from .forms import *

# Create your views here.

class CompanyView(generic.ListView):
    template_name = "company/index.html"
    context_object_name = "companies"

    def get_queryset(self):
        return Company.objects.all()

class CompanyCreateView(generic.CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "company/company_form.html"
    success_url = reverse_lazy("company:index")
    
class CompanyUpdateView(generic.UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = "company/company_form.html"
    success_url = reverse_lazy("company:index")
   
class BranchCreateView(generic.CreateView):
    model = Branch
    form_class = BranchForm
    template_name = "company/company_form.html"
    success_url = reverse_lazy("company:index")

class BranchUpdateView(generic.UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = "company/company_form.html"
    success_url = reverse_lazy("company:index")
   
class DepartmentCreateView(generic.CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "company/company_form.html"
    success_url = reverse_lazy("company:index")

class DepartmentUpdateView(generic.UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = "company/company_form.html"
    success_url = reverse_lazy("company:index")

class DepartmentDetailView(generic.DetailView):
    model = Department
    template_name = "company/department_detail.html"
    context_object_name = "department"

class CategoryCreateView(generic.CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "company/company_form.html"
    success_url = reverse_lazy("company:department_detail")
    
    def get_success_url(self):
        return reverse_lazy("company:department_detail", kwargs={"pk": self.object.department.id})

class CategoryUpdateView(generic.UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "company/company_form.html"
    success_url = reverse_lazy("company:department_detail")

class EmployeeListView(generic.ListView):
    model = Employee
    template_name = "company/employee_list.html"
    context_object_name = "employee_list"
    
    def get_queryset(self):
        return Employee.objects.all().filter(employee_status="Active")
    
class EmployeeCreateView(generic.CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "company/employee_form.html"
    success_url = reverse_lazy("company:employee_list")
    
class LoadDepartments(generic.View):
    def get(self, request):
        branch_id = request.GET.get('branch_id')
        departments = Department.objects.filter(branch_id=branch_id).values('id', 'department_name')
        return JsonResponse(list(departments), safe=False)
    
class EmployeeUpdateView(generic.UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "company/employee_form.html"
    success_url = reverse_lazy("company:employee_list")
    
class EmployeeDeactivateView(generic.View):
    def get(self,request, pk):
        employee = get_object_or_404(Employee,pk=pk)
        employee.deactivate_employee()
        return HttpResponseRedirect(reverse("company:employee_list"))
    
def employee_add_user(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = employee.first_name
            user.last_name = employee.last_name
            user.email = employee.employee_email
            user.save()
            employee.user = user
            employee.save()
            return redirect('company:employee_list')
    else:
        form = UserCreationForm()
    return render(request, 'company/employee_add_user.html', {'form': form, 'employee': employee})
    
# def index(request):
#     companies = Company.objects.all()
#     return render(request,"company/index.html",{"companies":companies})