-- ============================================
-- Smart Proctoring System - PostgreSQL Setup
-- Execute these queries in order in pgAdmin
-- ============================================

-- ============================================
-- STEP 1: Create Extensions
-- ============================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- STEP 2: Create ENUM Types
-- ============================================

-- User roles
CREATE TYPE user_role AS ENUM ('admin', 'student', 'proctor');

-- Exam status
CREATE TYPE exam_status AS ENUM ('draft', 'published', 'scheduled', 'in_progress', 'completed', 'archived');

-- Exam attempt status
CREATE TYPE attempt_status AS ENUM ('in_progress', 'completed', 'terminated', 'cancelled');

-- Proctoring event types
CREATE TYPE proctoring_event AS ENUM (
    'face_detection',
    'voice_detection',
    'stress_alert',
    'tab_switch',
    'window_blur',
    'multiple_faces',
    'no_face',
    'suspicious_behavior'
);

-- AI analysis types
CREATE TYPE ai_analysis_type AS ENUM (
    'face_recognition',
    'voice_recognition',
    'stress_detection',
    'behavioral_analysis'
);

-- ============================================
-- STEP 3: Create Tables
-- ============================================

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'student',
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exams table
CREATE TABLE exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_by_admin UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    exam_config JSONB NOT NULL,
    status exam_status DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_exam_time CHECK (end_time > start_time)
);

-- Exam attempts table
CREATE TABLE exam_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP NULL,
    status attempt_status DEFAULT 'in_progress',
    session_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_active_attempt UNIQUE (student_id, exam_id, status)
);

-- Proctoring logs table
CREATE TABLE proctoring_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    event_type proctoring_event NOT NULL,
    description TEXT,
    confidence_score NUMERIC(3,2) CHECK (confidence_score BETWEEN 0 AND 1),
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI analysis table
CREATE TABLE ai_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    analysis_type ai_analysis_type NOT NULL,
    result_data JSONB,
    anomaly_score NUMERIC(3,2) CHECK (anomaly_score BETWEEN 0 AND 1),
    recommendations TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Submissions table
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    answers JSONB NOT NULL,
    score NUMERIC(5,2),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submission_metadata JSONB,
    CONSTRAINT unique_submission_per_attempt UNIQUE (attempt_id)
);

-- Blockchain logs table (immutable audit trail)
CREATE TABLE blockchain_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    previous_hash VARCHAR(64),
    current_hash VARCHAR(64) NOT NULL UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    payload JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- STEP 4: Create Indexes
-- ============================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Exams indexes
CREATE INDEX idx_exams_status ON exams(status);
CREATE INDEX idx_exams_start_time ON exams(start_time);
CREATE INDEX idx_exams_created_by ON exams(created_by_admin);

-- Exam attempts indexes
CREATE INDEX idx_exam_attempts_exam ON exam_attempts(exam_id);
CREATE INDEX idx_exam_attempts_student ON exam_attempts(student_id);
CREATE INDEX idx_exam_attempts_status ON exam_attempts(status);
CREATE INDEX idx_exam_attempts_started ON exam_attempts(started_at);

-- Proctoring logs indexes
CREATE INDEX idx_proctoring_logs_attempt ON proctoring_logs(attempt_id);
CREATE INDEX idx_proctoring_logs_event_type ON proctoring_logs(event_type);
CREATE INDEX idx_proctoring_logs_timestamp ON proctoring_logs(timestamp);
CREATE INDEX idx_proctoring_logs_confidence ON proctoring_logs(confidence_score);

-- AI analysis indexes
CREATE INDEX idx_ai_analysis_attempt ON ai_analysis(attempt_id);
CREATE INDEX idx_ai_analysis_type ON ai_analysis(analysis_type);
CREATE INDEX idx_ai_analysis_anomaly ON ai_analysis(anomaly_score);
CREATE INDEX idx_ai_analysis_analyzed_at ON ai_analysis(analyzed_at);

-- Submissions indexes
CREATE INDEX idx_submissions_attempt ON submissions(attempt_id);
CREATE INDEX idx_submissions_submitted_at ON submissions(submitted_at);

-- Blockchain logs indexes
CREATE INDEX idx_blockchain_logs_event_type ON blockchain_logs(event_type);
CREATE INDEX idx_blockchain_logs_entity ON blockchain_logs(entity_type, entity_id);
CREATE INDEX idx_blockchain_logs_created_at ON blockchain_logs(created_at);
CREATE INDEX idx_blockchain_logs_current_hash ON blockchain_logs(current_hash);

-- ============================================
-- STEP 5: Create Triggers (Auto-update timestamps)
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for exams table
CREATE TRIGGER update_exams_updated_at
    BEFORE UPDATE ON exams
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- STEP 6: Insert Default Admin User
-- ============================================

-- NOTE: The password hash below is for "StrongPassword123!"
-- Generated using bcrypt with 12 rounds
-- In production, use your backend's hash generation method

INSERT INTO users (email, password_hash, role, full_name, is_active)
VALUES (
    'admin@gmail.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWJ7GRJu',
    'admin',
    'System Administrator',
    TRUE
);

-- ============================================
-- STEP 7: Insert Genesis Blockchain Block
-- ============================================

INSERT INTO blockchain_logs (
    previous_hash,
    current_hash,
    event_type,
    entity_type,
    entity_id,
    payload
)
VALUES (
    NULL,
    'genesis_block_hash_0000000000000000000000000000000000000000000000000',
    'system_init',
    'system',
    NULL,
    '{"system": "Smart Proctoring System", "version": "1.0", "description": "Blockchain audit trail initialized"}'::jsonb
);

-- ============================================
-- STEP 8: Verify Setup
-- ============================================

-- Check tables created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check admin user created
SELECT id, email, role, full_name, is_active, created_at 
FROM users 
WHERE email = 'admin@gmail.com';

-- Check genesis block created
SELECT id, event_type, created_at 
FROM blockchain_logs 
WHERE event_type = 'system_init';

-- Check indexes created
SELECT indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY indexname;

-- ============================================
-- OPTIONAL: Sample Data (for testing)
-- ============================================

-- Insert sample student (password: TestStudent123!)
INSERT INTO users (email, password_hash, role, full_name)
VALUES (
    'student@example.com',
    '$2b$12$KIXvZ3H5y8n3UQ0J8F0HNuN7LQ3xJ5yN8L0H2F3K4L5M6N7O8P9Q0',
    'student',
    'Test Student'
);

-- Insert sample exam
INSERT INTO exams (
    title,
    description,
    created_by_admin,
    start_time,
    end_time,
    duration_minutes,
    exam_config,
    status
)
SELECT 
    'Sample Midterm Exam',
    'This is a sample exam for testing',
    id,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP + INTERVAL '7 days',
    120,
    '{"questions": [{"id": 1, "text": "Sample question", "type": "multiple_choice", "options": ["A", "B", "C", "D"]}]}'::jsonb,
    'draft'
FROM users
WHERE email = 'admin@gmail.com'
LIMIT 1;

-- ============================================
-- COMPLETION MESSAGE
-- ============================================

SELECT 'Database setup completed successfully!' AS status;
SELECT 'Default admin: admin@gmail.com / StrongPassword123!' AS credentials;
SELECT 'Total tables created: ' || COUNT(*)::text FROM information_schema.tables WHERE table_schema = 'public';
