from django.contrib import admin

from restaurants.models import Restaurant, Client, RestaurantRating, Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


class RestaurantRatingAdmin(admin.TabularInline):
    model = RestaurantRating


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    inlines = [RestaurantRatingAdmin]
    fields = ['name', 'photo', 'address', 'average_rating']
    readonly_fields = ['average_rating']
