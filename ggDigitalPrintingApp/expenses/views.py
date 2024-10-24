from datetime import datetime
from django.shortcuts import render, redirect
from .forms import ExpensesForm
from .models import MonthlyFeeMaintenance, MonthlyFees


# Create your views here.
def add_expenses(request):
    if request.method == 'POST':
        form = ExpensesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            return redirect('expenses:add-expenses')
    else:
        form = ExpensesForm()
    
    return render(request, 'expenses/add_expenses.html', {'form': form, 'add_expenses_menu': 'bg-gray-900 text-white'})


def monthly_fees(request):
    monthly_fee_list = MonthlyFeeMaintenance.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save':
            month = request.POST.get('month')
            year = request.POST.get('year')

            for monthly_fee in monthly_fee_list:
                title = monthly_fee.title
                amount = request.POST.get(f'amount_{monthly_fee.title}')

                if monthly_fee.amount != amount:
                    monthly_fee_maintenance = MonthlyFeeMaintenance.objects.get(title=title)
                    monthly_fee_maintenance.amount = amount
                    monthly_fee_maintenance.save()

                if request.POST.get(monthly_fee.title):
                    if MonthlyFees.objects.filter(title=title, month=month, year=year).exists():
                        monthly_fee = MonthlyFees.objects.get(month=month, year=year, title=title)

                        if amount:
                            monthly_fee.amount = amount
                            monthly_fee.save()
                    else:
                        MonthlyFees.objects.create(month=month, year=year, title=title, amount=amount)
                else:
                    if MonthlyFees.objects.filter(month=month, year=year, title=title).exists():
                        monthly_fee = MonthlyFees.objects.get(month=month, year=year, title=title)

                        monthly_fee.delete()
        else:
            new_title = request.POST.get('new_title')
            new_amount = request.POST.get('new_amount')

            if new_title and new_amount:
                MonthlyFeeMaintenance.objects.create(title=new_title, amount=new_amount)


        return redirect('expenses:monthly-fees')


    year_range = range(2022, datetime.now().year+1)
    cur_year = datetime.now().year
    cur_month = datetime.now().month
    months = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }

    return render(request, 'expenses/monthly_fees.html', {'monthly_fees_menu': 'bg-gray-900 text-white', 
                                                          'year_range': year_range, 'cur_year': cur_year, 'cur_month': cur_month,
                                                          'months': months, 'monthly_fee_list': monthly_fee_list})
