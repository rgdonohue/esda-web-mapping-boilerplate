from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_active_user
)
from app.core.exceptions import AuthenticationError
from app.db.session import get_db
from app.models.user import User, UserCreate, UserInDB
from app.api.v1.base import BaseAPIRouter

router = BaseAPIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Register a new user."""
    # Check if user exists
    existing_user = await db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=user_in.is_active
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Login user and return access token."""
    user = await db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AuthenticationError("Incorrect email or password")
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Refresh access token."""
    access_token = create_access_token({"sub": str(current_user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/password-reset")
async def request_password_reset(
    email: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Request password reset."""
    user = await db.query(User).filter(User.email == email).first()
    if user:
        # In a real application, you would send an email with the reset token
        # For now, we'll just return a success message
        return {"message": "Password reset email sent"}
    return {"message": "Password reset email sent"}

@router.post("/password-reset/{token}")
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Reset password using token."""
    email = verify_password_reset_token(token)
    if not email:
        raise AuthenticationError("Invalid or expired token")
    
    user = await db.query(User).filter(User.email == email).first()
    if not user:
        raise AuthenticationError("User not found")
    
    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    
    return {"message": "Password updated successfully"}

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user."""
    return current_user 