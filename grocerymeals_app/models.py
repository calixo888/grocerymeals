from django.db import models

class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    provider = models.CharField(max_length=50)
    image_url = models.TextField()
    title = models.CharField(max_length=50)
    formatted_title = models.CharField(max_length=50)
    price = models.CharField(max_length=50)

    def __str__(self):
        return self.provider + " - " + self.title
