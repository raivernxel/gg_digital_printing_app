The `on_delete` option in Django’s `ForeignKey` field specifies the behavior to adopt when the referenced object (the one linked by the foreign key) is deleted. Here’s a list of the available `on_delete` options you can use:

### **1. `CASCADE`**

- Deletes the objects that have a foreign key reference to the deleted object.
- Use this when you want related objects to be deleted along with the parent.
- Example:
    
    python
    
    Copy code
    
    `from django.db import models  class Order(models.Model):     customer = models.ForeignKey('Customer', on_delete=models.CASCADE)`
    
- **Behavior:** If the referenced `Customer` is deleted, all associated `Order` instances will also be deleted.

### **2. `PROTECT`**

- Prevents the deletion of the referenced object if it has related objects.
- Raises a `ProtectedError` when an attempt is made to delete the referenced object.
- Example:
    
    python
    
    Copy code
    
    `class Order(models.Model):     customer = models.ForeignKey('Customer', on_delete=models.PROTECT)`
    
- **Behavior:** If the `Customer` has associated `Order` instances, deleting the `Customer` will raise an error.

### **3. `SET_NULL`**

- Sets the foreign key to `NULL` when the referenced object is deleted.
- Requires the foreign key field to have `null=True`.
- Example:
    
    python
    
    Copy code
    
    `class Order(models.Model):     customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True)`
    
- **Behavior:** If the `Customer` is deleted, the `customer` field in `Order` will be set to `NULL`.

### **4. `SET_DEFAULT`**

- Sets the foreign key to its default value when the referenced object is deleted.
- Requires the foreign key field to have a `default` value specified.
- Example:
    
    python
    
    Copy code
    
    `class Order(models.Model):     customer = models.ForeignKey('Customer', on_delete=models.SET_DEFAULT, default=1)`
    
- **Behavior:** If the `Customer` is deleted, the `customer` field in `Order` will be set to the specified default value.

### **5. `SET()`**

- Sets the foreign key to the value passed to `SET()` when the referenced object is deleted.
- Accepts a callable (e.g., a function) that returns a value to set.
- Example:
    
    python
    
    Copy code
    
    `class Order(models.Model):     customer = models.ForeignKey('Customer', on_delete=models.SET(some_function))`
    
- **Behavior:** If the `Customer` is deleted, the `customer` field in `Order` will be set to the value returned by `some_function`.

### **6. `DO_NOTHING`**

- Takes no action when the referenced object is deleted.
- This requires manual handling of the situation (e.g., using signals to manage the deletion).
- Example:
    
    python
    
    Copy code
    
    `class Order(models.Model):     customer = models.ForeignKey('Customer', on_delete=models.DO_NOTHING)`
    
- **Behavior:** No action is taken when the `Customer` is deleted. If the database integrity is violated (e.g., trying to delete a `Customer` that is still referenced by an `Order`), it will result in an integrity error at the database level.

### **Summary Table of `on_delete` Options:**

|Option|Description|
|---|---|
|`CASCADE`|Deletes related objects automatically.|
|`PROTECT`|Prevents deletion by raising a `ProtectedError`.|
|`SET_NULL`|Sets the foreign key to `NULL`; requires `null=True`.|
|`SET_DEFAULT`|Sets the foreign key to its default value.|
|`SET()`|Sets the foreign key to the value provided by a callable.|
|`DO_NOTHING`|Takes no action; requires manual handling of integrity issues.|

Choose the `on_delete` behavior that best fits your application's data integrity and management needs.