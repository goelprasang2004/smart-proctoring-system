-- ============================================
-- Smart Proctoring System - Seed Data
-- Purpose: Initial test data for development
-- ============================================

-- ============================================
-- SEED USERS
-- ============================================

-- Insert Admin User
-- Email: admin@proctoring.com
-- Password: Admin@123 (bcrypt hashed)
INSERT INTO users (id, email, password_hash, role, full_name, is_active) VALUES
(
    '00000000-0000-0000-0000-000000000001'::uuid,
    'admin@proctoring.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbGkJxw7hO',  -- Admin@123
    'admin',
    'System Administrator',
    TRUE
);

-- Insert Test Students
INSERT INTO users (id, email, password_hash, role, full_name, is_active) VALUES
(
    '00000000-0000-0000-0000-000000000002'::uuid,
    'student1@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbGkJxw7hO',  -- Admin@123
    'student',
    'John Doe',
    TRUE
),
(
    '00000000-0000-0000-0000-000000000003'::uuid,
    'student2@test.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYbGkJxw7hO',  -- Admin@123
    'student',
    'Jane Smith',
    TRUE
);

-- ============================================
-- SEED EXAMS
-- ============================================

-- Insert Test Exam
INSERT INTO exams (
    id,
    title,
    description,
    created_by_admin,
    start_time,
    end_time,
    duration_minutes,
    exam_config,
    status
) VALUES (
    '10000000-0000-0000-0000-000000000001'::uuid,
    'Python Programming - Final Exam',
    'Comprehensive assessment covering Python fundamentals, OOP, and data structures',
    '00000000-0000-0000-0000-000000000001'::uuid,
    CURRENT_TIMESTAMP + INTERVAL '1 day',
    CURRENT_TIMESTAMP + INTERVAL '2 days',
    60,
    '{
        "questions": [
            {
                "id": "q1",
                "type": "mcq",
                "question": "What is the output of print(type([]))?",
                "options": ["<class ''list''>", "<class ''dict''>", "<class ''tuple''>", "<class ''set''>"],
                "correct_answer": 0,
                "points": 5
            },
            {
                "id": "q2",
                "type": "mcq",
                "question": "Which keyword is used to create a function in Python?",
                "options": ["function", "def", "func", "define"],
                "correct_answer": 1,
                "points": 5
            },
            {
                "id": "q3",
                "type": "short_answer",
                "question": "Write a Python function to check if a number is prime.",
                "points": 15
            }
        ],
        "total_marks": 25,
        "passing_marks": 15,
        "proctoring_enabled": true,
        "allow_tab_switch": false,
        "max_tab_switches": 3,
        "browser_lock": true
    }'::jsonb,
    'scheduled'
);

-- Insert Another Test Exam (Draft)
INSERT INTO exams (
    id,
    title,
    description,
    created_by_admin,
    start_time,
    end_time,
    duration_minutes,
    exam_config,
    status
) VALUES (
    '10000000-0000-0000-0000-000000000002'::uuid,
    'Data Structures - Midterm',
    'Assessment on arrays, linked lists, stacks, and queues',
    '00000000-0000-0000-0000-000000000001'::uuid,
    CURRENT_TIMESTAMP + INTERVAL '3 days',
    CURRENT_TIMESTAMP + INTERVAL '4 days',
    90,
    '{
        "questions": [
            {
                "id": "q1",
                "type": "mcq",
                "question": "What is the time complexity of accessing an element in an array?",
                "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
                "correct_answer": 0,
                "points": 10
            }
        ],
        "total_marks": 50,
        "passing_marks": 30,
        "proctoring_enabled": true,
        "allow_tab_switch": false,
        "max_tab_switches": 2,
        "browser_lock": true
    }'::jsonb,
    'draft'
);

-- ============================================
-- INITIALIZE BLOCKCHAIN WITH GENESIS BLOCK
-- ============================================

INSERT INTO blockchain_logs (
    block_index,
    timestamp,
    data,
    previous_hash,
    current_hash,
    nonce,
    exam_id,
    attempt_id
) VALUES (
    0,
    CURRENT_TIMESTAMP,
    '{
        "type": "genesis_block",
        "message": "Smart Proctoring System - Genesis Block",
        "version": "1.0",
        "initialization_date": "2026-01-18"
    }'::jsonb,
    '0',
    'genesis_block_hash_0000000000000000000000000000000000000000000000000000000000000000',
    0,
    NULL,
    NULL
);

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Verify inserted data
SELECT 'Users created:' as info, COUNT(*) as count FROM users;
SELECT 'Exams created:' as info, COUNT(*) as count FROM exams;
SELECT 'Blockchain initialized:' as info, COUNT(*) as count FROM blockchain_logs;

-- Display test credentials
SELECT 
    '============================================' as separator
UNION ALL
SELECT 'TEST CREDENTIALS:'
UNION ALL
SELECT '============================================'
UNION ALL
SELECT 'Admin:'
UNION ALL
SELECT '  Email: admin@proctoring.com'
UNION ALL
SELECT '  Password: Admin@123'
UNION ALL
SELECT ''
UNION ALL
SELECT 'Student 1:'
UNION ALL
SELECT '  Email: student1@test.com'
UNION ALL
SELECT '  Password: Admin@123'
UNION ALL
SELECT ''
UNION ALL
SELECT 'Student 2:'
UNION ALL
SELECT '  Email: student2@test.com'
UNION ALL
SELECT '  Password: Admin@123'
UNION ALL
SELECT '============================================';

-- ============================================
-- END OF SEED DATA
-- ============================================
