from dataclasses import dataclass

@dataclass
class APITesterConfig:
    base_url: str
    auth_url: str
    session_manager_url: str
    auth_payload: dict
    session_manager_payload: dict
    golia_session_manager_create_payload: dict
    golia_session_manager_update_payload: dict
    auth_basic_auth_header: str