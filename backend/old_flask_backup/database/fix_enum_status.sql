-- Fix exam_status enum mismatch
-- Adds 'active' and 'cancelled' status to match backend code

-- Add new enum values
ALTER TYPE exam_status ADD VALUE IF NOT EXISTS 'active';
ALTER TYPE exam_status ADD VALUE IF NOT EXISTS 'cancelled';

-- Migrate existing 'in_progress' to 'active' (optional)
-- UPDATE exams SET status = 'active' WHERE status = 'in_progress';

-- Verify
SELECT enumlabel FROM pg_enum WHERE enumtypid = 'exam_status'::regtype ORDER BY enumlabel;
