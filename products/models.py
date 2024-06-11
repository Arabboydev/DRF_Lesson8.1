from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=300)

    class Meta:
        db_table = 'Category'

    def __str__(self):
        return self.name


class Pages(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, unique=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Pages'

    def __str__(self):
        return self.name


class Products(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    page = models.ForeignKey(Pages, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    description = models.TextField()
    price = models.FloatField()
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    price_discount = models.FloatField(default=0)

    def calculate_price_discount(self):
        return self.price * (1 - (self.discount / 100))

    def save(self, *args, **kwargs):
        self.price_discount = self.calculate_price_discount()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Products'

    def __str__(self):
        return self.name
# class Products(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     page = models.ForeignKey(Pages, on_delete=models.CASCADE)
#     name = models.CharField(max_length=500)
#     description = models.TextField()
#     price = models.FloatField()
#     discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
#     price_discount = models.IntegerField(default=1)
#
#     def calculate_price_discount(self):
#         return self.price - ((self.price // 100) * self.discount)
#
#     def save(self, *args, **kwargs):
#         self.price_discount = self.calculate_price_discount()
#         super().save(*args, **kwargs)
#
#     class Meta:
#         db_table = 'Products'
#
#     def __str__(self):
#         return self.name
#


class Images(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')

    class Meta:
        db_table = 'Images'

    def __str__(self):
        return f"image of - {self.product.name}"


class Comments(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    star_given = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "Comments"

    def __str__(self):
        return f"comment of - {self.product.name}"


class SavedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'SavedProduct'
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} saved {self.product.name}"
#
#
# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     total_price = models.FloatField(default=0)
#
#     class Meta:
#         db_table = 'Order'
#
#     def __str__(self):
#         return f"Order {self.id} by {self.user.username}"
#
#     def calculate_total_price(self):
#         total = sum(item.get_total_price() for item in self.items.all())
#         self.total_price = total
#         self.save()
#
#
# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey(Products, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#
#     class Meta:
#         db_table = 'OrderItem'
#
#     def __str__(self):
#         return f"{self.product.name} (x{self.quantity}) in order {self.order.id}"
#
#     def get_total_price(self):
#         return self.product.price_discount * self.quantity
#
#     def save(self, *args, **kwargs):
#         self.price = self.product.price_discount * self.quantity
#         super().save(*args, **kwargs)
#         self.order.calculate_total_price()
# class Like(models.Model):
#     account = models.ForeignKey(User, on_delete=models.CASCADE)
#     product = models.ForeignKey(Products, on_delete=models.CASCADE)
#
#     class Meta:
#         db_table = "Likes"
#
#     def __str__(self):
#         return f"{self.account.username} liked {self.product.name}"


class CartItem(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'
