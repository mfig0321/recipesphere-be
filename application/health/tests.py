from rest_framework.test import APITestCase
from rest_framework import status


class StatusCheckTest(APITestCase):

    def test_health_check_endpoint(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
