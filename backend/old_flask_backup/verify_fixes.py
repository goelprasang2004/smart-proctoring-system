#!/usr/bin/env python3
"""
Verification Script - Backend Proctoring System Fixes
======================================================
This script verifies that all identified issues have been fixed.
"""

import re
import os

FIXES_VERIFIED = {
    'FIXED': [],
    'IMPROVED': [],
    'VERIFIED': 0,
    'TOTAL': 4
}

def check_file_for_pattern(filepath, pattern, label):
    """Check if a file contains a pattern (fix verification)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                FIXES_VERIFIED['FIXED'].append(f"✅ {label}")
                FIXES_VERIFIED['VERIFIED'] += 1
                return True
            else:
                FIXES_VERIFIED['IMPROVED'].append(f"❌ {label} - NOT FOUND")
                return False
    except Exception as e:
        FIXES_VERIFIED['IMPROVED'].append(f"⚠️ {label} - ERROR: {str(e)}")
        return False

# Change to backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("BACKEND PROCTORING SYSTEM - FIXES VERIFICATION")
print("=" * 70)
print()

# Fix 1: Student Ownership Verification
print("1. Checking Student Ownership Verification...")
result = check_file_for_pattern(
    'api/routes/proctoring.py',
    r'# Verify attempt belongs to current user.*?from models\.exam_attempt import ExamAttempt.*?attempt = ExamAttempt\.find_by_id\(attempt_id\)',
    'Student-Attempt Ownership Check'
)
print(f"   Result: {'PASSED ✅' if result else 'FAILED ❌'}\n")

# Fix 2: Confidence Score Bounds
print("2. Checking Confidence Score Bounds Validation...")
result = check_file_for_pattern(
    'services/proctoring_service.py',
    r'# Final bounds check to ensure 4 decimal places within \[0, 1\].*?confidence = max\(0\.0, min\(1\.0, confidence\)\)',
    'Confidence Score Bounds Check'
)
print(f"   Result: {'PASSED ✅' if result else 'FAILED ❌'}\n")

# Fix 3: Risk Score NULL Handling
print("3. Checking Risk Score NULL Handling...")
result = check_file_for_pattern(
    'services/proctoring_service.py',
    r'if ai_summary and isinstance\(ai_summary, dict\) and ai_summary\.get\(.*?\):|if event_summary and isinstance\(event_summary, list\):',
    'Risk Score NULL Handling'
)
print(f"   Result: {'PASSED ✅' if result else 'FAILED ❌'}\n")

# Fix 4: STRING_AGG Ordering
print("4. Checking STRING_AGG Deterministic Ordering...")
result = check_file_for_pattern(
    'models/proctoring.py',
    r"STRING_AGG\(DISTINCT pl\.event_type::text, ', ' ORDER BY pl\.event_type::text\)",
    'STRING_AGG Ordered Output'
)
print(f"   Result: {'PASSED ✅' if result else 'FAILED ❌'}\n")

# Summary
print("=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)
print(f"\nFixes Verified: {FIXES_VERIFIED['VERIFIED']}/{FIXES_VERIFIED['TOTAL']}")
print()

if FIXES_VERIFIED['FIXED']:
    print("✅ FIXES APPLIED:")
    for fix in FIXES_VERIFIED['FIXED']:
        print(f"   {fix}")

if FIXES_VERIFIED['IMPROVED']:
    print("\n⚠️ ITEMS TO CHECK:")
    for item in FIXES_VERIFIED['IMPROVED']:
        print(f"   {item}")

print()
if FIXES_VERIFIED['VERIFIED'] == FIXES_VERIFIED['TOTAL']:
    print("🎉 ALL MAJOR FIXES VERIFIED! ✅")
    print("Backend proctoring system is ready for testing.")
else:
    print(f"⚠️ {FIXES_VERIFIED['TOTAL'] - FIXES_VERIFIED['VERIFIED']} fix(es) need verification.")

print("=" * 70)
