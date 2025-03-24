import logging
import urllib3
import os
import sys
import json
from api_tester import APITester
from api_tester_config import APITesterConfig
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
    required_env_vars = ["BASE_URL", "AUTH_URL", "SESSION_MANAGER_URL", "AUTH_PAYLOAD", "SESSION_MANAGER_PAYLOAD", "AUTH_BASIC_AUTH_HEADER"]

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

    auth_payload_str = os.getenv("AUTH_PAYLOAD")
    session_manager_payload_str = os.getenv("SESSION_MANAGER_PAYLOAD")
    AUTH_PAYLOAD =  json.loads(auth_payload_str) if auth_payload_str else {}
    SESSION_MANAGER_PAYLOAD =  json.loads(session_manager_payload_str) if session_manager_payload_str else {}

    api_list = [
        {"endpoint": "/get-endpoint", "method": "GET"},
        {"endpoint": "/post-endpoint", "method": "POST", "payload": {"key": "value"}},
        {"endpoint": "/put-endpoint", "method": "PUT", "payload": {"update": "new data"}},
        {"endpoint": "/delete-endpoint", "method": "DELETE"},
    ]

    config = APITesterConfig(
        os.getenv("BASE_URL"),
        api_list,
        os.getenv("AUTH_URL"),
        os.getenv("SESSION_MANAGER_URL"),
        AUTH_PAYLOAD,
        SESSION_MANAGER_PAYLOAD,
        os.getenv("AUTH_BASIC_AUTH_HEADER")
    )

    tester = APITester(config)
    tester.authenticate()
    # tester.test_apis()
