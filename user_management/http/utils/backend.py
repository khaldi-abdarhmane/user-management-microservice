"""Custome Backend."""
import logging
from typing import Any
from uuid import UUID

from fastapi import Response
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from myem_lib.nameko_settings_mixins import NetworkClusterRpcClient
from nameko.exceptions import RemoteError
from user_management.models import User
from user_management.http.config import settings
from user_management.http.utils.strategy import JWTStrategy


class CustomAuthenticationBackend(AuthenticationBackend[User, UUID]):
    """Custom authentication backend."""

    # here we are forced to violate the Liskov substitution principle because the parent class
    # of CustomAuthenticationBackend accept only the parent class of JWTStrategy witch is
    # not the case of us
    async def login(  # type: ignore
        self,
        strategy: JWTStrategy,
        user: User,
        response: Response,
    ) -> Any:
        """Login based on role."""
        customer_id = None
        if user.role in settings.customer_roles:
            with NetworkClusterRpcClient() as network_rpc:
                logging.warning(
                    f"Checking if {user.id} has associated customer and housing created."
                )
                try:
                    customer_id = network_rpc.customer_center_service.verify_user_essentials(
                        str(user.id), dict(user.address) if user.address else {}
                    )
                except RemoteError:
                    logging.error(f"Error while checking customer related to user: {user.id}")
                if not customer_id:
                    raise Exception(
                        f"User with first name: {user.first_name}, last name: {user.last_name}, email: {user.email} "
                        f"and id: {user.id} doesn't exists in customer center user table !"
                    )
        token = await strategy.write_token(user, customer_id)
        bearer_response = await self.transport.get_login_response(token, response)
        login_response: dict[str, Any] = {
            **bearer_response.dict(),
            "expires_in": strategy.lifetime_seconds,
        }

        if user.role in settings.available_roles and user.role not in settings.api_roles:
            login_response = {
                **login_response,
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "civility": user.civility,
                "phone": user.phone,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "role": user.role,
                "address": user.address,
                "company_name": user.company_name,
                "siren": user.siren,
                "last_visited_at": user.last_visited_at,
                "birthdate": user.birthdate,
            }

        if user.role in settings.customer_roles:
            return {
                **login_response,
                "customer_id": customer_id,
            }

        return login_response


def get_jwt_strategy() -> JWTStrategy:
    """Jwt strategy function."""
    return JWTStrategy(
        algorithm="RS256",
        secret=settings.private_key,
        public_key=settings.public_key,
        lifetime_seconds=settings.token_expiration_in_seconds,
    )


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

auth_backend = CustomAuthenticationBackend(
    name="application_backend",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)