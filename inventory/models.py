from django.db import models

class Item(models.Model):
    TYPE_CHOICES = [
        ('pastilla', 'Pastilla'),
        ('jarabe', 'Jarabe'),
        ('inyectable', 'Inyectable'),
    ]
    
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    disease_category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    version = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.sku} - {self.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
        ('ROLLEDBACK', 'Rolled Back'),
    ]
    
    code = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Order {self.code} - {self.status}"

class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.order.code} - {self.item.name} x {self.quantity}"
