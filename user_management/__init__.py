"""User management module."""
import os

import requests
from jwcrypto.jwk import JWK






def get_url_for_role(role: str, endpoint: str) -> str:
    """Return correct platform url according to role who is asking."""
    url = os.getenv(f"BASE_URL_{role.upper()}") or os.environ["BASE_URL"]
    return url + endpoint


rsa_key = JWK(**requests.get(os.environ["FASTAPI_USERS_RSA_KEY_URL"], timeout=10).json()["keys"][0])
private_key: str = rsa_key.export_to_pem(private_key=True, password=None)