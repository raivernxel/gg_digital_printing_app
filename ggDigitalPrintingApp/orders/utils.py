from datetime import datetime

from services.common import get_trello_id
from orders.models import Logistics, OrderStatus, SellingPlatform


def extract_order_data(request):
    data = {
        'trello_id': get_trello_id(),
        'trello_card_id': request.POST.get('card_id'),
        'username': request.POST.get('username'),
        'list_of_orders': request.POST.get('list_of_orders'),
        'address': request.POST.get('address'),
        'city': request.POST.get('city'),
        'region': request.POST.get('region'),
        'postal_code': request.POST.get('postal_code'),
        'first_name': request.POST.get('first_name'),
        'surname': request.POST.get('last_name'),
        'contact_number': request.POST.get('contact_number'),
        'email': request.POST.get('email'),
        'released_amount': float(request.POST.get('released_amount')),
        'delivery_fee': float(request.POST.get('delivery_fee')),
        'order_date': datetime.strptime(request.POST.get('order_date'), "%Y-%m-%d").date(),
        'delivered_date': datetime.strptime(request.POST.get('deliver_date'), "%Y-%m-%d").date(),
        'tracking_number': request.POST.get('tracking_number'),
        'logistics': Logistics.objects.get(logistic_name=request.POST.get('logistics')),
        'order_status': OrderStatus.objects.get(status_type='Delivered'),
        'platform': SellingPlatform.objects.get(platform=request.POST.get('platform'))
    }

    return data