from django.test import TestCase
from django.urls import reverse

from restaurants.models import Client, RestaurantRating
from restaurants.tests.factories import RestaurantFactory, ClientFactory


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('login')
        self.app_client = ClientFactory(name="test")

    def test_new_client(self):
        self.assertEqual(Client.objects.count(), 1)
        self.assertIsNone(self.client.session.get('client'))
        response = self.client.post(self.url, {'name': "new client"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Client.objects.count(), 2)
        self.assertEqual(self.client.session.get('client'), "new client")

    def test_existing_client(self):
        self.assertEqual(Client.objects.count(), 1)
        self.assertIsNone(self.client.session.get('client'))
        response = self.client.post(self.url, {'name': "test"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(self.client.session.get('client'), "test")


class RestaurantsViewTestCase(TestCase):
    def setUp(self):
        session = self.client.session
        session.update({'client': ClientFactory().name})
        session.save()
        self.url = reverse('restaurants')
        self.r1 = RestaurantFactory(name="Name")
        self.r2 = RestaurantFactory(name="Test")
        self.r3 = RestaurantFactory(name="Great Restaurant")

    def test_redirect_when_client_not_in_session(self):
        session = self.client.session
        session.update({'client': None})
        session.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login'))

    def test_list(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Great Restaurant")
        self.assertContains(response, "Test")
        self.assertContains(response, "Name")

    def test_search(self):
        response = self.client.get(
            f'{self.url}?term=Great',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.json(), [{'id': self.r3.id, 'label': "Great Restaurant"}])


class RestaurantDetailViewTestCase(TestCase):
    def setUp(self):
        session = self.client.session
        self.app_client = ClientFactory()
        session.update({'client': self.app_client.name})
        session.save()
        self.restaurant = RestaurantFactory(name="Great Restaurant")
        self.url = reverse('restaurant_detail', kwargs={'pk': self.restaurant.id})

    def test_redirect_when_client_not_in_session(self):
        session = self.client.session
        session.update({'client': None})
        session.save()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login'))

    def test_get(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Great Restaurant")

    def test_post(self):
        self.assertEqual(RestaurantRating.objects.count(), 0)
        response = self.client.post(
            self.url,
            data={'value': '5'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'msg': "Rating added"})
        self.assertEqual(RestaurantRating.objects.count(), 1)
        rating = RestaurantRating.objects.first()
        self.assertEqual(rating.client, self.app_client)
        self.assertEqual(rating.restaurant, self.restaurant)
        self.assertEqual(rating.rating, 5)

    def test_post_not_ajax(self):
        response = self.client.post(self.url, data={'value': 2})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'This endpoint accepts only AJAX POSTs')

    def test_post_invalid_value(self):
        response = self.client.post(
            self.url,
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'msg': "Invalid value"})

        response = self.client.post(
            self.url,
            data={'value': '0'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'msg': "Invalid value"})

        response = self.client.post(
            self.url,
            data={'value': '6'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'msg': "Invalid value"})

        response = self.client.post(
            self.url,
            data={'value': 'not digit'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'msg': "Invalid value"})

    def test_post_incorrect_client(self):
        session = self.client.session
        session.update({'client': None})
        session.save()
        response = self.client.post(
            self.url,
            data={'value': '1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'msg': "Invalid client in session"})
