class Employee:
    def __init__(self, employee_name, salary):
        self.employee_name = employee_name
        self.salary = salary
    

class Products(Employee):
    def __init__(self, employee_name, salary, products):
        super().__init__(employee_name, salary)
        self.products = products
