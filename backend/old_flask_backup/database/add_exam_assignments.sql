-- ============================================
-- Exam Assignments Table
-- Purpose: Track which exams are assigned to which students
-- ============================================

-- Create exam_assignments table
CREATE TABLE IF NOT EXISTS exam_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by_admin UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Prevent duplicate assignments
    CONSTRAINT unique_exam_student_assignment UNIQUE (exam_id, student_id)
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_exam_assignments_exam_id ON exam_assignments(exam_id);
CREATE INDEX IF NOT EXISTS idx_exam_assignments_student_id ON exam_assignments(student_id);
CREATE INDEX IF NOT EXISTS idx_exam_assignments_assigned_by ON exam_assignments(assigned_by_admin);

-- Add comment
COMMENT ON TABLE exam_assignments IS 'Tracks which exams are assigned to which students by admins';
COMMENT ON COLUMN exam_assignments.exam_id IS 'Reference to the exam being assigned';
COMMENT ON COLUMN exam_assignments.student_id IS 'Reference to the student receiving the assignment';
COMMENT ON COLUMN exam_assignments.assigned_by_admin IS 'Admin who created this assignment';

-- Verify table creation
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'exam_assignments'
ORDER BY ordinal_position;
