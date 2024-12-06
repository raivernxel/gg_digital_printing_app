from django.db import models


class ReservedMoney(models.Model):
    title = models.CharField(max_length=30)
    month = models.IntegerField()
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    IOE = models.CharField(max_length=1)

    class Meta:
        db_table = 'reserved_money'
