import csv
import io

from django.http import HttpResponse
from .models import Employees, EmployeeLogin
from products.models import Products
from django.shortcuts import render
from services.api import get_api

from pprint import pprint
from datetime import datetime

# Create your views here.
def insert_employees(request):
    if request.method == 'POST':
        csv_file = request.FILES['csv_file']

        # Check if the uploaded file is a CSV
        if not csv_file.name.endswith('.csv'):
            return HttpResponse('This is not a CSV file.')

        # Read the CSV file
        data_set = csv_file.read().decode('UTF-8', errors='ignore')
        io_string = io.StringIO(data_set)
        reader = csv.reader(io_string, delimiter=',', quotechar='"')

        titles = {}

        for x, row in enumerate(reader):
            if x > 0:
                emp_name = row[titles['Username']]
                salary_type = row[titles['Salary Type']]
                salary = 0
                if row[titles['Salary']] != '':
                    salary = float(row[titles['Salary']])
                products = row[titles['Product']]

                if not Employees.objects.filter(employee_name=emp_name):
                    Employees.objects.create(employee_name=emp_name, salary_type=salary_type, salary=salary, products=products)
            else:
                for y, col in enumerate(row):
                    titles[col] = y

    employees = Employees.objects.all()

    for emp in employees:
        if emp.products != '':
            for product in emp.get_products():
                print(product['productType'])

    products = Products.objects.all()
    product_list = []
    product_dict = {}

    for product in products:
        product_dict = {
            "productType": product.product_type,
            "variation1": product.variation_1,
            "variation2": product.variation_2,
            "salary": 5
        }

        product_list.append(product_dict)
        
    return render(request, 'employees/insert_employees.html')


def employee_log(request):
    asia_time = get_api('https://timeapi.io/api/time/current/zone?timeZone=Asia%2FManila')
    year = asia_time['year']
    month = asia_time['month']
    day = asia_time['day']
    hour = asia_time['hour']
    minute = asia_time['minute']
    log_type = 'Log In'

    date_string = f'{year}-{month}-{day} {hour}:{minute}'
    date_format = "%Y-%m-%d %H:%M"
    accepted_date_format = "%Y-%m-%dT%H:%M"
    date_time = datetime.strptime(date_string, date_format).strftime(accepted_date_format)
    login_time = date_time
    logout_time = ''

    log_in_time = EmployeeLogin.objects.filter(login__month=month, login__year=year)
    log_out_time = EmployeeLogin.objects.filter(logout__month=month, logout__year=year)

    if log_in_time:
        logout_time = date_time
        login_time = log_in_time[0].login.strftime(accepted_date_format)
        log_type = 'Log Out'
    
    if log_out_time:
        logout_time = log_out_time[0].logout.strftime(accepted_date_format)
        log_type = 'Today Logs'

    if request.method == "POST":
        user_id = request.user.id
        employee_account = Employees.objects.get(employee_id=user_id)

        if not log_in_time:
            EmployeeLogin.objects.create(employee_name=employee_account, login=date_time)
        elif not log_out_time:
            today_log = EmployeeLogin.objects.get(login__month=month, login__year=year)
            today_log.logout = date_time

            today_log.save()

    return render(request, 'employees/employee_log.html', {'login_time': login_time, 'logout_time': logout_time, 'log_type': log_type})
