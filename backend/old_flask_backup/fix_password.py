"""
Fix admin password
"""
from models.user import User
from services.auth_service import AuthService
from models.database import get_db_connection

# New password
new_password = "StrongPassword123!"
admin_email = "admin@gmail.com"

print("=" * 60)
print("FIXING ADMIN PASSWORD")
print("=" * 60)

# Hash the new password
print(f"\n1. Hashing new password: '{new_password}'")
new_hash = AuthService.hash_password(new_password)
print(f"   [OK] New hash created")

# Update in database
print(f"\n2. Updating password for {admin_email}")
try:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET password_hash = %s, updated_at = CURRENT_TIMESTAMP WHERE email = %s",
                (new_hash, admin_email)
            )
            conn.commit()
            print(f"   [OK] Password updated successfully")
except Exception as e:
    print(f"   [X] Error: {e}")
    exit(1)

# Verify the fix
print(f"\n3. Verifying the fix")
user = User.find_by_email(admin_email)
is_valid = AuthService.verify_password(new_password, user['password_hash'])

if is_valid:
    print(f"   [OK] Password verification successful!")
    print(f"\nYou can now login with:")
    print(f"   Email: {admin_email}")
    print(f"   Password: {new_password}")
else:
    print(f"   [X] Verification failed!")

print("\n" + "=" * 60)
