import ipaddress
import os
from dataclasses import dataclass, field
from urllib.parse import urlsplit

import requests


class ConfigurationError(ValueError):
    pass


class JoplinRequestError(RuntimeError):
    pass


@dataclass(frozen=True)
class ApiConfig:
    base_url: str
    token: str = field(repr=False)


def load_config(environ=None):
    environ = os.environ if environ is None else environ
    token = environ.get("JOPLIN_API_TOKEN", "").strip()
    if not token or any(character.isspace() for character in token):
        raise ConfigurationError("Set JOPLIN_API_TOKEN to a nonempty API token without whitespace.")
    base_url = environ.get("JOPLIN_API_URL", "").strip()
    try:
        parsed = urlsplit(base_url)
        port = parsed.port
        hostname = parsed.hostname
        loopback = hostname == "localhost" or ipaddress.ip_address(hostname).is_loopback
    except (ValueError, TypeError):
        raise ConfigurationError("Set JOPLIN_API_URL to an HTTP or HTTPS loopback server origin.") from None
    if (
        not loopback
        or parsed.scheme not in {"http", "https"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
        or port == 0
    ):
        raise ConfigurationError("Set JOPLIN_API_URL to an HTTP or HTTPS loopback server origin.")
    if environ.get("JOPLIN_TEST_PROFILE_ACKNOWLEDGED") != "1":
        raise ConfigurationError(
            "Set JOPLIN_TEST_PROFILE_ACKNOWLEDGED=1 only for a disposable local test profile."
        )
    return ApiConfig(base_url.rstrip("/"), token)


class JoplinTestClient:
    def __init__(self, environ=None):
        self._config = load_config(environ)
        self._session = requests.Session()
        self._session.trust_env = False

    def _request(self, method, path, *, params=None, json=None):
        parsed = urlsplit(path)
        if (
            not path.startswith("/")
            or path.startswith("//")
            or parsed.scheme
            or parsed.netloc
            or parsed.query
            or parsed.fragment
        ):
            raise ConfigurationError("Requests must use local API paths and separate query parameters.")
        query = dict(params or {})
        query.setdefault("token", self._config.token)
        try:
            return self._session.request(
                method,
                self._config.base_url + path,
                params=query,
                json=json,
                timeout=10,
                allow_redirects=False,
            )
        except requests.RequestException as error:
            raise JoplinRequestError(f"Local API request failed ({type(error).__name__}).") from None

    def get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)
