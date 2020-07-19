import factory
from faker import Factory

from restaurants.models import Address, Restaurant, Client, RestaurantRating

faker = Factory.create()


class AddressFactory(factory.DjangoModelFactory):
    class Meta:
        model = Address

    country = faker.country()
    city = faker.city()
    street = faker.street_name()
    number = faker.random_number()


class RestaurantFactory(factory.DjangoModelFactory):
    class Meta:
        model = Restaurant

    address = factory.SubFactory(AddressFactory)
    name = faker.word()


class ClientFactory(factory.DjangoModelFactory):
    class Meta:
        model = Client

    name = faker.name()


class RestaurantRatingFactory(factory.DjangoModelFactory):
    class Meta:
        model = RestaurantRating

    client = factory.SubFactory(ClientFactory)
    restaurant = factory.SubFactory(RestaurantFactory)
    rating = 3
