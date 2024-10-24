from django.db import models


class Expenses(models.Model):
    expense_title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=9, decimal_places=4, default=0)
    expense_date = models.DateField()
    proof = models.ImageField(upload_to='proof_images/')
    delivery_fee = models.DecimalField(max_digits=9, decimal_places=4, default=0)
    product_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'expenses'


class MonthlyFeeMaintenance(models.Model):
    title = models.CharField(primary_key=True, max_length=100)
    amount = models.DecimalField(max_digits=9, decimal_places=4, default=0)

    class Meta:
        db_table = 'monthly_fee_maintenance'


class MonthlyFees(models.Model):
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=9, decimal_places=4, default=0)
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        db_table = 'monthly_fees'


class Bills(models.Model):
    bill_name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=9, decimal_places=4, default=0)
    consumption = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    proof = models.ImageField(upload_to='proof_images/')
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        db_table = 'bills'


class ElectricityEquipment(models.Model):
    equipment = models.CharField(primary_key=True, max_length=200)
    wattage = models.IntegerField()

    class Meta:
        db_table = 'electricity_equipment'


class Electricity(models.Model):
    equipment = models.ForeignKey(ElectricityEquipment, on_delete=models.DO_NOTHING)
    hours_used = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    date_used = models.DateField()

    class Meta:
        db_table = 'electricity'
