import pandas as pd
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from .forms import OrderInformationForm
from .models import OrderInformation, Logistics, OrderStatus, SellingPlatform, OrderList
from datetime import datetime
from decouple import config
from api.services import get_trello_api_data
import csv, io, requests


# Create your views here.
def add_orders(request):
    if request.method == 'POST':
        form = ""
        data_file = request.FILES.get('data_file')

        if data_file:
            # Read the Excel file using pandas
            try:
                # Read all sheets from the Excel file into a dictionary of DataFrames
                excel_data = pd.read_excel(data_file, sheet_name=None)

                # Create a dictionary of data by column from the Shopee's Excel file.
                data_dict = {}
                for sheet_name, df in excel_data.items():
                    column_arrays = {}
                    for column_name in df.columns:
                        column_arrays[column_name] = df[column_name].tolist()
                    data_dict[sheet_name] = column_arrays

                prev_order_id = ""
                order_information = OrderInformation()

                for x in range(len(data_dict['orders']['Order ID'])):
                    order_id = data_dict['orders']['Order ID'][x]

                    if prev_order_id != order_id:
                        username = data_dict['orders']['Username (Buyer)'][x]
                        delivery_address = data_dict['orders']['Delivery Address'][x]
                        city = data_dict['orders']['City'][x]
                        province = data_dict['orders']['Province'][x]
                        tracking_number = check_nan(str(data_dict['orders']['Tracking Number*'][x]))
                        shipping_option = shipping_update(data_dict['orders']['Shipping Option'][x])

                        order_status = "Delivered"
                        if data_dict['orders']['Order Status'][x] != "Completed":
                            order_status = data_dict['orders']['Order Status'][x]

                        cancel_reason = check_nan(str(data_dict['orders']['Cancel reason'][x]))
                        refund_status = check_nan(str(data_dict['orders']['Return / Refund Status'][x]))
                        platform = "SHOPEE"
                        artist_cut = 0  # Update this in the future for the Artist's cut!!!
                        order_creation_date = datetime.strptime(
                                              data_dict['orders']['Order Creation Date'][x], "%Y-%m-%d %H:%M").date()

                        logistics = Logistics.objects.get(logistic_name=shipping_option)
                        order_status = OrderStatus.objects.get(status_type=order_status)
                        selling_platform = SellingPlatform.objects.get(platform=platform)
                        order_information = OrderInformation(order_id=order_id, username=username,
                                                             delivery_address=delivery_address, city=city,
                                                             province=province, tracking_number=tracking_number,
                                                             shipping_option=logistics, order_status=order_status,
                                                             cancel_reason=cancel_reason, refund_status=refund_status,
                                                             platform=selling_platform, artist_cut=artist_cut,
                                                             order_creation_date=order_creation_date)

                        order_information.save()

                    prev_order_id = order_id

                    product_name = data_dict['orders']['Product Name'][x]
                    variation_name = check_nan(str(data_dict['orders']['Variation Name'][x]))
                    original_price = data_dict['orders']['Original Price'][x]
                    deal_price = data_dict['orders']['Deal Price'][x]
                    quantity = data_dict['orders']['Quantity'][x]
                    returned_quantity = data_dict['orders']['Returned quantity'][x]
                    sku = check_nan(str(data_dict['orders']['Parent SKU Reference No.'][x]))

                    existing_order = OrderList.objects.filter(
                        order_id=order_id,
                        product_name=product_name,
                        variation_name=variation_name
                    ).exists()

                    if not existing_order:
                        order_list = OrderList(order_id=order_information, product_name=product_name,
                                           variation_name=variation_name, original_price=original_price,
                                           deal_price=deal_price, quantity=quantity,
                                           returned_quantity=returned_quantity, sku=sku)

                        order_list.save()

                    # print(data_dict['orders']['Order ID'][x])
                    # initial_data = {
                    #     'order_id': data_dict['orders']['Order ID'][x],
                    #     'username': data_dict['orders']['Username (Buyer)'][x],
                    #     'delivery_address': data_dict['orders']['Delivery Address'][x]
                    # }
                    # break

                # form = OrderInformationForm(initial=initial_data)
                # return render(request, 'orders/add_orders.html', {'form': form})

            except Exception as e:
                return HttpResponse(f"Error processing file: {e}")

            # Process the rows in the CSV
            # for x, row in enumerate(reader):
            #     if x > 0:
            #         continue
            #         # product_name = row[titles["Product Name"]]
            #         # variation_name = row[titles["Variation Name"]]
            #         # product_type = row[titles["Product Type"]]
            #         # variation_1 = row[titles["Variation 1"]]
            #         # variation_2 = row[titles["Variation 2"]]
            #         #
            #         # product_info = ProductInformation(product_name=product_name, variation_name=variation_name,
            #         #                                   product_type=product_type, variation_1=variation_1,
            #         #                                   variation_2=variation_2)
            #         #
            #         # product_info.save()
            #     else:
            #         for y, col in enumerate(row):
            #             print(col)
            #             titles[col] = y
        else:
            form = OrderInformationForm(request.POST)
    else:
        form = OrderInformationForm()
    return render(request, 'orders/add_orders.html', {'form': form, 'add_orders_menu': 'bg-gray-900 text-white'})


def orders(request):
    order_info = OrderInformation.objects.all().order_by('order_creation_date')
    paginator = Paginator(order_info, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    order_list = {}

    for order in order_info:
        order_list[order.order_id] = OrderList.objects.filter(order_id=order.order_id)

    return render(request, 'orders/orders.html', {'orders_menu': 'bg-gray-900 text-white',
                                                  'order_info': page_obj, 'order_list': order_list})


def trello_update(request):
    api_data = get_trello_api_data('https://api.trello.com/1/lists/5e5a0b8ad17ff766f0169719/cards?')
    logistics = Logistics.objects.all()
    platform = SellingPlatform.objects.all()

    return render(request, 'orders/trello_update.html', {'trello_update_menu': 'bg-gray-900 text-white', 'logistics': logistics, 'platforms': platform})


def check_nan(field):
    if field == "nan":
        return ''

    return field


def shipping_update(field):
    field = field.replace("Standard Local", "").replace("-", "")

    if field == "":
        field = "Others"

    return field
