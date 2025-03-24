import requests
import json
import os
import logging
from time import time
from api_tester_config import APITesterConfig
from urllib.parse import urljoin

class APITester:
    def __init__(self, config: APITesterConfig):
        """
        Initializes the API tester.

        :param base_url: The common base URL for all APIs.
        :param api_list: A list of dictionaries containing API details.
        :param auth_token: Optional JWT token for authentication.
        """
        self.results = {}
        self.config = config
        script_dir = os.path.dirname(os.path.abspath(__file__)) 
        self.api_test_file = os.path.join(script_dir, "apis_to_test.json")
        self.status_log = {"200": [], "500": [], "Other": {}}
        self.session = requests.Session()

    def authenticate(self):
        """Obtain JWT token from the authentication endpoint."""
        try:

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "APITester/1.0",
                "Authorization": self.config.auth_basic_auth_header
            }

            response = self.session.post(
                self.config.auth_url,
                data=self.config.auth_payload,
                headers=headers,
                verify=False
            )

            response.raise_for_status()
            self.token = response.json().get("access_token")

            if not self.token:
                raise ValueError("Authentication failed: No access_token in response.")

            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print("Authentication successful. JWT token obtained.")

        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            raise
    
    def create_session(self):
        try:    
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "APITester/1.0"
            }

            response = self.session.post(
                self.config.session_manager_url,
                json=self.config.session_manager_payload,
                headers=headers,
                verify=False
            )

            response.raise_for_status()
            self.session_id = response.json().get("sessionId")

            if not self.session_id:
                raise ValueError("Error creating session with session manager.")
            
            self.session.headers.update({"X-BEAR-SESSION-TOKEN": self.session_id})
            print(f"Session created succesfully. session_id: {self.session_id}")

        except requests.exceptions.RequestException as e:
            print(f"Session creation failed: {e}")
            raise


    def test_apis(self):
        with open(self.api_test_file, "r") as file:
            api_tests = json.load(file)

        """Tests all APIs and logs their responses and status codes."""
        for api_info in api_tests:
            self._test_single_api(api_info)

        self._save_results("api_responses.json", self.results)
        self._save_results("api_status_log.json", self.status_log)

        print("API testing completed. Check log files for more infos.")

    def _test_single_api(self, api_info):
        """
        Tests a single API based on provided details.

        :param api_info: Dictionary containing 'endpoint', 'method', 'payload', and 'headers'.
        """
        api_route = api_info['route']
        url = f"{self.config.base_url.rstrip('/')}{api_route}"
        method = api_info.get("method", "GET").upper()
        headers = api_info.get("headers", {})
        query_params = api_info.get("query_params", {})
        request_body = api_info.get("body", None)

        try:
            start_time = time()
            response = self.session.request(
                method, 
                url, 
                params=query_params,
                headers=headers,
                json=request_body
            )

            response_time = round(time() - start_time, 3)  # Response time in seconds

            self.results[api_route] = {
                "method": method,
                "status_code": response.status_code,
                "response_time_sec": response_time,
                "response": response.json() if response.status_code == 200 else {}
            }

            # Categorize API response status
            if response.status_code == 200:
                self.status_log["200"].append(api_route)
            elif response.status_code == 500:
                self.status_log["500"].append(api_route)
            else:
                self.status_log["Other"][api_route] = response.status_code

            logging.info(f"API: {api_route}, Method: {method}, Status: {response.status_code}, Time: {response_time}s")

        except requests.RequestException as e:
            self.results[api_route] = {"error": str(e)}
            logging.error(f"API: {api_route} failed with error: {str(e)}")

    def _save_results(self, filename, data):
        """Saves results to a JSON file."""
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)