"""
Test script to diagnose login issue
"""
from models.user import User
from services.auth_service import AuthService

# Test credentials
test_email = "admin@gmail.com"
test_password = "StrongPassword123!"

print("=" * 60)
print("LOGIN DIAGNOSTIC TEST")
print("=" * 60)

# 1. Find user
print(f"\n1. Looking for user: {test_email}")
user = User.find_by_email(test_email)

if not user:
    print("   [X] User not found!")
    exit(1)

print(f"   [OK] User found: {user['full_name']}")
print(f"   - Role: {user['role']}")
print(f"   - Active: {user['is_active']}")
print(f"   - Password hash (first 20 chars): {user['password_hash'][:20]}...")

# 2. Test password verification
print(f"\n2. Testing password: '{test_password}'")
is_valid = AuthService.verify_password(test_password, user['password_hash'])
print(f"   Password verification result: {is_valid}")

if not is_valid:
    print("   [X] PASSWORD DOES NOT MATCH!")
    print("\n   This is the problem. The password in the database doesn't match.")
    print("   You need to either:")
    print("   1. Use the correct password")
    print("   2. Re-run setup_db.py to reset the password")
else:
    print("   [OK] Password is correct!")

# 3. Test full login flow
if is_valid:
    print(f"\n3. Testing full login flow")
    try:
        result = AuthService.login_user(test_email, test_password)
        print("   [OK] Login successful!")
        print(f"   - User ID: {result['user']['id']}")
        print(f"   - Access token (first 30 chars): {result['access_token'][:30]}...")
    except Exception as e:
        print(f"   [X] Login failed: {e}")

print("\n" + "=" * 60)
