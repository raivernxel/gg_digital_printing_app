from django import forms
from . import models

class ProductPricesForm(forms.ModelForm):
    product_name = forms.ModelChoiceField(
        queryset=models.Products.objects.all(),
        label='Select Product',
        to_field_name='id'
    )
    material_price = forms.DecimalField(max_digits=9, decimal_places=4)
    price = forms.DecimalField(max_digits=9, decimal_places=4)
    price_last_update = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super(ProductPricesForm, self).__init__(*args, **kwargs)
        self.fields['product_name'].label_from_instance = lambda obj: obj.product_name()

    class Meta:
        model = models.ProductPrices
        fields = ['product_name', 'material_price', 'price', 'price_last_update']