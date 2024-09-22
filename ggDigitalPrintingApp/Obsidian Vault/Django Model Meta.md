The `Meta` class in a Django model is a way to define metadata for your model. It provides various options to control the behavior of the model, database table creation, validation, permissions, and more. Here’s a list of commonly used `Meta` options in Django models:

### **1. `db_table`**

- Specifies the name of the database table for the model.
- Example:

	class Meta:
	    db_table = 'custom_table_name'


### **2. `verbose_name`**

- A human-readable name for the model in singular form.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     verbose_name = 'product'`
    

### **3. `verbose_name_plural`**

- The plural name for the model.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     verbose_name_plural = 'products'`
    

### **4. `ordering`**

- Specifies the default ordering for queries.
- Use a list of field names to define the ordering. Prefix the field with `'-'` for descending order.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     ordering = ['name', '-created_at']`
    

### **5. `unique_together`** (Deprecated in favor of `UniqueConstraint` in Django 2.2+)

- Enforces a unique constraint on a combination of fields.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     unique_together = [('first_name', 'last_name')]`
    

### **6. `index_together`** (Deprecated in favor of `indexes` in Django 1.11+)

- Creates a database index on the specified set of fields to optimize queries.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     index_together = [['pub_date', 'author']]`
    

### **7. `constraints`** (Introduced in Django 2.2+)

- Allows the use of database constraints such as `UniqueConstraint`, `CheckConstraint`, etc.
- Example:
    
    python
    
    Copy code
    
    from django.db.models import UniqueConstraint, CheckConstraint, Q  
    
    class Meta:     
    constraints = [
	    UniqueConstraint(fields=['email'], name='unique_email'),         CheckConstraint(check=Q(age__gte=18), name='age_gte_18')
	]
    

### **8. `indexes`** (Introduced in Django 1.11+)

- Creates database indexes on specified fields.
- Example:
    
    python
    
    Copy code
    
    `from django.db.models import Index  class Meta:     indexes = [         Index(fields=['last_name', 'first_name']),         Index(fields=['-created_at'], name='created_at_idx')     ]`
    

### **9. `permissions`**

- Custom permissions for the model, which can be used for more granular access control.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     permissions = [         ('can_publish', 'Can publish articles'),     ]`
    

### **10. `get_latest_by`**

- Defines the default field(s) to use when retrieving the latest object (using methods like `latest()`).
- Example:
    
    python
    
    Copy code
    
    `class Meta:     get_latest_by = 'publish_date'`
    

### **11. `default_related_name`**

- Sets a default name for the reverse relation from the related model back to this one.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     default_related_name = 'products'`
    

### **12. `abstract`**

- Specifies if the model is an abstract base class. Abstract models are not created as database tables but can be inherited by other models.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     abstract = True`
    

### **13. `app_label`**

- Sets the application label for the model. Useful when defining a model outside of the standard models module.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     app_label = 'my_custom_app'`
    

### **14. `db_tablespace`**

- Specifies the tablespace for the model (if supported by the database).
- Example:
    
    python
    
    Copy code
    
    `class Meta:     db_tablespace = 'my_tablespace'`
    

### **15. `managed`**

- If `False`, Django won’t create or delete the database table for this model during migrations. Useful for integrating with existing tables.
- Default is `True`.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     managed = False`
    

### **16. `proxy`**

- Indicates whether the model is a proxy model. Proxy models don’t create new database tables; they use the table of the model they are proxying.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     proxy = True`
    

### **17. `select_on_save`**

- If `True`, Django will re-fetch the model from the database after saving it.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     select_on_save = True`
    

### **18. `base_manager_name`**

- The name of the base manager to use for the model.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     base_manager_name = 'objects'`
    

### **19. `default_manager_name`**

- The name of the default manager for the model.
- Example:
    
    python
    
    Copy code
    
    `class Meta:     default_manager_name = 'custom_manager'`
    

### **20. `swappable`**

- Allows the model to be swapped out with another model. Mainly used for built-in Django models (e.g., `AUTH_USER_MODEL`).
- Example:
    
    python
    
    Copy code
    
    `class Meta:     swappable = 'AUTH_USER_MODEL'`
    

### **Summary:**

These `Meta` options provide a wide range of customization for how Django handles models, from specifying database details to setting default behaviors in queries and validations. By adjusting these attributes, you can fine-tune the behavior of your models to suit the needs of your application.