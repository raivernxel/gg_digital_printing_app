from django.http import HttpResponse
from django.shortcuts import render
from .forms import OrderInformationForm
import csv
import io

# Create your views here.
def insert_products(request):
    if request.method == 'POST':
        # Get the uploaded file
        csv_file = request.FILES['csv_file']
        #insert_query = 'INSERT INTO products(product_type, stocks, variation_1, variation_2)\nVALUES\n'
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

        return render(request, 'orders/insert_products.html', {'insert_query': insert_query})

    return render(request, 'orders/insert_products.html')


def add_orders(request):
    if request.method == 'POST':
        form = OrderInformationForm(request.POST)
    else:
        form = OrderInformationForm()
    return render(request, 'orders/add_orders.html', {'form': form})
