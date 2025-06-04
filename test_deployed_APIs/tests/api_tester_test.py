import pytest
import requests
import requests_mock

from api_tester import APITester
from api_tester_config import APITesterConfig


@pytest.mark.usefixtures("requests_mock")
class TestAPITester:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.config = APITesterConfig (
            "https://example.com",
            "https://example.com/auth",
            "https://example.com/sessionmanager",
            {"username": "user", "password": "pass"},
            {"sessionId": "01"},
            {},
            {},
            "Basic dXNlcjpwYXNz"
        )
        
        self.sut = APITester(self.config, "", "", "")

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