from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum

from .models import TransactionHistory, ShareHolders, TransactionTypeMaintenance
from orders.models import OrderInformation, SellingPlatform, OrderList
from products.models import ProductInformation, ProductPrices
from expenses.models import Expenses, MonthlyFees, Bills
from employees.models import Employees, EmployeeLogin
from users.decorators import role_required
from services.common import get_month_and_year
from datetime import datetime, date
from .services import Products
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from .forms import TranHistForm

import json


@login_required
@role_required(allowed_roles=['shareholder', 'superuser'])
def user_income(request):
    shareholder_info = ShareHolders.objects.get(username__iexact=request.user)
    transaction_history = TransactionHistory.objects.filter(user_id=shareholder_info).order_by('-transaction_date')
    hide_name = True

    if request.user.is_superuser:
        transaction_history = TransactionHistory.objects.all().order_by('-transaction_date')
        hide_name = False

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

    return render(request, 'shareholders/user_income.html', {'transactions': page_obj, 'total_income': total_income,
                                                             'total_earned': total_earned, 'hide_name': hide_name})


def expenses(request, revenue_data):
    month = int(request.POST.get('month'))
    year = int(request.POST.get('year'))
    expenses = Expenses.objects.filter(expense_date__month=month, expense_date__year=year)
    monthly_fees = MonthlyFees.objects.filter(month=month, year=year)
    bills = Bills.objects.filter(month=month, year=year)

    expense_list = {}

    for expense in expenses:
        if expense.expense_title in expense_list:
            expense_list[expense.expense_title] += expense.amount + expense.delivery_fee
        else:
            expense_list[expense.expense_title] = expense.amount + expense.delivery_fee

    print(f'expenses_list: {expense_list}')
    revenue_data['expense_list'] = expense_list
    revenue_data['monthly_fees'] = monthly_fees
    revenue_data['bills'] = bills
    revenue_data['salary_hourly'] = salary_hourly(request)
    

def salary_hourly(request):
    month = int(request.POST.get('month'))
    year = int(request.POST.get('year'))
    employees = Employees.objects.filter(salary_type='Hourly').exclude(employee_id=0)
    salaries = {}

    for emp in employees:
        employee = Employees.objects.get(employee_id=emp.employee_id)
        empLogin = EmployeeLogin.objects.filter(login__month=month, login__year=year, employee_name=employee)

        for log in empLogin:
            if emp.employee_name in salaries:
                salaries[emp.employee_name] += emp.salary * log.hours
            else:
                salaries[emp.employee_name] = emp.salary * log.hours

    return salaries


def salary_per_item_sold(order_summary, total_orders):
    employees = Employees.objects.filter(salary_type='Item Sold')
    employee_list = []

    for employee in employees:
        prod_emp = Products(employee.employee_name, 0, employee.get_products())
        if 'Parcel' in prod_emp.products:
            print('total_orders: ', total_orders)
            prod_emp.salary += (prod_emp.products['Parcel'] * total_orders)

        employee_list.append(prod_emp)

    for product_type in order_summary.keys():
        for product_name in order_summary[product_type].keys():
            for emp_prod in employee_list:
                if product_name in emp_prod.products:
                    emp_prod.salary += (emp_prod.products[product_name] * order_summary[product_type][product_name][
                        'totalOrders'])
    
    print(f'{employee_list[0].employee_name} Salary: ', employee_list[0].salary)
    print(f'{employee_list[1].employee_name} Salary: ', employee_list[1].salary)
    print(f'{employee_list[2].employee_name} Salary: ', employee_list[2].salary)
    return employee_list


def order_list(request, order, order_summary, common):
    order_list = OrderList.objects.filter(order_id=order)

    for item in order_list:
        product_info = ProductInformation.objects.filter(product_name=item.product_name,
                                                         variation_name=item.variation_name)

        for product in product_info:
            product_name = product.get_prod_name()
            # First day of the next month. Use to get the material price based on the last update vs the order date.
            order_date = date(int(request.POST.get('year')), int(request.POST.get('month')), 1) + relativedelta(
                months=1)
            product_price = ProductPrices.objects.filter(_product_name=product_name,
                                                         price_last_update__lt=order_date).order_by(
                '-price_last_update')

            if not product_price:
                ProductPrices.objects.create(_product_name=product_name, material_price=0, price=item.deal_price,
                                             price_last_update=date(2024, 1, 1))
                common['message'] += f'Update Price: {product_name}\n'
                print(f'Update Price: {product_name}')
                continue

            if product.product_type in order_summary:
                if product_name in order_summary[product.product_type]:
                    order_summary[product.product_type][product_name]['totalOrders'] += item.quantity
                    order_summary[product.product_type][product_name]['totalProdPrice'] += (item.quantity *
                                                                                            product_price[
                                                                                                0].material_price) + (
                                                                                                       item.defect_quantity *
                                                                                                       product_price[
                                                                                                           0].material_price)
                    order_summary[product.product_type][product_name]['totalDefect'] += item.defect_quantity
                    order_summary[product.product_type][product_name]['totalReturned'] += item.returned_quantity
                else:
                    order_summary[product.product_type][product_name] = {
                        'totalOrders': item.quantity,
                        'totalProdPrice': (item.quantity * product_price[0].material_price) + (
                                    item.defect_quantity * product_price[0].material_price),
                        'totalDefect': item.defect_quantity,
                        'totalReturned': item.returned_quantity
                    }
            else:
                order_summary[product.product_type] = {
                    product_name: {
                        'totalOrders': item.quantity,
                        'totalProdPrice': (item.quantity * product_price[0].material_price) + (
                                    item.defect_quantity * product_price[0].material_price),
                        'totalDefect': item.defect_quantity,
                        'totalReturned': item.returned_quantity
                    }
                }


