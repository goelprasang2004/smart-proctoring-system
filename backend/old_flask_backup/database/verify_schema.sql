-- ============================================
-- Database Schema Verification Script
-- Smart Proctoring System
-- ============================================

\echo '=========================================='
\echo 'DATABASE SCHEMA VERIFICATION'
\echo '=========================================='
\echo ''

-- ============================================
-- 1. VERIFY EXTENSIONS
-- ============================================

\echo '1. Verifying PostgreSQL Extensions...'
SELECT extname, extversion 
FROM pg_extension 
WHERE extname = 'uuid-ossp';

\echo ''

-- ============================================
-- 2. VERIFY ENUM TYPES
-- ============================================

\echo '2. Verifying Custom ENUM Types...'
SELECT 
    t.typname as enum_name,
    string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) as values
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typname IN ('user_role', 'exam_status', 'attempt_status', 'proctoring_event', 'ai_analysis_type')
GROUP BY t.typname
ORDER BY t.typname;

\echo ''

-- ============================================
-- 3. VERIFY TABLES
-- ============================================

\echo '3. Verifying Tables...'
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

\echo ''

-- ============================================
-- 4. VERIFY COLUMNS FOR EACH TABLE
-- ============================================

\echo '4. Verifying Table Columns...'
\echo ''
\echo 'Table: users'
\d users

\echo ''
\echo 'Table: exams'
\d exams

\echo ''
\echo 'Table: exam_attempts'
\d exam_attempts

\echo ''
\echo 'Table: proctoring_logs'
\d proctoring_logs

\echo ''
\echo 'Table: ai_analysis'
\d ai_analysis

\echo ''
\echo 'Table: submissions'
\d submissions

\echo ''
\echo 'Table: blockchain_logs'
\d blockchain_logs

\echo ''

-- ============================================
-- 5. VERIFY PRIMARY KEYS
-- ============================================

\echo '5. Verifying Primary Keys...'
SELECT 
    tc.table_name, 
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'PRIMARY KEY'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;

\echo ''

-- ============================================
-- 6. VERIFY FOREIGN KEYS
-- ============================================

\echo '6. Verifying Foreign Key Constraints...'
SELECT 
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;

\echo ''

-- ============================================
-- 7. VERIFY UNIQUE CONSTRAINTS
-- ============================================

\echo '7. Verifying Unique Constraints...'
SELECT 
    tc.table_name,
    tc.constraint_name,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'UNIQUE'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;

\echo ''

-- ============================================
-- 8. VERIFY CHECK CONSTRAINTS
-- ============================================

\echo '8. Verifying Check Constraints...'
SELECT 
    tc.table_name,
    tc.constraint_name,
    cc.check_clause
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc
    ON tc.constraint_name = cc.constraint_name
WHERE tc.constraint_type = 'CHECK'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;

\echo ''

-- ============================================
-- 9. VERIFY INDEXES
-- ============================================

\echo '9. Verifying Indexes...'
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

\echo ''

-- ============================================
-- 10. VERIFY TRIGGERS
-- ============================================

\echo '10. Verifying Triggers...'
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table;

\echo ''

-- ============================================
-- 11. VERIFY TABLE COMMENTS
-- ============================================

\echo '11. Verifying Table Comments...'
SELECT 
    c.relname AS table_name,
    pg_catalog.obj_description(c.oid, 'pg_class') AS comment
FROM pg_catalog.pg_class c
LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
    AND n.nspname = 'public'
    AND pg_catalog.obj_description(c.oid, 'pg_class') IS NOT NULL
ORDER BY c.relname;

\echo ''

-- ============================================
-- 12. SUMMARY
-- ============================================

\echo '=========================================='
\echo 'VERIFICATION SUMMARY'
\echo '=========================================='

-- Count tables
SELECT 'Total Tables: ' || COUNT(*)::text
FROM pg_tables
WHERE schemaname = 'public';

-- Count indexes
SELECT 'Total Indexes: ' || COUNT(*)::text
FROM pg_indexes
WHERE schemaname = 'public';

-- Count foreign keys
SELECT 'Total Foreign Keys: ' || COUNT(*)::text
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
    AND table_schema = 'public';

-- Count triggers
SELECT 'Total Triggers: ' || COUNT(*)::text
FROM information_schema.triggers
WHERE trigger_schema = 'public';

\echo ''
\echo '=========================================='
\echo 'VERIFICATION COMPLETE'
\echo '=========================================='
