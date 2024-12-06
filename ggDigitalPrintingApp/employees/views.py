import csv
import io

from django.http import HttpResponse
from .models import Employees
from products.models import Products
from django.shortcuts import render

from pprint import pprint

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
