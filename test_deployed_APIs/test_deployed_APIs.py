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
        logging.FileHandler("api_test.log")
    ]
)

def load_configurations(microservice, env_name, script_dir):
    dot_env_file_name = f".env.{microservice}.{env_name}"
    dot_env_file_path = os.path.join(script_dir, "api_configs", dot_env_file_name)
    
    if not os.path.exists(dot_env_file_path):
        print(f"Error: Environment file '{dot_env_file_name}' not found!")
        sys.exit(1)
    
    load_dotenv(dot_env_file_path)

def check_config_variables(microservice):
    required_env_vars = ["BASE_URL", "AUTH_URL", "SESSION_MANAGER_URL", "AUTH_PAYLOAD", "AUTH_BASIC_AUTH_HEADER"]

    # two different env vars are valued if microservice is golia or the other ones
    required_env_vars += ["GOLIA_SESSION_MANAGER_CREATE_PAYLOAD", "GOLIA_SESSION_MANAGER_UPDATE_PAYLOAD"] if microservice == "golia" else ["SESSION_MANAGER_PAYLOAD"]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("usage: python test_deployed_APIs.py <microservice> <environment>")
        sys.exit(1)

    microservice= sys.argv[1]
    env = sys.argv[2]
    script_dir = os.path.dirname(os.path.abspath(__file__)) 

    load_configurations(microservice, env, script_dir)

    check_config_variables(microservice)

    auth_payload_str = os.getenv("AUTH_PAYLOAD")
    session_manager_payload_str = os.getenv("SESSION_MANAGER_PAYLOAD")
    golia_session_manager_create_payload_str = os.getenv("GOLIA_SESSION_MANAGER_CREATE_PAYLOAD")
    golia_session_manager_update_payload_str = os.getenv("GOLIA_SESSION_MANAGER_UPDATE_PAYLOAD")
    AUTH_PAYLOAD =  json.loads(auth_payload_str) if auth_payload_str else {}
    SESSION_MANAGER_PAYLOAD =  json.loads(session_manager_payload_str) if session_manager_payload_str else {}
    GOLIA_SESSION_MANAGER_CREATE_PAYLOAD =  json.loads(golia_session_manager_create_payload_str) if golia_session_manager_create_payload_str else {}
    GOLIA_SESSION_MANAGER_UPDATE_PAYLOAD =  json.loads(golia_session_manager_update_payload_str) if golia_session_manager_update_payload_str else {}

    configs = APITesterConfig(
        os.getenv("BASE_URL"),
        os.getenv("AUTH_URL"),
        os.getenv("SESSION_MANAGER_URL"),
        AUTH_PAYLOAD,
        SESSION_MANAGER_PAYLOAD,
        GOLIA_SESSION_MANAGER_CREATE_PAYLOAD,
        GOLIA_SESSION_MANAGER_UPDATE_PAYLOAD,
        os.getenv("AUTH_BASIC_AUTH_HEADER")
    )

    api_tester = APITester(configs, script_dir, microservice, env)
    api_tester.authenticate()
    api_tester.create_session()
    api_tester.test_apis()
