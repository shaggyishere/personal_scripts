import logging
import urllib3
import os
import sys
import json
from api_tester import APITester
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("api_test.log"),
        logging.StreamHandler()
    ]
)

def check_env_variables():
    required_env_vars = ["BASE_URL", "AUTH_URL", "AUTH_PAYLOAD", "AUTH_BASIC_AUTH_HEADER"]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

if __name__ == "__main__":
    load_dotenv()

    try:
        check_env_variables()

    except EnvironmentError as e:
        print(e)
        sys.exit(1)

    BASE_URL = os.getenv("BASE_URL")
    AUTH_URL = os.getenv("AUTH_URL")
    auth_payload_str = os.getenv("AUTH_PAYLOAD")
    AUTH_PAYLOAD =  json.loads(auth_payload_str) if auth_payload_str else {}
    AUTH_BASIC_AUTH_HEADER = os.getenv("AUTH_BASIC_AUTH_HEADER")

    api_list = [
        {"endpoint": "/get-endpoint", "method": "GET"},
        {"endpoint": "/post-endpoint", "method": "POST", "payload": {"key": "value"}},
        {"endpoint": "/put-endpoint", "method": "PUT", "payload": {"update": "new data"}},
        {"endpoint": "/delete-endpoint", "method": "DELETE"},
    ]

    tester = APITester(BASE_URL, api_list, AUTH_URL, AUTH_PAYLOAD, AUTH_BASIC_AUTH_HEADER)
    tester.authenticate()
    # tester.test_apis()
