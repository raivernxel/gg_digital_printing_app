from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import TransactionHistory, ShareHolders
from orders.models import OrderInformation, SellingPlatform, OrderList
from products.models import ProductInformation, ProductPrices
from expenses.models import Expenses, MonthlyFees, Bills
from employees.models import Employees
from users.decorators import role_required
from services.common import get_month_and_year
from datetime import datetime, date
from .services import Products
from dateutil.relativedelta import relativedelta
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

    salary_per_item_sold(order_summary, total_orders)

    order_summary_per_product = {}
    for prod, _ in order_summary.items():
        for prod_name, _ in order_summary[prod].items():
            if prod in order_summary_per_product:
                order_summary_per_product[prod] += order_summary[prod][prod_name]['totalProdPrice']
            else:
                order_summary_per_product[prod] = order_summary[prod][prod_name]['totalProdPrice']

    revenue_data['total_income_per_platform'] = total_income_per_platform
    revenue_data['order_summary_per_product'] = order_summary_per_product

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


@login_required
@role_required(allowed_roles=['shareholder', 'superuser'])
def revenue(request):
    month = ''
    year = datetime.now().year
    common = {
        'message': ''
    }
    revenue_data = {'total_sales': 0,
                    'total_expenses': 0}

    if request.method == 'POST':
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        income(request, common, revenue_data)
        expenses(request, revenue_data)

        compute_total_revenue_and_expenses(revenue_data)
        revenue_data['revenue'] = revenue_data['total_sales'] - revenue_data['total_expenses']

    month_and_year = get_month_and_year()
    month_and_year['cur_year'] = year
    month_and_year['cur_month'] = month

    print('total_expenses: ', revenue_data['total_expenses'])

    return render(request, 'shareholders/revenue_page.html', {'month_and_year': month_and_year,
                                                              'revenue_menu': 'bg-gray-900 text-white',
                                                              'common': json.dumps(common),
                                                              'revenue_data': revenue_data})
