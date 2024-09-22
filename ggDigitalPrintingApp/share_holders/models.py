from django.db import models
from django.db.models import DO_NOTHING


# Create your models here.
class ShareHolders(models.Model):
    investor_name = models.CharField(primary_key=True, max_length=20)
    share_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    invested = models.DecimalField(max_digits=14, decimal_places=4)

    class Meta:
        db_table = 'share_holders'

class NotClaimedIncome(models.Model):
    investor_name = models.ForeignKey(ShareHolders, on_delete=DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=4)
    month = models.IntegerField()
    year = models.IntegerField()
    received = models.BooleanField(default=False)

    class Meta:
        db_table = 'not_claimed_income'

class MoneySentToPrinterInvestors(models.Model):
    investor_name = models.ForeignKey(ShareHolders, on_delete=DO_NOTHING)
    amount_sent = models.DecimalField(max_digits=10, decimal_places=4)
    proof_of_payment = models.ImageField(null=True)
    platform = models.CharField(max_length=10)
    date_sent = models.DateField()
    note = models.TextField()

    class Meta:
        db_table = 'money_sent_to_printer_investors'
