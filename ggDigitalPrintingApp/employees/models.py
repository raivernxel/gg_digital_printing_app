import json

from django.db import models


class Employees(models.Model):
    employee_id = models.IntegerField(default=0)
    employee_name = models.CharField(primary_key=True, max_length=100)
    salary_type = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    products = models.TextField(null=True)

    def get_products(self):
        return json.loads(self.products)

    def set_products(self, product_list):
        self.products = json.dumps(product_list)
        self.save()

    class Meta:
        db_table = 'employees'


class EmployeeLogin(models.Model):
    employee_name = models.ForeignKey(Employees, on_delete=models.DO_NOTHING)
    login = models.DateTimeField(null=True)
    logout = models.DateTimeField(null=True)
    hours = models.IntegerField(default=0)

    class Meta:
        db_table = 'employee_login'
