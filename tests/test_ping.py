import requests
import unittest

class TestPingEndpoint(unittest.TestCase):
    def test_ping_response(self):
        """ Test that the /ping endpoint returns the correct response. """
        # URL to your Flask application
        url = 'http://localhost:5500/ping'
        
        # Make a GET request to the /ping endpoint
        response = requests.get(url)
        
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Assert that the response contains the correct JSON data
        self.assertEqual(response.json(), {'message': 'pong'})

if __name__ == '__main__':
    unittest.main()
