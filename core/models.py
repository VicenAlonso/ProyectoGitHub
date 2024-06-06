from django.db import models
from django.contrib.auth.models import User

class MiModelo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre


#python manage.py migrate          # Aplicar migraciones iniciales
#python manage.py createsuperuser  # Crear superusuario
#python manage.py makemigrations   # Crear migraciones para nuevos modelos
#python manage.py migrate          # Aplicar migraciones para nuevos modelos
#python manage.py runserver        # Ejecutar el servidor de desarrollo

#bloqueo de usuario

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateField()
    seller_name = models.CharField(max_length=255)
    seller_email = models.EmailField()
    seller_phone = models.CharField(max_length=20)
    seller_website = models.CharField(max_length=255)
    seller_address = models.CharField(max_length=255)
    buyer_name = models.CharField(max_length=255)
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=20)
    buyer_address = models.CharField(max_length=255)
    shipping_address = models.CharField(max_length=255)
    payment_email = models.EmailField()
    cheque_to = models.CharField(max_length=255)
    bank_transfer = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Order {self.pk} by {self.user.username}'