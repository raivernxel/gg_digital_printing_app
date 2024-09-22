import csv
import io

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductPricesForm
from .models import Products


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
    return render(request, 'products/product_prices.html', {'form': form})

def insert_product_information(request):
    if request.method == 'POST':
        # Get the uploaded file
        csv_file = request.FILES['csv_file']
        #insert_query = 'INSERT INTO products(product_type, stocks, variation_1, variation_2)\nVALUES\n'
        insert_query = 'INSERT INTO product_information(product_name, variation_name, product_type, variation_1, variation_2)\nVALUES\n'

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
                insert_query += f"('{row[0]}','{row[1]}','{row[2]}','{row[3]}','{row[4]}'),\n"
                product_name = {row[0]}
                variation_name = {row[1]}
            else:
                for y, col in enumerate(row):
                    titles[col] = y
                    print(col, y)

        return render(request, 'products/insert_product_information.html', {'insert_query': insert_query})

    return render(request, 'products/insert_product_information.html')