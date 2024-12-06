from orders.models import OrderMaintenance
from datetime import datetime


def get_trello_id_count():
    return OrderMaintenance.objects.get(name='trello_id_count').value


def get_trello_id():
    id_count = get_trello_id_count()

    # Sample ID : GGA00562FB
    return f'GGA{'0'*(5-len(id_count))}{id_count}FB'


def get_month_and_year():
    year_range = range(2022, datetime.now().year+1)
    cur_year = datetime.now().year
    cur_month = datetime.now().month
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

    month_and_year = {
        'year_range': year_range,
        'cur_year': cur_year,
        'cur_month': cur_month,
        'months': months
    }

    return month_and_year