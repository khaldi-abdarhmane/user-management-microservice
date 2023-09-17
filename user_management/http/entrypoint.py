"""http entrypoint file."""
from uuid import UUID


from fastapi import  FastAPI
from fastapi_users import  FastAPIUsers
from sqlalchemy.future import select
from sqlalchemy_utils import register_composites
from user_management.models import  Role, User
from user_management.schemas import (

    DanticBaseUser, DanticUserModel, DanticBaseUserUpdate, DanticBaseUserCreate)
from user_management.http.config import _conn, async_session_maker, get_db, settings
from user_management.http.utils.backend import auth_backend
from user_management.http.utils.user_manager import get_user_manager, UserManager


app = FastAPI()


@app.on_event("startup")
async def startup() -> None:
    """Connect to database at app startup required for fastapi_users, and create roles."""
    async with async_session_maker() as session:
        for role_name in settings.available_roles:
            statement = select(Role).where(Role.name == role_name.lower())
            if not ((await session.execute(statement)).first()):
                session.add(Role(name=role_name.lower()))
                await session.commit()
    register_composites(_conn)


fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])
auth_router = fastapi_users.get_auth_router(auth_backend, requires_verification=True)
verify_router = fastapi_users.get_verify_router(DanticBaseUser)
users_router = fastapi_users.get_users_router(
    user_schema=DanticUserModel, user_update_schema=DanticBaseUserUpdate, requires_verification=True
)

URL_PREFIX = "/auth"


app.include_router(
    auth_router,
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(
        user_schema=DanticUserModel,
        user_create_schema=DanticBaseUserCreate,
    ),
    prefix=URL_PREFIX,
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix=URL_PREFIX,
    tags=["auth"],
)
app.include_router(
    verify_router,
    prefix=URL_PREFIX,
    tags=["auth"],
)
app.include_router(users_router, prefix="/users", tags=["users"])

settings.init_app(app)