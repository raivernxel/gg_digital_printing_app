from django import forms
from .models import OrderInformation, Logistics, OrderStatus, SellingPlatform


class OrderInformationForm(forms.ModelForm):
    shipping_option = forms.ModelChoiceField(
        queryset=Logistics.objects.all(),
        label='Logistics',
        to_field_name='logistic_name'
    )
    order_status = forms.ModelChoiceField(
        queryset=OrderStatus.objects.all(),
        label='Order Status',
        to_field_name='status_type'
    )
    platform = forms.ModelChoiceField(
        queryset=SellingPlatform.objects.all(),
        label='Selling Platform',
        to_field_name='platform'
    )
    order_creation_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    order_complete_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    cancelled_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super(OrderInformationForm, self).__init__(*args, **kwargs)
        self.fields['shipping_option'].label_from_instance = lambda obj: obj.logistic_name
        self.fields['order_status'].label_from_instance = lambda obj: obj.status_type
        self.fields['platform'].label_from_instance = lambda obj: obj.platform

    class Meta:
        model = OrderInformation
        fields = ['order_id', 'username', 'delivery_address', 'city', 'province', 'tracking_number', 'shipping_option',
                  'order_status', 'released_amount', 'cancel_reason', 'refund_status', 'platform', 'delivery_fee',
                  'artist_cut', 'stocks_updated', 'blank_mousepad', 'order_creation_date', 'order_complete_date',
                  'cancelled_date']
