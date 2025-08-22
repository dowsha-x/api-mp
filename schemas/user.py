import phonenumbers
from pydantic import BaseModel, EmailStr, SecretStr, field_validator, validator


class UserCreate(BaseModel):
    """
    Схема для создания пользователя с валидацией пароля и телефона.

    Поля:
    - name: имя пользователя
    - email: email пользователя
    - phone: телефон пользователя (валидируется по формату)
    - password: пароль пользователя (минимум 8 символов)
    """
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
                raise ValueError('Неверный номер телефона')
        except Exception as e:
            raise ValueError('Неверный формат номера телефона') from e
        return v


class UserRead(BaseModel):
    """
    Схема пользователя для ответа API.

    Поля:
    - id: уникальный идентификатор пользователя
    - name: имя пользователя
    - email: email пользователя
    - phone: телефон пользователя
    - is_superuser: флаг суперпользователя
    """
    id: int
    name: str
    email: EmailStr
    phone: str
    is_superuser: bool

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class UserLogin(BaseModel):
    """
    Схема для логина пользователя.

    Поля:
    - email: email пользователя
    - password: пароль пользователя
    """
    email: EmailStr
    password: SecretStr
