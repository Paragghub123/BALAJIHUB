from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class ProductDetail(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.price} €"

class ProductUserDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_product_detail')
    product = models.ForeignKey(ProductDetail, on_delete=models.CASCADE)
    quantity = models.IntegerField( validators=[MinValueValidator(0), MaxValueValidator(10)])
    total_price = models.DecimalField(decimal_places=2,null=True,blank=True,max_digits=6)

    def __str__(self):
        return f"{self.user.username}"

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product')
        ]

    def gross_order_price(self, obj):
        total = ProductUserDetail.objects.filter(user=obj.user).aggregate(
            total=models.Sum('total_price')
        )['total'] or 0
        return f"{total:.2f} €"

    gross_order_price.short_description = "Gross Order Price"
