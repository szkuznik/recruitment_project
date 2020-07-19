from django.test import TestCase

from restaurants.tests.factories import RestaurantFactory, RestaurantRatingFactory


class RestaurantTestCase(TestCase):
    def setUp(self):
        self.restaurant = RestaurantFactory()
        RestaurantRatingFactory(restaurant=self.restaurant, rating=3)
        RestaurantRatingFactory(restaurant=self.restaurant, rating=3)
        RestaurantRatingFactory(restaurant=self.restaurant, rating=4)
        self.restaurant2 = RestaurantFactory()

    def test_average_rating(self):
        self.assertEqual(self.restaurant.average_rating, 3.3)
        self.assertIsNone(self.restaurant2.average_rating)
