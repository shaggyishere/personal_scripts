import pytest
import requests
import requests_mock
import os
from unittest.mock import patch, call, mock_open

from api_tester import APITester
from api_tester_config import APITesterConfig


@pytest.mark.usefixtures("requests_mock")
class TestAPITester:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.config = APITesterConfig (
            "https://example.com",
            "https://example.com/auth",
            "https://sessionmanager.com",
            {"username": "user", "password": "pass"},
            {},
            {},
            {},
            "Basic dXNlcjpwYXNz"
        )
        
        self.sut = APITester(self.config, "fake_dir.json", "ms", "dev")

    def test_authenticate_success(self, requests_mock):
        
        # given
        requests_mock.post(self.config.auth_url, json={"access_token": "mocked-token"})

        # when
        self.sut.authenticate()

        # then
        assert self.sut.token == "mocked-token"
        assert self.sut.session.headers["Authorization"] == "Bearer mocked-token"

    def test_authenticate_missing_token_raises(self, requests_mock):
        
        # given
        requests_mock.post(self.config.auth_url, json={})

        # when & then
        with pytest.raises(ValueError, match="No access_token"):
            self.sut.authenticate()

    def test_authenticate_http_error(self, requests_mock):

        # given
        requests_mock.post(self.config.auth_url, status_code=401, json={"error": "unauthorized"})

        # when & then
        with pytest.raises(requests.exceptions.HTTPError):
            self.sut.authenticate()

    def test_create_session_success(self, requests_mock):
        
        # given
        requests_mock.post(self.config.session_manager_url, json={"sessionId": "mocked-sessionId"})

        # when
        self.sut.create_session()

        # then
        assert self.sut.session_id == "mocked-sessionId"
        assert self.sut.session.headers["X-BEAR-SESSION-TOKEN"] == "mocked-sessionId"

    def test_create_session_missing_sessionId_raises(self, requests_mock):
        
        # given
        requests_mock.post(self.config.session_manager_url, json={})

        # when & then
        with pytest.raises(ValueError, match="No sessionId"):
            self.sut.create_session()

    def test_create_session_http_error(self, requests_mock):

        # given
        requests_mock.post(self.config.session_manager_url, status_code=401, json={"error": "unauthorized"})

        # when & then
        with pytest.raises(requests.exceptions.HTTPError):
            self.sut.create_session()

    def test_create_session_golia_success(self, requests_mock):
        
        # given
        self.sut = APITester(self.config, "", "golia", "")

        mockedSessionId = "mocked-sessionId"

        requests_mock.post(
            f"{self.config.session_manager_url}/api/session",
            json={"payload": mockedSessionId}
        )

        requests_mock.post(
            f"{self.config.session_manager_url}/api/session/customer/{mockedSessionId}",
            status_code = 200,
            json={"operation": "success"}
        )

        # when
        self.sut.create_session()

        # then
        assert self.sut.session_id == "mocked-sessionId"
        assert self.sut.session.headers["X-BEAR-SESSION-TOKEN"] == "mocked-sessionId"    

    def test_create_session_golia_missing_sessionId_raises(self, requests_mock):
        
        # given
        self.sut = APITester(self.config, "", "golia", "")

        requests_mock.post(
            f"{self.config.session_manager_url}/api/session", 
            json={}
        )

        # when & then
        with pytest.raises(ValueError, match="No sessionId"):
            self.sut.create_session()
    
    def test_create_session_golia_http_error(self, requests_mock):

        # given
        self.sut = APITester(self.config, "", "golia", "")

        mockedSessionId = "mocked-sessionId"

        requests_mock.post(
            f"{self.config.session_manager_url}/api/session",
            json={"payload": mockedSessionId}
        )

        requests_mock.post(
            f"{self.config.session_manager_url}/api/session/customer/{mockedSessionId}",
            status_code = 500,
            json={"operation": "error"}
        )

        # when & then
        with pytest.raises(requests.exceptions.HTTPError):
            self.sut.create_session()

    def test_call_apis_and_save_results(self):

        # given
        mock_apis = [{"endpoint": "/api1"}, {"endpoint": "/api2"}, {"endpoint": "/api3"}]
        response_time_for_single_api = 4.0

        with patch.object(self.sut, "_load_apis_to_test", return_value=mock_apis) as mock_load_apis, \
            patch.object(self.sut, "_call_single_api_and_store_response", return_value=response_time_for_single_api) as mock_call_single_api, \
            patch.object(self.sut, "_save_results_into_file") as mock_save_results:


            # when
            res = self.sut.call_apis_and_save_results()


            # then
            mock_load_apis.assert_called_once()

            assert mock_call_single_api.call_count == len(mock_apis)

            assert mock_save_results.call_count == 2
            expected_calls = [
                call(f"api_responses_ms_dev.json", self.sut.results),
                call(f"api_status_ms_dev.json", self.sut.status_log)
            ]
            mock_save_results.assert_has_calls(expected_calls, any_order=False)
            
            assert res == response_time_for_single_api * len(mock_apis)
    
    def test_load_apis_to_test(self):
        # given
        mock_file = '[{"endpoint": "/api1", "method": "GET"}, {"endpoint": "/api2", "method": "GET"}]'

        with patch("builtins.open", mock_open(read_data=mock_file)):
            # when
            res = self.sut._load_apis_to_test()

            # then
            assert res == [{"endpoint": "/api1", "method": "GET"}, {"endpoint": "/api2", "method": "GET"}]

    def test_call_single_api_and_store_response_success(self, requests_mock):
        # given
        mock_api_info = {
            "method": "GET",
            "route": "/api",
            "query_params": {"param": "value"}
        }
        mock_response = {"field1": "value1"}
        mock_status_code = 200

        requests_mock.get(
            f"{self.config.base_url.rstrip('/')}{mock_api_info['route']}",
            status_code = mock_status_code,
            json=mock_response
        )

        # when
        res = self.sut._call_single_api_and_store_response(mock_api_info)

        # then
        assert self.sut.results == {
            "microservice": "ms",
            "env": "dev",
            "/api": {
                "query_param": mock_api_info["query_params"],
                "request_body": {},
                "status_code": mock_status_code,
                "response_time_sec": res,
                "response": mock_response
            }
        }

        assert self.sut.status_log == {
            "microservice": "ms",
            "env": "dev",
            "200": ["/api"],
            "500": [],
            "Other": {}
        }

    def test_call_single_api_and_store_response_internal_server_error(self, requests_mock):
        # given
        mock_api_info = {
            "method": "POST",
            "route": "/broken",
            "body": {"field1": "value1"},
        }
        mock_response = {"error": "internal server error"}
        mock_status_code = 500

        requests_mock.post(
            f"{self.config.base_url.rstrip('/')}{mock_api_info['route']}",
            status_code = mock_status_code,
            json=mock_response
        )

        # when
        res = self.sut._call_single_api_and_store_response(mock_api_info)

        # then
        assert self.sut.results == {
            "microservice": "ms",
            "env": "dev",
            "/broken": {
                "query_param": {},
                "request_body": mock_api_info["body"],
                "status_code": mock_status_code,
                "response_time_sec": res,
                "response": mock_response
            }
        }

        assert self.sut.status_log == {
            "microservice": "ms",
            "env": "dev",
            "200": [],
            "500": ["/broken"],
            "Other": {}
        }
    
    def test_call_single_api_and_store_response_other_error(self, requests_mock):
        # given
        mock_api_info = {
            "method": "POST",
            "route": "/other-error",
            "body": {"field1": "value1"},
        }
        mock_response = {"error": "not found error"}
        mock_status_code = 404

        requests_mock.post(
            f"{self.config.base_url.rstrip('/')}{mock_api_info['route']}",
            status_code = mock_status_code,
            json=mock_response
        )

        # when
        res = self.sut._call_single_api_and_store_response(mock_api_info)

        # then
        assert self.sut.results == {
            "microservice": "ms",
            "env": "dev",
            "/other-error": {
                "query_param": {},
                "request_body": mock_api_info["body"],
                "status_code": mock_status_code,
                "response_time_sec": res,
                "response": mock_response
            }
        }

        assert self.sut.status_log == {
            "microservice": "ms",
            "env": "dev",
            "200": [],
            "500": [],
            "Other": {
                "/other-error" :"404"
            }
        }
    
    def test_call_single_api_and_store_raise_exception(self, requests_mock):
        # given
        mock_api_info = {
            "method": "GET",
            "route": "/other-error",
            "query_param": {"param1": "value1"},
        }
        mock_error_message = "Connection failed"

        requests_mock.get(
            f"{self.config.base_url.rstrip('/')}{mock_api_info['route']}",
            exc=requests.exceptions.ConnectionError(mock_error_message)
        )

        # when
        self.sut._call_single_api_and_store_response(mock_api_info)

        # then
        assert mock_api_info['route'] in self.sut.results
        assert "Connection failed" in self.sut.results[mock_api_info['route']]["error"]

    def test_save_results_into_file(self):
        # given
        mock_filename = "fake_file_name.json"
        mock_data = '{"fake": "data"}'
        file_path = os.path.join("api_results", mock_filename)


        with patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", mock_open()) as mock_file, \
         patch("json.dump") as mock_json_dump:

            # when
            self.sut._save_results_into_file (
                mock_filename,
                mock_data
            )

            # then
            mock_file.assert_called_once_with(file_path, "w")
            mock_json_dump.assert_called_once_with(mock_data, mock_file(), indent=4)


