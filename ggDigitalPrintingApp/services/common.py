from orders.models import OrderMaintenance


def get_trello_id_count():
    return OrderMaintenance.objects.get(name='trello_id_count').value


def get_trello_id():
    id_count = get_trello_id_count()

    # Sample ID : GGA00562FB
    return f'GGA{'0'*(5-len(id_count))}{id_count}FB'