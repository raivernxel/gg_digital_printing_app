from django.db import models
from django.db.models import UniqueConstraint
from products.models import ProductInformation


# Create your models here.
class Logistics(models.Model):
    logistic_name = models.CharField(unique=True, max_length=50)

    class Meta:
        db_table = 'logistics'


class OrderMaintenance(models.Model):
    name = models.CharField(unique=True, max_length=255)
    value = models.CharField(max_length=100)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'order_maintenance'


class SellingPlatform(models.Model):
    platform = models.CharField(unique=True, max_length=20)

    class Meta:
        db_table = 'selling_platform'


class OrderStatus(models.Model):
    status_type = models.CharField(unique=True, max_length=15)
    color = models.CharField(max_length=10, default="green")

    class Meta:
        db_table = 'order_status'


class OrderFulfillment(models.Model):
    order_id = models.CharField(primary_key=True, max_length=20)
    amount_received = models.DecimalField(max_digits=10, decimal_places=4)
    account_received = models.CharField(max_length=20)
    payout_completed_date = models.DateField()
    updated = models.BooleanField(default=False)

    class Meta:
        db_table = 'order_fulfillment'


class OrderInformation(models.Model):
    order_id = models.CharField(primary_key=True, max_length=20)
    username = models.CharField(max_length=30)
    delivery_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=20, blank=True)
    province = models.CharField(max_length=20, blank=True)
    tracking_number = models.CharField(max_length=20, blank=True)
    shipping_option = models.ForeignKey(Logistics, on_delete=models.DO_NOTHING)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.DO_NOTHING)
    released_amount = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    cancel_reason = models.CharField(max_length=100, blank=True)
    refund_status = models.CharField(max_length=20, blank=True)
    platform = models.ForeignKey(SellingPlatform, on_delete=models.DO_NOTHING)
    delivery_fee = models.DecimalField(max_digits=9, decimal_places=4, default=0)
    artist_cut = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    stocks_updated = models.BooleanField(default=False)
    blank_mousepad = models.BooleanField(default=False)
    order_creation_date = models.DateField()
    order_complete_date = models.DateField(null=True, blank=True)
    cancelled_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'order_information'


class OrderList(models.Model):
    order_id = models.ForeignKey(OrderInformation, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    variation_name = models.CharField(max_length=40, blank=True)
    original_price = models.DecimalField(max_digits=9, decimal_places=4, default=0)
    deal_price = models.DecimalField(max_digits=9, decimal_places=4, default=0)
    quantity = models.IntegerField()
    returned_quantity = models.IntegerField(default=0)
    defect_quantity = models.IntegerField(default=0)
    sku = models.CharField(max_length=255, null=True, blank=True)

    def clean(self):
        if not ProductInformation.objects.filter(product_name=self.product_name, variation_name=self.variation_name).exists():
            raise ValueError(f"No such product in Product Information! {self.product_name} {self.variation_name}")

    # Validate first before saving.
    def save(self, *args, **kwargs):
        self.full_clean()
        super(OrderList, self).save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(fields=('order_id', 'product_name', 'variation_name'), name='unique_order_list')
        ]
        db_table = 'order_list'
