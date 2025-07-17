from sqlalchemy import Column, Integer, String, Boolean
from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_superuser = Column(Boolean, default=False)
