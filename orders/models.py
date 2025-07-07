from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel
from products.models import Product


class Cart(TimeStampedModel):
    """
    Shopping cart model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(TimeStampedModel):
    """
    Shopping cart item model
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart for {self.cart.user.username}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(TimeStampedModel):
    """
    Order model
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50)
    payment_details = models.JSONField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(TimeStampedModel):
    """
    Order item model
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order {self.order.id}"

    @property
    def total_price(self):
        if self.price is None:
            return 0
        return self.price * self.quantity


class Payment(TimeStampedModel):
    """
    Payment model
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_id = models.CharField(max_length=100)  # ID from payment gateway
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50)
    payment_details = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.payment_id} for order {self.order.id}"


class Wishlist(TimeStampedModel):
    """
    Wishlist model - stores user's favorite products
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')

    def __str__(self):
        return f"Wishlist for {self.user.username}"

    @property
    def total_items(self):
        return self.items.count()


class WishlistItem(TimeStampedModel):
    """
    Wishlist item model - represents a product in user's wishlist
    """
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('wishlist', 'product')

    def __str__(self):
        return f"{self.product.name} in wishlist for {self.wishlist.user.username}"
