import pandas as pd
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import F
from django.http import JsonResponse
from .forms import OrderInformationForm
from .models import OrderInformation, Logistics, OrderStatus, SellingPlatform, OrderList, OrderMaintenance
from .utils import extract_order_data
from products.models import ProductInformation, ProductTypes, ProductPrices
from datetime import datetime
from decouple import config
from services.api import get_trello_api_data, update_trello_api_data
from services.common import get_trello_id, get_trello_id_count
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
    order_info = OrderInformation.objects.all().order_by('-order_creation_date')
    paginator = Paginator(order_info, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    order_list = {}

    for order in order_info:
        order_list[order.order_id] = OrderList.objects.filter(order_id=order.order_id)

    return render(request, 'orders/orders.html', {'orders_menu': 'bg-gray-900 text-white',
                                                  'order_info': page_obj, 'order_list': order_list})


def trello_update(request):
    printed_orders = get_trello_api_data(f'https://api.trello.com/1/lists/{config('TRELLO_MOUSEPAD_PRINTED_ID')}/cards?')

    if printed_orders:
        return trello_update3(request)
    else:
        return trello_update2(request)

def trello_update1(request):
    if request.method == 'POST':
        order_data = extract_order_data(request)
        
        get_card_url = f'https://api.trello.com/1/cards/{order_data['trello_card_id']}'

        desc = (f'{order_data['list_of_orders']}\n'
                f'Address: {order_data['address']}\n'
                f'City: {order_data['city']}\n'
                f'Region: {order_data['region']}\n'
                f'Zip Code: {order_data['postal_code']}\n'
                f'Name: {order_data['first_name']} {['surname']}\n'
                f'Contact Number: {order_data['contact_number']}\n'
                f'Email: {order_data['email']}\n\n'
                f'Paid Amount: {order_data['released_amount']}\n'
                f'Delivery Fee: {order_data['delivery_fee']}\n\n'
                f'Tracking Number: {order_data['tracking_number']}\n')
        
        params = {
            'desc': desc,
            'idList': config('TRELLO_MOUSEPAD_FOR_DELIVERY_ID')
        }
        
        update_trello_api_data(get_card_url, params)

    order_data = get_trello_api_data(f'https://api.trello.com/1/lists/{config('TRELLO_MOUSEPAD_PRINTED_ID')}/cards?')

    logistics = Logistics.objects.all()
    platform = SellingPlatform.objects.all()
    product_info = ProductInformation.objects.filter(product_name=F('product_type'))
    product_types = ProductTypes.objects.all()

    if len(order_data) > 0:
        for label in order_data[0]['labels']:
            if label['color'] == 'orange':
                order_data[0]['logistic'] = label['name']

        if order_data[0]['start'] != None:
            order_data[0]['start'] = datetime.fromisoformat(order_data[0]['start'].replace("Z", ""))

        order_data = order_data[0]

    return render(request, 'orders/trello_update.html', {'trello_update_menu': 'bg-gray-900 text-white', 
                                                         'logistics': logistics, 'platforms': platform, 'product_info': product_info,
                                                         'product_types': product_types, 'trello_data': order_data})


def trello_update2(request):
    if request.method == 'POST':
        order_data = extract_order_data(request)

        if not OrderInformation.objects.filter(order_id=order_data['trello_id']).exists():
            order_info = OrderInformation(order_id=order_data['trello_id'], username=order_data['username'], delivery_address=order_data['address'], city=order_data['city'],
                                        province=order_data['region'], tracking_number=order_data['tracking_number'], shipping_option=order_data['logistics'],
                                        order_status=order_data['order_status'], released_amount=order_data['released_amount'], cancel_reason="",
                                        refund_status="", platform=order_data['platform'], delivery_fee=order_data['delivery_fee'], order_creation_date=order_data['order_date'],
                                        order_complete_date=order_data['delivered_date'])
            
            order_info.save()

        # Mousepad : 60x35 Printed Edge : 4pc(s) x 450.00 : 0 : 0
        for order in order_data['list_of_orders'].split('\n'):
            break_down = order.split(' : ')
            if len(break_down) == 5:
                product_name = break_down[0]
                variation_name = break_down[1]
                quantity = int(break_down[2].split('pc(s) x ')[0])
                price = float(break_down[2].split('pc(s) x ')[1])
                returned = int(break_down[3])
                defect = int(break_down[4])

                product_info = ProductInformation.objects.get(product_name=product_name, variation_name=variation_name)
                product_price = ProductPrices.objects.get(_product_name=product_info.get_prod_name()).price

                order_info = OrderInformation.objects.get(order_id=order_data['trello_id'])

                if not OrderList.objects.filter(order_id=order_info, product_name=product_name, variation_name=variation_name).exists():
                    order_list = OrderList(order_id=order_info, product_name=product_name, variation_name=variation_name,
                                        original_price=product_price, deal_price=price, quantity=quantity, returned_quantity=returned,
                                        defect_quantity=defect, sku="")
                    
                    order_list.save()
        
        get_card_url = f'https://api.trello.com/1/cards/{order_data['trello_card_id']}'
        first_pos = get_trello_api_data(f'https://api.trello.com/1/lists/{config('TRELLO_MOUSEPAD_DELIVERED_ID')}/cards?')[0]['pos']
        
        params = {
            'name': f'{order_data['username']} {order_data['trello_id']}',
            'pos' : first_pos - 1,
            'idList' : config('TRELLO_MOUSEPAD_DELIVERED_ID')
        }
        
        update_trello_api_data(get_card_url, params)

        # Increment trello id
        trello_id_count = OrderMaintenance.objects.get(name='trello_id_count')
        trello_id_count.value = int(trello_id_count.value) + 1
        trello_id_count.save()

    orders = get_trello_api_data(f'https://api.trello.com/1/lists/{config('TRELLO_MOUSEPAD_DONE_ID')}/cards?')

    logistics = Logistics.objects.all()
    platform = SellingPlatform.objects.all()
    product_info = ProductInformation.objects.filter(product_name=F('product_type'))
    product_types = ProductTypes.objects.all()

    if orders:
        order = orders[-1]
        for x, fields in enumerate(order['desc'].split('\n\n')):
            if x == 0:
                order['desc'] = fields
            else:
                for values in fields.split('\n'):
                    value = values.split(': ')
                    if value[0] == 'Name':
                        order['first_name'] = ""
                        full_name = value[1].split(' ')
                        for y, name in enumerate(full_name):
                            if y < len(full_name) - 1:
                                order['first_name'] += f'{name} '
                            else:
                                order['last_name'] = name
                    else:
                        order[value[0].replace(' ', '_').lower()] = "" if len(value) < 2 else value[1] 

        for label in order['labels']:
            if label['color'] == 'orange':
                order['logistic'] = label['name']

        if order['start'] != None:
            order['start'] = datetime.fromisoformat(order['start'].replace("Z", ""))

        if order['due'] != None:
            order['due'] = datetime.fromisoformat(order['due'].replace("Z", ""))

    return render(request, 'orders/trello_update.html', {'trello_update_menu': 'bg-gray-900 text-white', 
                                                         'logistics': logistics, 'platforms': platform, 'product_info': product_info,
                                                         'product_types': product_types, 'trello_data': order})

def trello_update3(request):
    if request.method == 'POST':
        trello_id_count = OrderMaintenance.objects.get(name='trello_id_count').value
        trello_card_id = request.POST.get('card_id')
        username = request.POST.get('usernames')
        list_of_orders = request.POST.get('list_of_orders')
        address = request.POST.get('address')
        city = request.POST.get('city')
        region = request.POST.get('region')
        postal_code = request.POST.get('postal_code')
        first_name = request.POST.get('first_name')
        surname = request.POST.get('last_name')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        released_amount = request.POST.get('released_amount')
        delivery_fee = request.POST.get('delivery_fee')

        logistics = request.POST.get('logistics')
        tracking_number = request.POST.get('tracking_number')
        platform = request.POST.get('platform')

        order_info = OrderInformation()
        
        get_card_url = f'https://api.trello.com/1/cards/{trello_card_id}'

        desc = (f'{list_of_orders}\n'
                f'Address: {address}\n'
                f'City: {city}\n'
                f'Region: {region}\n'
                f'Zip Code: {postal_code}\n'
                f'Name: {first_name} {surname}\n'
                f'Contact Number: {contact_number}\n'
                f'Email: {email}\n\n'
                f'Paid Amount: {released_amount}\n'
                f'Delivery Fee: {delivery_fee}\n\n'
                f'Tracking Number: {tracking_number}\n')
        
        params = {
            'desc': desc,
            'name': username
        }
        
        update_trello_api_data(get_card_url, params)

    orders = get_trello_api_data(f'https://api.trello.com/1/lists/{config('TRELLO_MOUSEPAD_PRINTED_ID')}/cards?')
    order = []

    logistics = Logistics.objects.all()
    platform = SellingPlatform.objects.all()
    product_info = ProductInformation.objects.filter(product_name=F('product_type'))
    product_types = ProductTypes.objects.all()

    for ord in orders:
        if not ord['desc'].startswith('Mousepad : '):
            order = ord
            break

    # Mousepad : 60x35 Printed Edge : 1pc(s) x 450.00 : 0 : 0 -- Order Format
    if len(order) > 0:
        released_amount = 0
        orderDesc = ''
        order['delivery_fee'] = 0
        for x, desc in enumerate(order['desc'].split('\n\n')):
            if x == 0:
                for field in desc.split('\n'):
                    field = field.replace('white', 'Printed Edge').replace('black', 'Black Edge').replace('no stitch', 'No Stitch')

                    for y, value in enumerate(field.split(' : ')):
                        if y == 0:
                            orderDesc += f'Mousepad : {value} : '
                        elif y == 1:
                            value = value.replace('pcs', '').replace('pc', '').replace(' x', '')
                            price = value.split(" ")
                            orderDesc += f'{price[0]}pc(s) x {price[1]}.00 : 0 : 0\n'
                            released_amount += (int(price[0]) * int(price[1]))
            else:
                for field in desc.split('\n'):
                    fieldValues = field.split(' : ')
                    if fieldValues[0].startswith('Address'):
                        order['address'] = fieldValues[1].replace('N/A', '')
                    elif fieldValues[0].startswith('Delivery Fee'):
                        order['delivery_fee'] = fieldValues[1]
                    elif fieldValues[0].startswith('Name'):
                        order['first_name'] = fieldValues[1]
                    elif fieldValues[0].startswith('Contact'):
                        order['contact'] = fieldValues[1]
        
        order['old_desc'] = order['desc']
        order['desc'] = orderDesc
        order['paid_amount'] = released_amount

        for label in order['labels']:
            if label['color'] == 'orange':
                order['logistic'] = label['name']

        if order['start'] != None:
            order['start'] = datetime.fromisoformat(order['start'].replace("Z", ""))

    return render(request, 'orders/trello_update.html', {'trello_update_menu': 'bg-gray-900 text-white', 
                                                         'logistics': logistics, 'platforms': platform, 'product_info': product_info,
                                                         'product_types': product_types, 'trello_data': order})


def load_var_names(request):
    prod_name = request.GET.get('prod_name')
    var_names = ProductInformation.objects.filter(product_name=prod_name).order_by('variation_name')
    return JsonResponse(list(var_names.values('variation_name')), safe=False)


def get_prod_price(request):
    prod_name = request.GET.get('prod_name')
    var_name = request.GET.get('var_name')
    prod_info = ProductInformation.objects.get(product_name=prod_name, variation_name=var_name)
    price = ProductPrices.objects.get(_product_name=prod_info.get_prod_name())

    return JsonResponse(price.price, safe=False)


def check_nan(field):
    if field == "nan":
        return ''

    return field


def shipping_update(field):
    field = field.replace("Standard Local", "").replace("-", "")

    if field == "":
        field = "Others"

    return field
