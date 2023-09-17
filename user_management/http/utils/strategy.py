"""Custom strategy."""
from typing import Any
from uuid import UUID

import jwt
from fastapi_users import BaseUserManager, exceptions
from fastapi_users.authentication import Strategy
from fastapi_users.authentication.strategy import StrategyDestroyNotSupportedError
from fastapi_users.jwt import decode_jwt, generate_jwt, SecretType
from user_management.models import User


class JWTStrategy(Strategy[User, UUID]):
    """Custom startegy."""

    def __init__(
        self,
        secret: SecretType,
        lifetime_seconds: int | None,
        token_audience: list[str] | None = None,
        algorithm: str = "RS256",
        public_key: SecretType | None = None,
    ):
        """Init file."""
        if not token_audience:
            self.token_audience = ["fastapi-users:auth"]
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds
        self.algorithm = algorithm
        self.public_key = public_key

    @property
    def encode_key(self) -> SecretType:
        """Encode key."""
        return self.secret

    @property
    def decode_key(self) -> SecretType:
        """Decode key."""
        return self.public_key or self.secret

    async def read_token(
        self, token: str | None, user_manager: BaseUserManager[User, UUID]
    ) -> User | None:
        """Read token."""
        if token is None:
            return None

        try:
            data = decode_jwt(
                token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
            )
            if (user_id := data.get("id")) is None:
                return None
        except jwt.PyJWTError:
            return None

        try:
            parsed_id = user_manager.parse_id(user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(self, user: User, customer_id: int | None = None) -> str:
        """Write token."""
        data: dict[str, Any] = {"id": str(user.id), "aud": self.token_audience, "role": user.role}
        if customer_id:
            data = {**data, "customer_id": customer_id}
        return generate_jwt(data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm)

    async def destroy_token(self, token: str, user: User) -> None:
        """Destroy token."""
        raise StrategyDestroyNotSupportedError(
            "A JWT can't be invalidated: it's valid until it expires."
        )