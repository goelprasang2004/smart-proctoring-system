import requests
import json
import datetime

BASE_URL = 'http://localhost:5000/api'

def print_step(msg):
    print(f"\n[STEP] {msg}")

def run_verification():
    session = requests.Session()

    # 1. Login as Admin
    print_step("Logging in as Admin...")
    resp = session.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@gmail.com",
        "password": "StrongPassword123!"
    })
    if resp.status_code != 200:
        print(f"Admin login failed: {resp.text}")
        return
    
    admin_token = resp.json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    print("Admin logged in.")

    # 2. Create a New Student
    print_step("Creating a new Student...")
    student_email = f"teststudent_{int(datetime.datetime.now().timestamp())}@test.com"
    resp = session.post(f"{BASE_URL}/admin/students", headers=admin_headers, json={
        "email": student_email,
        "password": "password123",
        "full_name": "Test Student Verification"
    })
    if resp.status_code != 201:
        print(f"Student creation failed: {resp.text}")
        return
    
    student_id = resp.json()['student']['id']
    print(f"Student created: {student_email} (ID: {student_id})")

    # 3. Create a New Exam
    print_step("Creating a new Exam...")
    start_time = (datetime.datetime.now() + datetime.timedelta(minutes=5)).isoformat()
    end_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()
    
    resp = session.post(f"{BASE_URL}/exams", headers=admin_headers, json={
        "title": "Verification Exam",
        "description": "Exam to verify assignment flow",
        "start_time": start_time,
        "end_time": end_time,
        "duration_minutes": 60,
        "exam_config": {"questions": []}
    })
    
    if resp.status_code != 201:
        print(f"Exam creation failed: {resp.text}")
        return

    exam_id = resp.json()['exam']['id']
    print(f"Exam created: {exam_id}")

    # 4. Change Status to Scheduled (Default is draft)
    print_step("Changing Exam Status to Scheduled...")
    resp = session.patch(f"{BASE_URL}/exams/{exam_id}/status", headers=admin_headers, json={
        "status": "scheduled"
    })
    if resp.status_code != 200:
        print(f"Status update failed: {resp.text}")
        return
    print("Exam status updated to 'scheduled'.")

    # 5. Assign Exam to Student
    print_step("Assigning Exam to Student...")
    resp = session.post(f"{BASE_URL}/exams/{exam_id}/assign", headers=admin_headers, json={
        "student_ids": [student_id]
    })
    if resp.status_code != 200:
        print(f"Assignment failed: {resp.text}")
        return
    
    # Check assignment result
    result = resp.json()
    if len(result['success']) > 0:
        print("Assignment successful.")
    else:
        print(f"Assignment returned no success: {result}")
        return

    # 6. Login as Student
    print_step("Logging in as Student...")
    resp = session.post(f"{BASE_URL}/auth/login", json={
        "email": student_email,
        "password": "password123"
    })
    if resp.status_code != 200:
        print(f"Student login failed: {resp.text}")
        return
    
    student_token = resp.json()['access_token']
    student_headers = {'Authorization': f'Bearer {student_token}'}
    print("Student logged in.")

    # 7. Get Available Exams
    print_step("Fetching Available Exams for Student...")
    resp = session.get(f"{BASE_URL}/exams/available", headers=student_headers)
    
    if resp.status_code != 200:
        print(f"Fetch failed: {resp.text}")
        return

    data = resp.json()
    print("Response from /exams/available:")
    print(json.dumps(data, indent=2))

    # Check if exam is present
    exams = data.get('exams') if 'exams' in data else data # Handle both formats just in case
    if isinstance(exams, list) and any(e.get('id') == exam_id for e in exams):
        print("\nSUCCESS: The assigned exam is visible in the student response.")
    elif isinstance(exams, list) and any(e.get('exam_id') == exam_id for e in exams):
        print("\nSUCCESS: The assigned exam is visible (but check 'id' field).")
    else:
        print("\nFAILURE: The assigned exam is NOT visible in the student response.")

if __name__ == "__main__":
    run_verification()
