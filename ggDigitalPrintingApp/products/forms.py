from django import forms
from .models import Products, ProductPrices


class ProductPricesForm(forms.ModelForm):
    product_name = forms.ModelChoiceField(
        queryset=Products.objects.all(),
        label='Select Product',
        to_field_name='id'
    )
    price_last_update = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super(ProductPricesForm, self).__init__(*args, **kwargs)
        self.fields['product_name'].label_from_instance = lambda obj: obj.product_name()

    class Meta:
        model = ProductPrices
        fields = ['product_name', 'material_price', 'price', 'price_last_update']
