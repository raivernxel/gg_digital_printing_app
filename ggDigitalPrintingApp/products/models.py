from django.db import models
from django.db.models import UniqueConstraint


# Create your models here.
class ProductTypes(models.Model):
    product_type = models.CharField(unique=True, max_length=15)

    class Meta:
        db_table = 'product_types'

class Products(models.Model):
    product_type = models.CharField(max_length=20)
    variation_1 = models.CharField(max_length=20)
    variation_2 = models.CharField(max_length=20)
    stocks = models.IntegerField(default=0)

    def product_name(self):
        return f'{self.product_type}:{self.variation_1}:{self.variation_2}'

    class Meta:
        constraints = [
            UniqueConstraint(fields=('product_type','variation_1','variation_2'), name='unique_product_name')
        ]
        db_table = 'products'

class ProductPrices(models.Model):
    _product_name = models.CharField(unique=True, max_length=200)
    material_price = models.DecimalField(max_digits=9, decimal_places=4)
    price = models.DecimalField(max_digits=9, decimal_places=4)
    price_last_update = models.DateField()

    @property
    def product_name(self):
        return self._product_name

    @product_name.setter
    def product_name(self, product_name):
        for product in Products.objects.all():
            if product_name == product.product_name():
                self._product_name = product_name
                return

        raise ValueError("No such product name in Product list!")

    class Meta:
        db_table = 'product_prices'

class ProductInformation(models.Model):
    product_name = models.CharField(max_length=100, default="")
    variation_name = models.CharField(max_length=50)
    product_type = models.CharField(max_length=100)
    variation_1 = models.CharField(max_length=20)
    variation_2 = models.CharField(max_length=20)
    bundle = models.BooleanField(default=False)
    bundle_count = models.IntegerField(default=0)

    def clean(self):
        if not Products.objects.filter(product_type=self.product_type, variation_1=self.variation_1, variation_2=self.variation_2).exists():
            raise ValueError("No such product name in Product list!")

    #Validate first before saving.
    def save(self, *args, **kwargs):
        self.full_clean()
        super(ProductInformation, self).save(*args, **kwargs)

    class Meta:
        db_table = 'product_information'