-- ============================================
-- Smart Proctoring System - Database Schema
-- PostgreSQL 14+
-- Created: 2026-01-18
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- ENUM TYPES
-- ============================================

-- User role enumeration
CREATE TYPE user_role AS ENUM ('admin', 'student');

-- Exam status lifecycle
CREATE TYPE exam_status AS ENUM ('draft', 'scheduled', 'active', 'completed', 'cancelled');

-- Exam attempt status
CREATE TYPE attempt_status AS ENUM ('in_progress', 'submitted', 'auto_submitted', 'abandoned');

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
-- TABLE: users
-- Purpose: Store admin and student accounts
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL
);

-- Indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================
-- TABLE: exams
-- Purpose: Store exam definitions and configuration
-- ============================================

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

-- Indexes for exams table
CREATE INDEX idx_exams_status ON exams(status);
CREATE INDEX idx_exams_start_time ON exams(start_time);
CREATE INDEX idx_exams_created_by ON exams(created_by_admin);

-- ============================================
-- TABLE: exam_attempts
-- Purpose: Track student exam sessions
-- ============================================

CREATE TABLE exam_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP NULL,
    status attempt_status DEFAULT 'in_progress',
    browser_metadata JSONB,
    ip_address VARCHAR(45),
    final_score DECIMAL(5,2) CHECK (final_score >= 0 AND final_score <= 100),
    flagged_for_review BOOLEAN DEFAULT FALSE,
    CONSTRAINT one_attempt_per_student_per_exam UNIQUE (exam_id, student_id)
);

-- Indexes for exam_attempts table
CREATE INDEX idx_attempts_exam_id ON exam_attempts(exam_id);
CREATE INDEX idx_attempts_student_id ON exam_attempts(student_id);
CREATE INDEX idx_attempts_status ON exam_attempts(status);

-- ============================================
-- TABLE: proctoring_logs
-- Purpose: Real-time proctoring event tracking
-- ============================================

CREATE TABLE proctoring_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type proctoring_event NOT NULL,
    description TEXT NOT NULL,
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    metadata JSONB
);

-- Indexes for proctoring_logs table
CREATE INDEX idx_proctoring_attempt_id ON proctoring_logs(attempt_id);
CREATE INDEX idx_proctoring_event_type ON proctoring_logs(event_type);
CREATE INDEX idx_proctoring_timestamp ON proctoring_logs(timestamp);

-- ============================================
-- TABLE: ai_analysis
-- Purpose: AI-generated analysis results
-- ============================================

CREATE TABLE ai_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    analysis_type ai_analysis_type NOT NULL,
    result_data JSONB NOT NULL,
    anomaly_score DECIMAL(5,4) CHECK (anomaly_score >= 0 AND anomaly_score <= 1),
    recommendations TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for ai_analysis table
CREATE INDEX idx_ai_analysis_attempt_id ON ai_analysis(attempt_id);
CREATE INDEX idx_ai_analysis_type ON ai_analysis(analysis_type);

-- ============================================
-- TABLE: submissions
-- Purpose: Student answer submissions with integrity
-- ============================================

CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attempt_id UUID UNIQUE NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    answers JSONB NOT NULL,
    submission_hash VARCHAR(64) NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    integrity_verified BOOLEAN DEFAULT FALSE
);

-- Indexes for submissions table
CREATE INDEX idx_submissions_attempt_id ON submissions(attempt_id);
CREATE INDEX idx_submissions_hash ON submissions(submission_hash);

-- ============================================
-- TABLE: blockchain_logs
-- Purpose: Immutable blockchain audit trail
-- ============================================

CREATE TABLE blockchain_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    block_index INTEGER UNIQUE NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data JSONB NOT NULL,
    previous_hash VARCHAR(64) NOT NULL,
    current_hash VARCHAR(64) UNIQUE NOT NULL,
    nonce INTEGER NOT NULL,
    exam_id UUID REFERENCES exams(id) ON DELETE SET NULL,
    attempt_id UUID REFERENCES exam_attempts(id) ON DELETE SET NULL
);

-- Indexes for blockchain_logs table
CREATE INDEX idx_blockchain_index ON blockchain_logs(block_index);
CREATE INDEX idx_blockchain_exam_id ON blockchain_logs(exam_id);
CREATE INDEX idx_blockchain_attempt_id ON blockchain_logs(attempt_id);

-- ============================================
-- TRIGGERS - Auto-update timestamps
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
-- COMMENTS - Documentation
-- ============================================

COMMENT ON TABLE users IS 'Stores admin and student user accounts with role-based access';
COMMENT ON TABLE exams IS 'Exam definitions, scheduling, and configuration';
COMMENT ON TABLE exam_attempts IS 'Individual student exam sessions and attempts';
COMMENT ON TABLE proctoring_logs IS 'Real-time proctoring events captured during exams';
COMMENT ON TABLE ai_analysis IS 'AI-generated analysis results for exam attempts';
COMMENT ON TABLE submissions IS 'Student exam answer submissions with integrity verification';
COMMENT ON TABLE blockchain_logs IS 'Immutable blockchain-based audit trail';

-- ============================================
-- END OF SCHEMA
-- ============================================
