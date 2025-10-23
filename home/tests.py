from rest_framework.test import APITestCase
from rest_framework import status
from home.models import Restaurant

class RestaurantInfoAPITest(APITestCase):
    """
    Test suite for the Restaurant Info API endpoint.
    Ensures the endpoint returns correct restaurant details.
    """

    def setUp(self):
        """
        Create a sample restaurant record before each test.
        """
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            address="123 Test St",
            phone_number="9876543210"
        )
        # Adjust this URL to match your actual endpoint path
        self.url = "/api/restaurant-info/"

    def test_get_restaurant_info(self):
        """
        Ensure GET /api/restaurant-info/ returns restaurant data successfully.
        """
        response = self.client.get(self.url)

        # ✅ Assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # ✅ Check if the response contains expected fields
        self.assertIn("name", response.data)
        self.assertIn("address", response.data)

        # ✅ Assert that data matches what we created
        self.assertEqual(response.data["name"], self.restaurant.name)
        self.assertEqual(response.data["address"], self.restaurant.address)
