import csv
import io

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductPricesForm
from .models import Products, ProductInformation
from share_holders.models import TransactionHistory, TransactionTypeMaintenance, ShareHolders
from dateutil.relativedelta import relativedelta

from datetime import datetime


def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
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


@user_passes_test(is_admin)
def insert_product_information(request):
    # insert_single_transaction_history(request)
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


@user_passes_test(is_admin)
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


@user_passes_test(is_admin)
def insert_single_transaction_history(request):
    shareholder = ShareHolders.objects.get(username='Bane')
    transaction_type = TransactionTypeMaintenance.objects.get(transaction_type='DEBIT')
    transaction_date = datetime.strptime('11/17/2024', '%m/%d/%Y')

    TransactionHistory.objects.create(user_id=shareholder, amount=3562.88, transaction_type=transaction_type,
                                        transaction_date=transaction_date, remarks=f'Payment for the Cebu Pacific Tickets.')


@user_passes_test(is_admin)
def insert_transaction_history_data():
    # Data for Trasaction history
    # DEBIT
    # data = [
    #     ['MaryCris', 4379.25, 'CASH', '04/15/2023', 'Month - Feb, March'],
    #     ['MaryCris', 1482, 'CASH', '05/07/2023', 'Month - April'],
    #     ['Jenny', 3824, 'BANK', '08/04/2023', 'Month - Less to April, May, June'],
    #     ['Jam', 4544.17, 'GCASH', '12/12/2022', ''],
    #     ['Jam', 5117.84, 'GCASH', '11/01/2022', ''],
    #     ['Mic', 6208.67, 'GCASH', '03/15/2023', ''],
    #     ['Mic', 5537.42, 'GCASH', '04/07/2023', ''],
    #     ['Jam', 5000, 'BANK', '11/06/2023', 'Month - October'],
    #     ['MaryCris', 6070, 'CASH', '12/20/2023', 'Month - June, September, October, November'],
    #     ['Jam', 2937, 'BANK', '11/06/2023', 'Month - September'],
    #     ['Mic', 2963.46, 'GCASH', '05/05/2023', 'Month - April'],
    #     ['Mic', 3205.93, 'GCASH', '03/18/2024', 'Month - January, February (Paid to Condo)'],
    #     ['Mic', 2229.43, 'GCASH', '07/03/2023', 'Month - June'],
    #     ['Mic', 4617, 'MAYA', '12/18/2022', ''],
    #     ['Jenny', 14482.93, 'SEABANK', '01/02/2023', ''],
    #     ['MaryCris', 7241.47, 'CASH', '01/07/2023', ''],
    #     ['MaryCris', 2257.92, 'CASH', '12/17/2022', ''],
    #     ['MaryCris', 1493.79, 'CASH', '02/04/2023', ''],
    #     ['Jenny', 6763, 'BANK', '11/09/2023', 'Month - September, October'],
    #     ['MaryCris', 822.99, 'GCASH', '06/05/2023', 'Month - May'],
    #     ['Bane', 1482, 'MAYA', '05/07/2023', 'Month - April'],
    #     ['Mic', 3396.42, 'BANK', '05/14/2024', 'Month - April (Payed in Condo)'],
    #     ['Jenny', 4617, 'SEABANK', '12/18/2022', ''],
    #     ['Bane', 4955, 'GCASH', '12/07/2023', 'Month - September, October, November'],
    #     ['Bane', 1493.79, 'CASH', '02/04/2023', ''],
    #     ['Jenny', 11746.09, 'PNB', '04/03/2023', '3 Months Salary (Jan, Feb, March)'],
    #     ['Jam', 2000, 'GCASH', '12/07/2023', 'Month - November'],
    #     ['Jenny', 5142.84, 'SEABANK', '11/04/2022', ''],
    #     ['Jam', 73.39, 'GCASH', '12/12/2022', ''],
    #     ['Bane', 436.57, 'GCASH', '03/04/2024', 'Month - February'],
    #     ['Jenny', 5319.64, 'GCASH', '01/05/2024', 'Month - December'],
    #     ['Mic', 6763, 'GCASH', '11/09/2023', 'Month - September, October'],
    #     ['Jenny', 3206, 'GCASH', '03/15/2024', 'Month - January, February'],
    #     ['Bane', 1166, 'GCASH', '02/27/2024', 'Month - January'],
    #     ['Bane', 2257.92, 'CASH', '12/17/2022', ''],
    #     ['Jam', 14483, 'GCASH', '01/07/2023', ''],
    #     ['Mic', 8467, 'BANK', '01/05/2024', 'Month - November, December'],
    #     ['Jam', 11746.09, 'CASH', '04/18/2023', '3 Months Salary (Jan, Feb, March)'],
    #     ['Mic', 5117.84, 'MAYA', '11/02/2022', ''],
    #     ['Jenny', 2728.45, 'BANK', '07/29/2023', 'Month - Less to April, May, June'],
    #     ['MaryCris', 2595.81, 'CASH', '11/05/2022', ''],
    #     ['Bane', 1937.7, 'CASH', '07/04/2023', 'Month - May, June'],
    #     ['Mic', 437.02, 'MAYA', '04/17/2024', 'Month - March'],
    #     ['Jenny', 4105.64, 'BANK', '06/04/2024', 'Month - March, April, May'],
    #     ['Bane', 2659.82, 'GCASH', '01/05/2024', 'Month - December'],
    #     ['Mic', 1646, 'GCASH', '06/08/2023', 'Month - May'],
    #     ['Jenny', 1867, 'BANK', '08/27/2024', 'Month - June, July'],
    #     ['Jenny', 3147, 'GCASH', '12/08/2023', 'Month - November'],
    #     ['Bane', 7241.47, 'CASH', '01/07/2023', ''],
    #     ['Jam', 6552.45, 'CASH', '07/07/2023', 'Month - April, May, June'],
    #     ['Mic', 14482.93, 'MAYA', '01/01/2023', ''],
    #     ['Bane', 2595.81, 'MAYA', '11/04/2022', 'For the month of: October'],
    #     ['Bane', 4379.25, 'CASH', '11/04/2022', 'For the month of: February, March'],
    #     ['Jam', 5319.64, 'CASH', '01/04/2024', 'For the month of: December']
    # ]

    # CREDIT
    data = [
        ('Jam', '11/1/2022', 5142.84),
        ('Mic', '11/1/2022', 5117.84),
        ('Jenny', '11/1/2022', 5117.84),
        ('MaryCris', '11/1/2022', 2595.81),
        ('Bane', '11/1/2022', 2595.81),
        ('Jam', '12/1/2022', 4617),
        ('Mic', '12/1/2022', 4617),
        ('Jenny', '12/1/2022', 4617),
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
        ('Jam', '5/1/2023', 2963.46),
        ('Mic', '5/1/2023', 2963.46),
        ('Jenny', '5/1/2023', 2963.46),
        ('MaryCris', '5/1/2023', 1482),
        ('Bane', '5/1/2023', 1482),
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
        ('Jam', '10/1/2023', 2936.54),
        ('Mic', '10/1/2023', 2936.54),
        ('Jenny', '10/1/2023', 2936.54),
        ('MaryCris', '10/1/2023', 1468.27),
        ('Bane', '10/1/2023', 1468.27),
        ('Jam', '11/1/2023', 3826.48),
        ('Mic', '11/1/2023', 3826.48),
        ('Jenny', '11/1/2023', 3826.48),
        ('MaryCris', '11/1/2023', 1913.24),
        ('Bane', '11/1/2023', 1913.24),
        ('Jam', '12/1/2023', 3147),
        ('Mic', '12/1/2023', 3147),
        ('Jenny', '12/1/2023', 3147),
        ('MaryCris', '12/1/2023', 1573.5),
        ('Bane', '12/1/2023', 1573.5),
        ('Jam', '1/1/2024', 5319.64),
        ('Mic', '1/1/2024', 5319.64),
        ('Jenny', '1/1/2024', 5319.64),
        ('MaryCris', '1/1/2024', 2659.82),
        ('Bane', '1/1/2024', 2659.82),
        ('Jam', '2/1/2024', 2332.79),
        ('Mic', '2/1/2024', 2332.79),
        ('Jenny', '2/1/2024', 2332.79),
        ('MaryCris', '2/1/2024', 1166.4),
        ('Bane', '2/1/2024', 1166.4),
        ('Jam', '3/1/2024', 873.14),
        ('Mic', '3/1/2024', 873.14),
        ('Jenny', '3/1/2024', 873.14),
        ('MaryCris', '3/1/2024', 436.57),
        ('Bane', '3/1/2024', 436.57),
        ('Jam', '4/1/2024', 437.02),
        ('Mic', '4/1/2024', 437.02),
        ('Jenny', '4/1/2024', 437.02),
        ('MaryCris', '4/1/2024', 218.51),
        ('Bane', '4/1/2024', 218.51),
        ('Jam', '5/1/2024', 3396.42),
        ('Mic', '5/1/2024', 3396.42),
        ('Jenny', '5/1/2024', 3396.42),
        ('MaryCris', '5/1/2024', 1698.21),
        ('Bane', '5/1/2024', 1698.21),
        ('Jam', '6/1/2024', 272.2),
        ('Mic', '6/1/2024', 272.2),
        ('Jenny', '6/1/2024', 272.2),
        ('MaryCris', '6/1/2024', 136.1),
        ('Bane', '6/1/2024', 136.1),
        ('Jam', '7/1/2024', 772.21),
        ('Mic', '7/1/2024', 772.21),
        ('Jenny', '7/1/2024', 772.21),
        ('MaryCris', '7/1/2024', 386.11),
        ('Bane', '7/1/2024', 386.11),
        ('Jam', '8/1/2024', 1094.73),
        ('Mic', '8/1/2024', 1094.73),
        ('Jenny', '8/1/2024', 1094.73),
        ('MaryCris', '8/1/2024', 547.37),
        ('Bane', '8/1/2024', 547.37)
    ]

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

    # For Credit
    for col in data:
        shareholder = ShareHolders.objects.get(username=col[0])
        transaction_type = TransactionTypeMaintenance.objects.get(transaction_type='CREDIT')
        transaction_date = datetime.strptime(col[1], '%m/%d/%Y')
        month_of = transaction_date - relativedelta(months=1)

        TransactionHistory.objects.create(user_id=shareholder, amount=col[2], transaction_type=transaction_type,
                                          transaction_date=transaction_date, remarks=f'For the month of: {months[month_of.month]}')

    # For Debit
    # for col in data:
    #     shareholder = ShareHolders.objects.get(username=col[0])
    #     transaction_type = TransactionTypeMaintenance.objects.get(transaction_type='DEBIT')
    #     transaction_date = datetime.strptime(col[3], '%m/%d/%Y')
    #
    #     TransactionHistory.objects.create(user_id=shareholder, amount=col[1], transaction_type=transaction_type,
    #                                       transaction_date=transaction_date, remarks=col[4],
    #                                       transaction_platform=col[2])
