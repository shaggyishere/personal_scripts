import requests
import json
import os
import logging
import uuid
from time import time
from api_tester_config import APITesterConfig

class APITester:
    def __init__(self, configs: APITesterConfig, script_dir, microservice, env):
        self.results = {}
        self.config = configs
        self.status_log = {"200": [], "500": [], "Other": {}}
        self.session = requests.Session()
        self.script_dir = script_dir
        self.microservice = microservice
        self.env = env
        self.api_test_file = os.path.join(script_dir, "api_configs", "apis_to_test_golia.json") if microservice == "golia" else os.path.join(script_dir, "api_configs", "apis_to_test.json")

    def authenticate(self):
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

            self.session_id = ""

            if self.microservice == "golia":
                # creating session
                response = self.session.post(
                    f"{self.config.session_manager_url}/api/session",
                    json=self.config.golia_session_manager_create_payload,
                    headers=headers,
                    verify=False
                )

                response.raise_for_status()
                self.session_id = response.json().get("payload")

                if not self.session_id:
                    raise ValueError("Error creating session with session manager.")

                # updating session
                response = self.session.post(
                    f"{self.config.session_manager_url}/api/session/customer/{self.session_id}",
                    json=self.config.golia_session_manager_update_payload,
                    headers=headers,
                    verify=False
                )

                response.raise_for_status()
            else:
                self.config.session_manager_payload["sessionId"] = str(uuid.uuid4())

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
        total_response_time = None

        with open(self.api_test_file, "r") as file:
            api_tests = json.load(file)

        logging.info(f"--------------------------------------------begin script run -------------------------------------------------")
        logging.info(f"microservice: {self.microservice}, env: {self.env}")

        try:

            for api_info in api_tests:
                total_response_time = (total_response_time or 0.0) + self._test_single_api(api_info)

            self._save_results(f"api_responses_{self.microservice}_{self.env}.json", self.results)
            self._save_results(f"api_status_{self.microservice}_{self.env}.json", self.status_log)

        finally:
            logging.info(f"--------------------------------------------end script run ---------------------------------------------------")

        print(f"API testing completed. Total duration time: {round(total_response_time, 2)}s. Check log file and api_results/ directory for more infos.")

    def _test_single_api(self, api_info):
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

            self.results["microservice"] = self.microservice
            self.results["env"] = self.env
            self.results[api_route] = {
                "query_param": query_params,
                "status_code": response.status_code,
                "response_time_sec": response_time,
                "response": response.json() if response.status_code in {200, 400, 500} else {}
            }

            self.status_log["microservice"] = self.microservice
            self.status_log["env"] = self.env
            if response.status_code == 200:
                self.status_log["200"].append(api_route)
            elif response.status_code == 500:
                self.status_log["500"].append(api_route)
            else:
                self.status_log["Other"][api_route] = response.status_code

            logging.info(f"API: {api_route}, Method: {method}, Status: {response.status_code}, Time: {response_time}s")

            return response_time

        except requests.RequestException as e:
            self.results[api_route] = {"error": str(e)}
            logging.error(f"API: {api_route} failed with error: {str(e)}")

    
    def _save_results(self, filename, data, directory="api_results"):
        os.makedirs(directory, exist_ok=True)
        
        file_path = os.path.join(directory, filename)
        
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    