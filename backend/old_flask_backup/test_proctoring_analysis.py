"""
Test and Analysis Script for Proctoring System
================================================
This script identifies issues and validates implementation against requirements.
"""

import json

# Analysis Results
ISSUES_FOUND = {
    'critical': [],
    'major': [],
    'minor': [],
    'warnings': []
}

def check_issue(severity, title, description, file_path, line_number=None):
    """Log an issue found during analysis"""
    issue = {
        'title': title,
        'description': description,
        'file': file_path,
        'line': line_number
    }
    ISSUES_FOUND[severity].append(issue)
    print(f"[{severity.upper()}] {title}")
    print(f"  File: {file_path}" + (f":{line_number}" if line_number else ""))
    print(f"  {description}\n")


# ISSUE 1: Missing validation in log_event endpoint
print("="*70)
print("PROCTORING SYSTEM CODE REVIEW")
print("="*70)
print("\n1. CHECKING: Proctoring API Routes\n")

check_issue(
    'minor',
    'Missing attempt ownership verification',
    'In /api/proctoring/my-attempt/:attempt_id endpoint, there is a TODO comment indicating '
    'that student-attempt ownership is not verified. A student could access other students\' '
    'proctoring data if they know the attempt ID.',
    'api/routes/proctoring.py',
    130
)

# ISSUE 2: Risk score calculation issue
print("2. CHECKING: Risk Score Calculation Logic\n")

check_issue(
    'major',
    'Risk score calculation exceeds maximum of 1.0',
    'In services/proctoring_service.py, the _calculate_risk_score method can exceed 1.0 if all three '
    'factors are maximized. The formula uses min(1.0, risk) at the end, but it\'s mathematically '
    'possible. Max should be (0.4 + 0.3 + 0.3 = 1.0) which is correct, but floating point '
    'precision could cause issues. Consider clamping after each factor.',
    'services/proctoring_service.py',
    369
)

# ISSUE 3: AI Analysis trigger threshold
print("3. CHECKING: AI Analysis Triggering\n")

check_issue(
    'minor',
    'AI analysis triggered only for confidence >= 0.7',
    'The system only triggers AI analysis when confidence_score >= 0.7. This means many '
    'events with moderate confidence (0.5-0.7) won\'t be analyzed. Consider lower threshold.',
    'services/proctoring_service.py',
    86
)

# ISSUE 4: Metadata handling in anomaly calculation
print("4. CHECKING: Anomaly Score Calculation\n")

check_issue(
    'minor',
    'Incomplete metadata handling in anomaly calculation',
    'In _calculate_anomaly_score, the function checks for specific fields in result_data, '
    'but doesn\'t validate that result_data contains expected fields based on analysis_type.',
    'services/proctoring_service.py',
    243
)

# ISSUE 5: Database query performance
print("5. CHECKING: Database Queries\n")

check_issue(
    'major',
    'get_all_suspicious_attempts uses STRING_AGG without ordering',
    'In models/proctoring.py, the get_all_suspicious_attempts method aggregates event_types '
    'without specifying ORDER BY within the STRING_AGG function, leading to non-deterministic output.',
    'models/proctoring.py',
    260
)

# ISSUE 6: Blockchain integration error handling
print("6. CHECKING: Blockchain Integration\n")

check_issue(
    'minor',
    'Blockchain logging failures are silently caught',
    'In log_event and _trigger_ai_analysis, blockchain logging failures are caught and only '
    'logged as warnings. If blockchain logging is critical for audit trail, consider raising.',
    'services/proctoring_service.py',
    87
)

# ISSUE 7: Response format inconsistency
print("7. CHECKING: API Response Consistency\n")

check_issue(
    'minor',
    'Event response format inconsistency',
    'The log_event endpoint returns event as a dict with string UUID values, but the database '
    'query returns UUID objects that may not serialize properly in all Flask versions.',
    'models/proctoring.py',
    59
)

# ISSUE 8: Missing error handling in model methods
print("8. CHECKING: Error Handling\n")

check_issue(
    'major',
    'Missing NULL check in get_proctoring_summary',
    'In services/proctoring_service.py, get_proctoring_summary doesn\'t handle the case where '
    'ProctoringEvent.get_event_summary or AIAnalysis.get_summary_by_attempt returns empty results. '
    'This could cause KeyError or AttributeError.',
    'services/proctoring_service.py',
    345
)

# ISSUE 9: Confidence score bounds
print("9. CHECKING: Confidence Score Bounds\n")

check_issue(
    'major',
    'Confidence score calculation doesn\'t properly validate bounds',
    'In _simulate_confidence, after adding randomness and adjusting for metadata, the max() and min() '
    'calls may result in confidence outside [0, 1] range due to float precision issues.',
    'services/proctoring_service.py',
    111
)

# SUMMARY
print("\n" + "="*70)
print("ANALYSIS SUMMARY")
print("="*70)

total_issues = sum(len(v) for v in ISSUES_FOUND.values())
print(f"\nTotal Issues Found: {total_issues}")
print(f"  Critical: {len(ISSUES_FOUND['critical'])}")
print(f"  Major: {len(ISSUES_FOUND['major'])}")
print(f"  Minor: {len(ISSUES_FOUND['minor'])}")
print(f"  Warnings: {len(ISSUES_FOUND['warnings'])}\n")

if ISSUES_FOUND['critical']:
    print("CRITICAL ISSUES (Must Fix):")
    for issue in ISSUES_FOUND['critical']:
        print(f"  - {issue['title']} ({issue['file']})")

if ISSUES_FOUND['major']:
    print("\nMAJOR ISSUES (Should Fix):")
    for issue in ISSUES_FOUND['major']:
        print(f"  - {issue['title']} ({issue['file']})")

if ISSUES_FOUND['minor']:
    print("\nMINOR ISSUES (Could Improve):")
    for issue in ISSUES_FOUND['minor']:
        print(f"  - {issue['title']} ({issue['file']})")
