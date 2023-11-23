from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ProductCategory(models.Model):
    name = models.CharField('Category name', max_length=100)
    description = models.CharField('Category description', max_length=300)

class Product(models.Model):
    name = models.CharField('Product name', max_length=200)
    image = models.ImageField('Product image', max_length=300)
    stock = models.IntegerField('Product stock', default=0)
    price = models.DecimalField('Product price', max_digits=10, decimal_places=2)
    category_id = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def is_available(self):
        return self.stock > 0

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    first_name = models.CharField('Client first name', max_length=100)
    last_name = models.CharField('Client last name', max_length=200)
    address = models.CharField('Client address', max_length=300)
    phone = models.IntegerField('Client phone')

    def create_cart(self):
        return Cart.objects.create(user=self.user)

class PaymentMethod(models.Model):
    name = models.CharField('Payment method', max_length=100)

class Pedido(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    housenumber = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    pickup_time = models.TimeField()
    total_carrito = models.DecimalField(max_digits=10, decimal_places=2)
    status_choices = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('ENTREGADA', 'Entregada'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='PENDIENTE')

    def __str__(self):
        return f'Pedido {self.id} - {self.user.username}'



class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(Product, through='CartItem')
    created_at = models.DateTimeField(default=timezone.now)

    def get_total_price(self):
        total_price = sum(item.subtotal() for item in self.cartitem_set.all())
        return total_price

    def __str__(self):
        return f'Cart for {self.user.username}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField('Product quantity', default=0)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, null=True, blank=True)

    def subtotal(self):
        if self.quantity is not None:
            return self.product.price * self.quantity
        return 0

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in {self.cart}'


    @classmethod
    def create_or_update(cls, cart, product, quantity=1):
        cart_item, created = cls.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item
    

