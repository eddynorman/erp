from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from .models import (
    Expense, ExpenseCategory, ExpenseType, RecurringExpense,
    ExpenseAttachment, ExpenseComment
)
from .forms import (
    ExpenseForm, ExpenseCategoryForm, ExpenseTypeForm, RecurringExpenseForm,
    ExpenseAttachmentForm, ExpenseCommentForm, ExpenseFilterForm,
    BulkExpenseActionForm
)

@login_required
def dashboard(request):
    # Get expense statistics
    total_expenses = Expense.objects.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
    pending_expenses = Expense.objects.filter(status='submitted').count()
    this_month_expenses = Expense.objects.filter(
        date__year=timezone.now().year,
        date__month=timezone.now().month,
        status='paid'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get recent expenses
    recent_expenses = Expense.objects.all().order_by('-created_at')[:5]
    
    # Get expenses by category
    expenses_by_category = ExpenseCategory.objects.annotate(
        total_amount=Sum('expenses__amount', filter=Q(expenses__status='paid'))
    )
    
    # Get pending approvals
    pending_approvals = Expense.objects.filter(status='submitted').order_by('-created_at')[:5]
    
    context = {
        'total_expenses': total_expenses,
        'pending_expenses': pending_expenses,
        'this_month_expenses': this_month_expenses,
        'recent_expenses': recent_expenses,
        'expenses_by_category': expenses_by_category,
        'pending_approvals': pending_approvals,
    }
    return render(request, 'expenses/dashboard.html', context)

@login_required
def expense_list(request):
    expenses = Expense.objects.all()
    filter_form = ExpenseFilterForm(request.GET)
    
    if filter_form.is_valid():
        filters = filter_form.cleaned_data
        if filters['start_date']:
            expenses = expenses.filter(date__gte=filters['start_date'])
        if filters['end_date']:
            expenses = expenses.filter(date__lte=filters['end_date'])
        if filters['category']:
            expenses = expenses.filter(category=filters['category'])
        if filters['expense_type']:
            expenses = expenses.filter(expense_type=filters['expense_type'])
        if filters['status']:
            expenses = expenses.filter(status=filters['status'])
        if filters['min_amount']:
            expenses = expenses.filter(amount__gte=filters['min_amount'])
        if filters['max_amount']:
            expenses = expenses.filter(amount__lte=filters['max_amount'])
        if filters['payment_method']:
            expenses = expenses.filter(payment_method=filters['payment_method'])
    
    paginator = Paginator(expenses, 10)
    page = request.GET.get('page')
    expenses = paginator.get_page(page)
    
    bulk_form = BulkExpenseActionForm(expenses=expenses)
    
    context = {
        'expenses': expenses,
        'filter_form': filter_form,
        'bulk_form': bulk_form,
    }
    return render(request, 'expenses/expense_list.html', context)

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, 'Expense created successfully.')
            return redirect('expenses:expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm()
    
    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'title': 'Create Expense'
    })

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            expense = form.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('expenses:expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'expense': expense,
        'title': 'Edit Expense'
    })

@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    attachments = expense.attachments.all()
    comments = expense.comments.all()
    
    if request.method == 'POST':
        comment_form = ExpenseCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.expense = expense
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully.')
            return redirect('expenses:expense_detail', pk=pk)
    else:
        comment_form = ExpenseCommentForm()
    
    attachment_form = ExpenseAttachmentForm()
    
    context = {
        'expense': expense,
        'attachments': attachments,
        'comments': comments,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
    }
    return render(request, 'expenses/expense_detail.html', context)

@login_required
@permission_required('expenses.can_approve_expenses')
def expense_approve(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.approve(request.user)
    messages.success(request, 'Expense approved successfully.')
    return redirect('expenses:expense_detail', pk=pk)

@login_required
@permission_required('expenses.can_reject_expenses')
def expense_reject(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.reject()
    messages.success(request, 'Expense rejected successfully.')
    return redirect('expenses:expense_detail', pk=pk)

@login_required
def expense_submit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if expense.created_by == request.user:
        expense.submit()
        messages.success(request, 'Expense submitted for approval.')
    return redirect('expenses:expense_detail', pk=pk)

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully.')
        return redirect('expenses:expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})

@login_required
def attachment_upload(request, expense_pk):
    expense = get_object_or_404(Expense, pk=expense_pk)
    if request.method == 'POST':
        form = ExpenseAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.expense = expense
            attachment.uploaded_by = request.user
            attachment.save()
            messages.success(request, 'Attachment uploaded successfully.')
    return redirect('expenses:expense_detail', pk=expense_pk)

@login_required
def attachment_delete(request, pk):
    attachment = get_object_or_404(ExpenseAttachment, pk=pk)
    expense_pk = attachment.expense.pk
    if request.method == 'POST':
        attachment.delete()
        messages.success(request, 'Attachment deleted successfully.')
    return redirect('expenses:expense_detail', pk=expense_pk)

@login_required
def category_list(request):
    categories = ExpenseCategory.objects.all()
    return render(request, 'expenses/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('expenses:category_list')
    else:
        form = ExpenseCategoryForm()
    return render(request, 'expenses/category_form.html', {'form': form})

@login_required
def expense_type_list(request):
    expense_types = ExpenseType.objects.all()
    return render(request, 'expenses/expense_type_list.html', {'expense_types': expense_types})

@login_required
def expense_type_create(request):
    if request.method == 'POST':
        form = ExpenseTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense type created successfully.')
            return redirect('expenses:expense_type_list')
    else:
        form = ExpenseTypeForm()
    return render(request, 'expenses/expense_type_form.html', {'form': form})

@login_required
def recurring_expense_list(request):
    recurring_expenses = RecurringExpense.objects.filter(is_active=True)
    return render(request, 'expenses/recurring_expense_list.html', {'recurring_expenses': recurring_expenses})

@login_required
def recurring_expense_create(request):
    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST)
        if form.is_valid():
            recurring_expense = form.save(commit=False)
            recurring_expense.created_by = request.user
            recurring_expense.next_due_date = recurring_expense.start_date
            recurring_expense.save()
            messages.success(request, 'Recurring expense created successfully.')
            return redirect('expenses:recurring_expense_list')
    else:
        form = RecurringExpenseForm()
    return render(request, 'expenses/recurring_expense_form.html', {'form': form})

@login_required
def bulk_expense_action(request):
    if request.method == 'POST':
        form = BulkExpenseActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            expense_ids = form.cleaned_data['selected_expenses']
            expenses = Expense.objects.filter(id__in=expense_ids)
            
            if action == 'approve' and request.user.has_perm('expenses.can_approve_expenses'):
                for expense in expenses:
                    expense.approve(request.user)
                messages.success(request, f'{len(expenses)} expenses approved successfully.')
            elif action == 'reject' and request.user.has_perm('expenses.can_reject_expenses'):
                for expense in expenses:
                    expense.reject()
                messages.success(request, f'{len(expenses)} expenses rejected successfully.')
            elif action == 'delete':
                expenses.delete()
                messages.success(request, f'{len(expenses)} expenses deleted successfully.')
                
    return redirect('expenses:expense_list')
