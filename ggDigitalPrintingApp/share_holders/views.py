from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import TransactionHistory, ShareHolders
from users.decorators import role_required


@login_required
@role_required(allowed_roles=['shareholder'])
def user_income(request):
    shareholder_info = ShareHolders.objects.get(username=request.user)
    transaction_history = TransactionHistory.objects.filter(user_id=shareholder_info).order_by('-transaction_date')
    paginator = Paginator(transaction_history, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    total_income = 0
    total_earned = 0

    for transaction in transaction_history:
        if transaction.transaction_type.transaction_type == 'DEBIT':
            total_income -= transaction.amount
        elif transaction.transaction_type.transaction_type == 'CREDIT':
            total_income += transaction.amount
            total_earned += transaction.amount

    return render(request, 'shareholders/user_income.html', {'transactions': page_obj, 'total_income':total_income, 'total_earned':total_earned})
