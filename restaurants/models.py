from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.safestring import mark_safe


class Address(models.Model):
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    number = models.IntegerField()

    def __str__(self):
        return f"{self.country} {self.city} {self.street} {self.number}"


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='photos', blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        if rating := self.restaurantrating_set.aggregate(Avg('rating')).get('rating__avg'):
            rating = round(rating, 1)
        return rating

    @property
    def image_tag(self):
        if self.photo:
            return mark_safe(f'<img src="{self.photo.url}" class="img-fluid img-thumbnail"/>')
        return None


class Client(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class RestaurantRating(models.Model):
    """
    One client can give many ratings for the same restaurant.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f"{self.client} {self.restaurant} {self.rating}"
