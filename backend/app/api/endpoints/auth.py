from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()

@router.post("/login/access-token")
def login_access_token(
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    print(f"Login attempt with username: {form_data.username}")
    user = AuthService.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    print(f"User authenticated: {user is not None}")
    if not user:
        print("Authentication failed: Incorrect email or password")
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        print(f"Authentication failed: User {user.email} is not active")
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value if hasattr(user.role, 'value') else user.role
        }
    }
