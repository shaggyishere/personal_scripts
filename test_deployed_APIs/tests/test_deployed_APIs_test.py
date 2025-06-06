import os

from unittest.mock import patch
from test_deployed_APIs import get_dot_env_file_name, clear_env, load_configurations, check_config_variables, retrieve_configs_from_env_file
from api_tester_config import APITesterConfig

def test_get_dot_env_file_name():
    # given
    microservice = "ms"
    env = "dev"

    # when
    res = get_dot_env_file_name(microservice, env)

    # then
    assert res == f".env.{microservice}.{env}"

@patch("test_deployed_APIs.dotenv_values")
@patch.dict(os.environ, {"VAR1": "123", "VAR2": "456", "VAR3": "789"}, clear=True)
def test_clear_env(mock_dotenv_values):
    # given
    mock_dotenv_values.return_value = {
        "VAR1": "value1",
        "VAR2": "value2"
    }

    # when
    clear_env("ms", "dev", "fake_path")

    # then
    assert "VAR1" not in os.environ
    assert "VAR2" not in os.environ
    assert "VAR3" in os.environ

@patch("os.path.exists")
@patch("test_deployed_APIs.load_dotenv")
def test_load_configurations_correctly(mock_path_exists, mock_load_env):
    # given
    mock_path_exists.return_value = True
    mock_load_env.return_value = True

    # when
    res = load_configurations("ms", "dev", "fake_path")

    # then
    assert res == True
    
@patch("os.path.exists")
def test_load_configurations_not_found(mock_path_exists):
    # given
    mock_path_exists.return_value = False

    # when
    res = load_configurations("ms", "dev", "fake_path")

    # then
    assert res == False

@patch.dict(os.environ, {
    "BASE_URL": "fake_data",
    "AUTH_URL": "fake_data",
    "SESSION_MANAGER_URL": "fake_data",
    "AUTH_PAYLOAD": "fake_data",
    "AUTH_BASIC_AUTH_HEADER": "fake_data",
    "SESSION_MANAGER_PAYLOAD": "fake_data"
    }, clear=True)
def test_check_config_variables_normal_ms_correctly():
    # when
    res = check_config_variables("ms", "dev")

    # then
    assert res == True
    
@patch.dict(os.environ, {
    "BASE_URL": "fake_data",
    "SESSION_MANAGER_URL": "fake_data",
    "AUTH_BASIC_AUTH_HEADER": "fake_data",
    "SESSION_MANAGER_PAYLOAD": "fake_data"
    }, clear=True)
def test_check_config_variables_normal_ms_env_vars_not_defined():
    # when
    res = check_config_variables("ms", "dev")

    # then
    assert res == False

@patch.dict(os.environ, {
    "BASE_URL": "fake_data",
    "AUTH_URL": "fake_data",
    "SESSION_MANAGER_URL": "fake_data",
    "AUTH_PAYLOAD": "fake_data",
    "AUTH_BASIC_AUTH_HEADER": "fake_data",
    "GOLIA_SESSION_MANAGER_CREATE_PAYLOAD": "fake_data",
    "GOLIA_SESSION_MANAGER_UPDATE_PAYLOAD": "fake_data"
    }, clear=True)
def test_check_config_variables_golia_correctly():
    # when
    res = check_config_variables("golia", "dev")

    # then
    assert res == True

@patch.dict(os.environ, {
    "BASE_URL": "fake_data",
    "SESSION_MANAGER_URL": "fake_data",
    "AUTH_BASIC_AUTH_HEADER": "fake_data",
    "SESSION_MANAGER_PAYLOAD": "fake_data",
    "GOLIA_SESSION_MANAGER_CREATE_PAYLOAD": "fake_data"
    }, clear=True)
def test_check_config_variables_golia_env_vars_not_defined():
    # when
    res = check_config_variables("golia", "dev")

    # then
    assert res == False

@patch.dict(os.environ, {
    "BASE_URL": "fake_data",
    "AUTH_URL": "fake_data",
    "SESSION_MANAGER_URL": "fake_data",
    "AUTH_PAYLOAD": '{"fake_field": "fake_value"}',
    "AUTH_BASIC_AUTH_HEADER": "fake_data",
    "SESSION_MANAGER_PAYLOAD": '{"fake_field": "fake_value"}'
    }, clear=True)
def test_retrieve_configs_from_env_file():
    # given

    # when
    res = retrieve_configs_from_env_file()

    # then
    assert res == APITesterConfig(
        "fake_data",
        "fake_data",
        "fake_data",
        {"fake_field": "fake_value"},
        {"fake_field": "fake_value"},
        {},
        {},
        "fake_data"
    )