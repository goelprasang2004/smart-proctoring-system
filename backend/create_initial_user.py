from app.core.database import SessionLocal, engine, Base

from app.models.user import User, UserRole
from app.models.exam import Exam, ExamAttempt
from app.models.proctoring import ProctoringLog
from app.models.blockchain import BlockchainBlock

from app.core.security import get_password_hash
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

def create_user():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Create admin user
    admin_email = "admin@gmail.com"
    admin_password = "StrongPassword123!"
    
    existing = db.query(User).filter(User.email == admin_email).first()
    if not existing:
        user = User(
            full_name="Admin User",
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(user)
        db.commit()
        print(f"Created user: {admin_email} / {admin_password}")
    else:
        print(f"User {admin_email} already exists.")
    
    # Create student user
    student_email = "student@example.com"
    student_password = "TestStudent123!"
    
    existing = db.query(User).filter(User.email == student_email).first()
    if not existing:
        user = User(
            full_name="Test Student",
            email=student_email,
            hashed_password=get_password_hash(student_password),
            role=UserRole.STUDENT,
            is_active=True
        )
        db.add(user)
        db.commit()
        print(f"Created user: {student_email} / {student_password}")
    else:
        print(f"User {student_email} already exists.")

if __name__ == "__main__":
    create_user()
