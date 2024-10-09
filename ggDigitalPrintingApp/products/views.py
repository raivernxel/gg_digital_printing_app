import csv
import io

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductPricesForm
from .models import Products, ProductInformation


# Create your views here.
def product_prices(request):
    if request.method == 'POST':
        form = ProductPricesForm(request.POST)
        if form.is_valid():
            new_price = form.save(commit=False)
            product_id = request.POST.get('product_name')
            selected_product = get_object_or_404(Products, id=product_id)
            new_price.product_name = selected_product.product_name()
            new_price.save()
            return redirect('products:prices')
    else:
        form = ProductPricesForm()
    return render(request, 'products/product_prices.html', {'form': form, 'prices_menu': 'bg-gray-900 text-white'})


def insert_product_information(request):
    if request.method == 'POST':
        # Get the uploaded file
        csv_file = request.FILES['csv_file']
        #insert_query = 'INSERT INTO products(product_type, stocks, variation_1, variation_2)\nVALUES\n'
        insert_query = ('INSERT INTO product_information(product_name, variation_name, product_type, variation_1, '
                        'variation_2)\nVALUES\n')

        # Check if the uploaded file is a CSV
        if not csv_file.name.endswith('.csv'):
            return HttpResponse('This is not a CSV file.')

        # Read the CSV file
        data_set = csv_file.read().decode('UTF-8', errors='ignore')
        io_string = io.StringIO(data_set)
        reader = csv.reader(io_string, delimiter=',', quotechar='"')

        titles = {}

        # Process the rows in the CSV
        for x, row in enumerate(reader):
            if x > 0:
                product_name = row[titles["Product Name"]]
                variation_name = row[titles["Variation Name"]]
                product_type = row[titles["Product Type"]]
                variation_1 = row[titles["Variation 1"]]
                variation_2 = row[titles["Variation 2"]]

                product_info = ProductInformation(product_name=product_name, variation_name=variation_name,
                                                  product_type=product_type, variation_1=variation_1,
                                                  variation_2=variation_2)

                product_info.save()
            else:
                for y, col in enumerate(row):
                    titles[col] = y

    return render(request, 'products/insert_product_information.html', {'product_info_menu': 'bg-gray-900 text-white'})


def insert_products(request):
    if request.method == 'POST':
        # Get the uploaded file
        csv_file = request.FILES['csv_file']
        # insert_query = 'INSERT INTO products(product_type, stocks, variation_1, variation_2)\nVALUES\n'
        insert_query = 'INSERT INTO product_prices(product_name, material_price, price, price_last_update)\nVALUES\n'

        # Check if the uploaded file is a CSV
        if not csv_file.name.endswith('.csv'):
            return HttpResponse('This is not a CSV file.')

        # Read the CSV file
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        reader = csv.reader(io_string, delimiter=',', quotechar='"')

        # Process the rows in the CSV
        for x, row in enumerate(reader):
            if x > 0:
                product_name = f'{row[0]}:{row[7]}:{row[8]}'
                insert_query += f"('{product_name}','{row[9]}','{row[5]}','2024-01-01'),\n"
                # for y, col in enumerate(row):
                #     if y == 0:
                #         insert_query += "("
                #
                #     if y in (0, 6, 7, 8):
                #         insert_query += f"'{col}'"
                #
                #         if y < 8:
                #             insert_query += ","
                #         else:
                #             insert_query += "),\n"

        return render(request, 'products/insert_products.html', {'insert_query': insert_query, 'insert_products_menu': 'bg-gray-900 text-white'})

    return render(request, 'products/insert_products.html', {'insert_products_menu': 'bg-gray-900 text-white'})
