"""Pydantic schemas for user models. Need to be defined, check fastapi user doc."""

import os
from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import BaseModel, Extra, Field, validator


enum_elements: dict[str, str] = {}
for element in os.environ["USER_MANAGEMENT_REGISTRABLE_ROLES"].split("|"):
    enum_elements[element] = element

# ignore mypy error https://github.com/python/mypy/issues/5317
EnumRole = Enum("RoleEnum", enum_elements)  # type: ignore


class DanticBirthdate(BaseModel):
    """Birthdate pydentic class."""

    @classmethod
    def __get_validators__(cls) -> Any:
        # Return an iterator of the custom validator method called `validate_birthdate`.
        yield cls.validate_birthdate

    @classmethod
    def validate_birthdate(cls, value: str) -> date:
        """Function to validate birthdate date."""

        try:
            dt = datetime.strptime(value, "%d/%m/%Y").date()
        except ValueError as error:
            raise ValueError("Format de la date invalide, DD/MM/YYYY attendu.") from error

        if dt > date.today():
            raise ValueError("La date de naissance ne peut être dans le futur.")

        return dt


class DanticLastVisit(BaseModel):
    """Last visit schema."""

    last_visited_at: datetime

    @validator("last_visited_at", pre=True)
    @classmethod
    def dt_validate(cls, last_visited_at: str) -> datetime:
        """Datetime validation for last_visited_at, it accepts only ISO format."""
        # Tzinfo=none removes timezone from the ISO string.

        return datetime.fromisoformat(last_visited_at).replace(tzinfo=None)


class CivilityEnum(str, Enum):
    """Civility Enum for front input validation."""

    mr = "Mr"
    mrs = "Mrs"


class PydanticApiToken(BaseModel):
    """API token schema."""

    access_token: str
    token_type: str
    expires_in: int


class DanticAddress(BaseModel):
    """Address model."""

    name: str
    address_addition: str | None
    zip_code: str
    city: str
    country: str
    lat: float
    lng: float
    extra_data: dict[str, Any] | None

    class Config:
        """Config for DanticAddress pydantic base config."""

        orm_mode = True


class DanticBaseUser(BaseUser[UUID]):
    """Base user pydantic model."""

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    first_name: str | None
    last_name: str | None
    civility: CivilityEnum | None
    phone: str
    address: DanticAddress | None
    role: str  # we use str instead of RoleEnum because we can return non registreable roles
    company_name: str | None
    siren: str | None = Field(max_length=9)

    class Config:
        """Config for DanticBaseUser pydantic base config."""

        orm_mode = True
        use_enum_values = True


class DanticBaseUserCreate(BaseUserCreate):
    """Base user create pydantic model."""

    first_name: str | None
    last_name: str | None
    civility: CivilityEnum | None
    phone: str
    role: EnumRole
    address: DanticAddress | None
    company_name: str | None
    siren: str | None = Field(max_length=9)
    birthdate: DanticBirthdate | None

    class Config:
        """Activate enum values to be rendered in dict as value."""

        use_enum_values = True

    @validator("email", "first_name", "last_name")
    @classmethod
    def remove_white_spaces(cls, value: str) -> str:
        """Remove white spaces from field."""

        return value.strip()


class DanticBaseUserUpdate(BaseUserUpdate):
    """Base user update pydantic model."""

    updated_at: datetime = Field(default_factory=datetime.now)
    first_name: str | None
    last_name: str | None
    civility: CivilityEnum | None
    phone: str | None
    address: DanticAddress | None
    company_name: str | None
    siren: str | None = Field(max_length=9)
    birthdate: DanticBirthdate | None

    @validator("email", "first_name", "last_name")
    @classmethod
    def remove_white_spaces(cls, value: str) -> str:
        """Remove white spaces from field."""

        return value.strip()


class BaseUserDB(BaseUser[UUID]):
    """BaseUserDB."""

    class Config:
        """BaseUserDB Config."""

        orm_mode = True


class DanticUserModel(DanticBaseUser, BaseUserDB):
    """User pydantic model."""

    class Config:
        """Config for DanticUserModel pydantic base config."""

        orm_mode = True


class DanticBaseUserOut(BaseUser[UUID]):
    """User Out pydantic model."""

    first_name: str | None
    last_name: str | None

    class Config:
        """Config for DanticUserModel pydantic base config."""

        orm_mode = True


class PydanticCommentIn(BaseModel):
    """Address pydantic base."""

    message: str = Field(...)

    class Config:
        """Config for comment pydantic base config."""

        extra = Extra.forbid
        orm_mode = True


class PydanticCommentOut(BaseModel):
    """Client pydantic base."""

    id: int
    created_at: datetime
    message: str = Field(...)

    class Config:
        """Config for comment pydantic base config."""

        extra = Extra.forbid
        orm_mode = True


class PydanticActivation(BaseModel):
    """Activation pydantic base."""

    user_id: str
    inscription_accepted: bool

    class Config:
        """Config for Activation pydantic base config."""

        extra = Extra.forbid


class PydanticAddNotificationDeviceDataIn(BaseModel):
    """Address pydantic base."""

    device_token: str

    class Config:
        """Config for comment pydantic base config."""

        extra = Extra.forbid
        orm_mode = True