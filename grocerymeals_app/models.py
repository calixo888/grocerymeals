from django.db import models

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    provider = models.CharField(max_length=500)
    image_url = models.TextField()
    title = models.CharField(max_length=500)
    formatted_title = models.CharField(max_length=500)
    price = models.CharField(max_length=500)

    def __str__(self):
        return self.provider + " - " + self.title


class ShoppingListItem(models.Model):
    user_id = models.IntegerField()
    product_id = models.CharField(max_length=50)

    def __str__(self):
        product = Product.objects.get(id=self.product_id)
        return product.title
