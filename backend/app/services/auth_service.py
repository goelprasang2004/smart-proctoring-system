from sqlalchemy.orm import Session
from app.models.user import User
from app.core import security

class AuthService:
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> User:
        print(f"AuthService: Looking for user with email: {email}")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"AuthService: User not found with email: {email}")
            return None
        print(f"AuthService: User found: {user.email}, checking password...")
        if not security.verify_password(password, user.hashed_password):
            print(f"AuthService: Password verification failed for user: {email}")
            return None
        print(f"AuthService: Password verified successfully for user: {email}")
        return user