def income(request, common, revenue_data):
    month = int(request.POST.get('month'))
    year = int(request.POST.get('year'))
    total_income_per_platform = {}
    order_summary = {}
    total_orders = 0

    orders = OrderInformation.objects.filter(order_complete_date__month=month, order_complete_date__year=year)
    platforms = SellingPlatform.objects.all()

    if platforms:
        for platform in platforms:
            total_income_per_platform[platform.platform] = 0

    if orders:
        for order in orders:
            if order.cancelled_date is None:
                total_orders += 1
            total_income_per_platform[order.platform.platform] += order.released_amount
            revenue_data['total_sales'] += order.released_amount
            order_list(request, order, order_summary, common)

    print('total_income_per_platform: ', total_income_per_platform)

    order_summary_per_product = {}
    for prod, _ in order_summary.items():
        for prod_name, _ in order_summary[prod].items():
            if prod in order_summary_per_product:
                order_summary_per_product[prod] += order_summary[prod][prod_name]['totalProdPrice']
            else:
                order_summary_per_product[prod] = order_summary[prod][prod_name]['totalProdPrice']

    revenue_data['total_income_per_platform'] = total_income_per_platform
    revenue_data['order_summary_per_product'] = order_summary_per_product

    revenue_data['salary_per_item_sold'] = salary_per_item_sold(order_summary, total_orders)

    print('order_summary: ', order_summary)
    print('order_summary_per_product: ', order_summary_per_product)


def compute_total_revenue_and_expenses(revenue_data):
    for value in revenue_data['order_summary_per_product'].values():
        revenue_data['total_expenses'] += value

    for value in revenue_data['expense_list'].values():
        revenue_data['total_expenses'] += value

    for value in revenue_data['monthly_fees']:
        revenue_data['total_expenses'] += value.amount

    for value in revenue_data['bills']:
        revenue_data['total_expenses'] += value.amount

    for value in revenue_data['salary_per_item_sold']:
        revenue_data['total_expenses'] += value.salary

    for value in revenue_data['salary_hourly'].values():
        revenue_data['total_expenses'] += value


@login_required
@role_required(allowed_roles=['shareholder', 'superuser'])
def revenue(request):
    month = ''
    year = datetime.now().year
    superuser = request.user.is_superuser
    month_and_year = get_month_and_year()

    common = {
        'message': ''
    }
    revenue_data = {'total_sales': 0,
                    'total_expenses': 0}

    if request.method == 'POST':
        save = request.POST.get('save-revenue')

        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        income(request, common, revenue_data)
        expenses(request, revenue_data)

        compute_total_revenue_and_expenses(revenue_data)
        five_percent = revenue_data['total_sales'] * Decimal('0.05')
        revenue_data['total_expenses'] += (five_percent * 2)
        revenue_data['revenue'] = revenue_data['total_sales'] - revenue_data['total_expenses']

        revenue_data['fund'] = five_percent

        if save == 'save':
            tran_type = TransactionTypeMaintenance.objects.get(transaction_type='CREDIT')
            shareholders = ShareHolders.objects.all()
            month_text = month_and_year['months'][month]
            next_month = datetime.strptime(f'{year}-{month}-1', "%Y-%m-%d") + relativedelta(months=1)

            for sh in shareholders:
                if sh.username != 'MaryCris' and sh.username != 'Raivern':
                    revenue_per_user = (sh.share_percentage * revenue_data['revenue'])/100
                    tran_hist_per_user = TransactionHistory.objects.filter(transaction_date=next_month, remarks=f'For the month of: {month_text}', 
                                                                        transaction_type=tran_type, user_id= sh)

                    if tran_hist_per_user:
                        print('Update!')
                        tran_hist_per_user[0].amount = revenue_per_user
                        tran_hist_per_user[0].save()
                    else:
                        print('Add!')
                        TransactionHistory.objects.create(amount=revenue_per_user, transaction_date=next_month,
                                                        remarks=f'For the month of: {month_text}',user_id= sh, transaction_type=tran_type)

    month_and_year['cur_year'] = year
    month_and_year['cur_month'] = month

    return render(request, 'shareholders/revenue_page.html', {'month_and_year': month_and_year,
                                                              'revenue_menu': 'bg-gray-900 text-white',
                                                              'common': json.dumps(common),
                                                              'revenue_data': revenue_data,
                                                              'superuser': superuser})


def cash_out(request):
    user_id = request.user.username

    total_debit_amount = TransactionHistory.objects.filter(
        user_id__username=user_id,
        transaction_type__transaction_type= 'DEBIT'
    ).aggregate(total=Sum('amount'))['total']

    total_credit_amount = TransactionHistory.objects.filter(
        user_id__username=user_id,
        transaction_type__transaction_type= 'CREDIT'
    ).aggregate(total=Sum('amount'))['total']

    total_revenue = total_credit_amount - total_debit_amount

    return render(request, 'shareholders/cash_out.html', {'total_revenue':total_revenue})

@login_required
@role_required(allowed_roles=['superuser'])
def add_tran_hist(request):
    if request.method == 'POST':
        form = TranHistForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('shareholders:add-tran-hist')
        else:
            print(form.errors)
    else:
        form = TranHistForm()

    return render(request, 'shareholders/add_tran_hist.html', {'form': form})
