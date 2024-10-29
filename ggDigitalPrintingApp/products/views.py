import csv
import io

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductPricesForm
from .models import Products, ProductInformation
from share_holders.models import TransactionHistory, TransactionTypeMaintenance, ShareHolders

from datetime import datetime


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
    inserted_count = 0
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

                if not ProductInformation.objects.filter(product_name=product_name, variation_name=variation_name).exists():
                    inserted_count += 1
                    product_info = ProductInformation(product_name=product_name, variation_name=variation_name,
                                                  product_type=product_type, variation_1=variation_1,
                                                  variation_2=variation_2)
                
                    product_info.save()
            else:
                for y, col in enumerate(row):
                    titles[col] = y

    return render(request, 'products/insert_product_information.html', {'product_info_menu': 'bg-gray-900 text-white', 'inserted_count': inserted_count})


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


def inser_transaction_history_data():
    # Data for Trasaction history
    data = [
        ('Jam', '11/1/2022', 5191.63),
        ('Mic', '11/1/2022', 5191.63),
        ('Jenny', '11/1/2022', 5191.63),
        ('MaryCris', '11/1/2022', 2595.81),
        ('Bane', '11/1/2022', 2595.81),
        ('Jam', '12/1/2022', 4515.84),
        ('Mic', '12/1/2022', 4515.84),
        ('Jenny', '12/1/2022', 4515.84),
        ('MaryCris', '12/1/2022', 2257.92),
        ('Bane', '12/1/2022', 2257.92),
        ('Jam', '1/1/2023', 14482.93),
        ('Mic', '1/1/2023', 14482.93),
        ('Jenny', '1/1/2023', 14482.93),
        ('MaryCris', '1/1/2023', 7241.47),
        ('Bane', '1/1/2023', 7241.47),
        ('Jam', '2/1/2023', 2987.58),
        ('Mic', '2/1/2023', 2987.58),
        ('Jenny', '2/1/2023', 2987.58),
        ('MaryCris', '2/1/2023', 1493.79),
        ('Bane', '2/1/2023', 1493.79),
        ('Jam', '3/1/2023', 3221.09),
        ('Mic', '3/1/2023', 3221.09),
        ('Jenny', '3/1/2023', 3221.09),
        ('MaryCris', '3/1/2023', 1610.54),
        ('Bane', '3/1/2023', 1610.54),
        ('Jam', '4/1/2023', 5537.42),
        ('Mic', '4/1/2023', 5537.42),
        ('Jenny', '4/1/2023', 5537.42),
        ('MaryCris', '4/1/2023', 2768.71),
        ('Bane', '4/1/2023', 2768.71),
        ('Jam', '5/1/2023', 2677.05),
        ('Mic', '5/1/2023', 2677.05),
        ('Jenny', '5/1/2023', 2677.05),
        ('MaryCris', '5/1/2023', 1338.53),
        ('Bane', '5/1/2023', 1338.53),
        ('Jam', '6/1/2023', 1645.97),
        ('Mic', '6/1/2023', 1645.97),
        ('Jenny', '6/1/2023', 1645.97),
        ('MaryCris', '6/1/2023', 822.99),
        ('Bane', '6/1/2023', 822.99),
        ('Jam', '7/1/2023', 2229.43),
        ('Mic', '7/1/2023', 2229.43),
        ('Jenny', '7/1/2023', 2229.43),
        ('MaryCris', '7/1/2023', 1114.71),
        ('Bane', '7/1/2023', 1114.71),
        ('Jam', '11/1/2023', 2936.54),
        ('Mic', '11/1/2023', 2936.54),
        ('Jenny', '11/1/2023', 2936.54),
        ('MaryCris', '11/1/2023', 1468.27),
        ('Bane', '11/1/2023', 1468.27),
        ('Jam', '12/1/2023', 3826.48),
        ('Mic', '12/1/2023', 3826.48),
        ('Jenny', '12/1/2023', 3826.48),
        ('MaryCris', '12/1/2023', 1913.24),
        ('Bane', '12/1/2023', 1913.24),
        ('Jam', '1/1/2024', 3147),
        ('Mic', '1/1/2024', 3147),
        ('Jenny', '1/1/2024', 3147),
        ('MaryCris', '1/1/2024', 1573.5),
        ('Bane', '1/1/2024', 1573.5),
        ('Jam', '2/1/2024', 5319.64),
        ('Mic', '2/1/2024', 5319.64),
        ('Jenny', '2/1/2024', 5319.64),
        ('MaryCris', '2/1/2024', 2659.82),
        ('Bane', '2/1/2024', 2659.82),
        ('Jam', '3/1/2024', 2332.79),
        ('Mic', '3/1/2024', 2332.79),
        ('Jenny', '3/1/2024', 2332.79),
        ('MaryCris', '3/1/2024', 1166.4),
        ('Bane', '3/1/2024', 1166.4),
        ('Jam', '4/1/2024', 873.14),
        ('Mic', '4/1/2024', 873.14),
        ('Jenny', '4/1/2024', 873.14),
        ('MaryCris', '4/1/2024', 436.57),
        ('Bane', '4/1/2024', 436.57),
        ('Jam', '5/1/2024', 437.02),
        ('Mic', '5/1/2024', 437.02),
        ('Jenny', '5/1/2024', 437.02),
        ('MaryCris', '5/1/2024', 218.51),
        ('Bane', '5/1/2024', 218.51),
        ('Jam', '6/1/2024', 3396.42),
        ('Mic', '6/1/2024', 3396.42),
        ('Jenny', '6/1/2024', 3396.42),
        ('MaryCris', '6/1/2024', 1698.21),
        ('Bane', '6/1/2024', 1698.21),
        ('Jam', '7/1/2024', 272.2),
        ('Mic', '7/1/2024', 272.2),
        ('Jenny', '7/1/2024', 272.2),
        ('MaryCris', '7/1/2024', 136.1),
        ('Bane', '7/1/2024', 136.1),
        ('Jam', '8/1/2024', 772.21),
        ('Mic', '8/1/2024', 772.21),
        ('Jenny', '8/1/2024', 772.21),
        ('MaryCris', '8/1/2024', 386.11),
        ('Bane', '8/1/2024', 386.11),
        ('Jam', '9/1/2024', 1094.73),
        ('Mic', '9/1/2024', 1094.73),
        ('Jenny', '9/1/2024', 1094.73),
        ('MaryCris', '9/1/2024', 547.37),
        ('Bane', '9/1/2024', 547.37)
    ]

    for col in data:
        shareholder = ShareHolders.objects.get(username=col[0])
        transaction_type = TransactionTypeMaintenance.objects.get(transaction_type='DEBIT')
        transaction_date = datetime.strptime(col[1], '%m/%d/%Y')

        TransactionHistory.objects.create(user_id=shareholder, amount=col[2], transaction_type=transaction_type,
                                          transaction_date=transaction_date, remarks='')
