import requests
import json
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
        self.status_log = {"200_OK": [], "500_Internal_Server_Error": [], "Other_Statuses": {}}
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
            logging.info("Authentication successful. JWT token obtained.")

        except requests.exceptions.RequestException as e:
            logging.error(f"Authentication failed: {e}")
            raise

    def test_apis(self):
        """Tests all APIs and logs their responses and status codes."""
        for api_info in self.config.api_list:
            self._test_single_api(api_info)

        self._save_results("api_responses.json", self.results)
        self._save_results("api_status_log.json", self.status_log)

        logging.info("API testing completed. Results saved.")

    def _test_single_api(self, api_info):
        """
        Tests a single API based on provided details.

        :param api_info: Dictionary containing 'endpoint', 'method', 'payload', and 'headers'.
        """
        endpoint = api_info.get("endpoint").lstrip("/")  # Ensure no leading slash
        url = urljoin(self.base_url + "/", endpoint)  # Join base URL with endpoint
        method = api_info.get("method", "GET").upper()
        payload = api_info.get("payload", None)
        headers = api_info.get("headers", {})

        try:
            start_time = time()
            response = self.session.request(
                method, 
                url, 
                json=payload, 
                headers=headers
            )

            response_time = round(time() - start_time, 3)  # Response time in seconds

            self.results[url] = {
                "method": method,
                "status_code": response.status_code,
                "response_time_sec": response_time,
                "response": response.json() if response.status_code == 200 else {"error": "Non-200 response"}
            }

            # Categorize API response status
            if response.status_code == 200:
                self.status_log["200_OK"].append(url)
            elif response.status_code == 500:
                self.status_log["500_Internal_Server_Error"].append(url)
            else:
                self.status_log["Other_Statuses"][url] = response.status_code

            logging.info(f"API: {url}, Method: {method}, Status: {response.status_code}, Time: {response_time}s")

        except requests.RequestException as e:
            self.results[url] = {"error": str(e)}
            self.status_log["Other_Statuses"][url] = "Request failed"
            logging.error(f"API: {url} failed with error: {str(e)}")

    def _save_results(self, filename, data):
        """Saves results to a JSON file."""
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)