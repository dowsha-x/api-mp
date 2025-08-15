from pydantic import BaseModel, EmailStr, SecretStr, field_validator, validator
import phonenumbers


class UserCreate(BaseModel):
    """Схема для создания пользователя с валидацией пароля."""
    name: str
    email: EmailStr
    phone: str
    password: SecretStr

    @field_validator('password')
    def validate_password(cls, v):
        if len(v.get_secret_value()) < 8:
            raise ValueError("Пароль должен быть минимум 8 символов")
        return v

    model_config = {
        "arbitrary_types_allowed": True
    }

    @validator('phone')
    def validate_phone(cls, v):
        try:
            p = phonenumbers.parse(v, 'RU')
            if not phonenumbers.is_valid_number(p):
                raise ValueError('Invalid phone number')
        except Exception:
            raise ValueError('Invalid phone number format')
        return v


class UserRead(BaseModel):
    """Схема пользователя для ответа."""
    id: int
    name: str
    email: EmailStr
    phone: str
    is_superuser: bool

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class UserLogin(BaseModel):
    """Схема для логина пользователя."""
    email: EmailStr
    password: SecretStr
