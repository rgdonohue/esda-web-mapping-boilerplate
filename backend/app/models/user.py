from typing import Optional
from sqlalchemy import Boolean, Column, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, EmailStr, constr
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserBase(BaseModel):
    """Base user model with common attributes."""
    email: EmailStr
    full_name: constr(min_length=2, max_length=100)
    role: UserRole = UserRole.USER
    is_active: bool = True

class UserCreate(UserBase):
    """User creation model."""
    password: constr(min_length=8, max_length=100)

class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    full_name: Optional[constr(min_length=2, max_length=100)] = None
    password: Optional[constr(min_length=8, max_length=100)] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    """User model for database operations."""
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserBase):
    """User model for API responses."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserDB(Base):
    """SQLAlchemy user model."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<User {self.email}>" 