"""Authentication routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.repository import get_repository
from app.schemas.schemas import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.utils.auth import create_access_token, get_current_user_id, hash_password, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest):
    repo = get_repository()
    email = req.email.lower()
    if repo.get_user_by_email(email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = repo.create_user(email, req.name.strip(), hash_password(req.password))
    token = create_access_token(user["id"], {"email": email})
    return TokenResponse(access_token=token, user_id=user["id"], name=user["name"], email=email)


@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest):
    repo = get_repository()
    user = repo.get_user_by_email(req.email.lower())
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(user["id"], {"email": user["email"]})
    return TokenResponse(access_token=token, user_id=user["id"], name=user["name"], email=user["email"])


@router.get("/me", response_model=UserResponse)
def me(user_id: str = Depends(get_current_user_id)):
    user = get_repository().get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(id=user["id"], email=user["email"], name=user["name"], created_at=user.get("created_at"))
