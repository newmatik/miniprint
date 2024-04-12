import os
import unittest
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TestPrintersAPI(unittest.TestCase):
    def test_list_printers(self):
        """
        Test that the API endpoint to list printers returns a successful response
        and the response contains the expected content type and structure.
        """
        # Setup
        url = 'http://localhost:5500/printers'
        headers = {'apikey': os.getenv('APIKEY')}

        # Execute
        response = requests.get(url, headers=headers)
        
        # Verify
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200, "API failed to respond with status 200, received {0} instead.".format(response.status_code))
        
        # Check for correct content-type
        self.assertIn('application/json', response.headers['Content-Type'], "API did not return content in JSON format.")

        # Success message
        print("Test passed: '/printers' endpoint correctly returns a list of printers with the expected structure and content type.")

if __name__ == '__main__':
    unittest.main()
