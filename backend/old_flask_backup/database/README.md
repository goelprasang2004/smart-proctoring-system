# Smart Proctoring System - Database Setup Guide

## Prerequisites

- PostgreSQL 14+ installed
- Python 3.9+ installed
- Basic knowledge of SQL and command line

## Step 1: Install PostgreSQL

### Windows
1. Download from: https://www.postgresql.org/download/windows/
2. Run the installer
3. Remember the password you set for the `postgres` user
4. Default port: 5432

### Alternative: Use Cloud Database (FREE)
- **ElephantSQL**: https://www.elephantsql.com/ (20MB free)
- **Supabase**: https://supabase.com/ (500MB free)
- **Neon**: https://neon.tech/ (3GB free)

## Step 2: Create Database

Open PostgreSQL command line (psql) or pgAdmin:

```sql
-- Create database
CREATE DATABASE proctoring_system;

-- Connect to database
\c proctoring_system
```

## Step 3: Run Schema Script

Execute the schema creation script:

```bash
# Method 1: Using psql command line
psql -U postgres -d proctoring_system -f database/schema.sql

# Method 2: Using pgAdmin
# Copy contents of schema.sql and execute in Query Tool
```

## Step 4: Load Seed Data (Optional)

Load test data for development:

```bash
psql -U postgres -d proctoring_system -f database/seed_data.sql
```

## Step 5: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and update database credentials:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=proctoring_system
   DB_USER=postgres
   DB_PASSWORD=your_actual_password
   ```

## Step 6: Install Python Dependencies

```bash
pip install psycopg2-binary python-dotenv
```

## Step 7: Test Connection

Run the connection test:

```bash
python database/db_connection.py
```

Expected output:
```
✓ DATABASE CONNECTION SUCCESSFUL
==================================================
Available tables:
  • users
  • exams
  • exam_attempts
  • proctoring_logs
  • ai_analysis
  • submissions
  • blockchain_logs
==================================================
```

## Verification Checklist

- [ ] PostgreSQL installed and running
- [ ] Database `proctoring_system` created
- [ ] All 7 tables created successfully
- [ ] Seed data loaded
- [ ] `.env` file configured
- [ ] Python dependencies installed
- [ ] Connection test passes

## Test Credentials (from seed data)

**Admin:**
- Email: admin@proctoring.com
- Password: Admin@123

**Student 1:**
- Email: student1@test.com
- Password: Admin@123

**Student 2:**
- Email: student2@test.com
- Password: Admin@123

## Troubleshooting

### Connection refused
- Ensure PostgreSQL service is running
- Check port 5432 is not blocked

### Authentication failed
- Verify database credentials in `.env`
- Check PostgreSQL user permissions

### Table creation errors
- Drop existing database and recreate: `DROP DATABASE proctoring_system;`
- Ensure PostgreSQL version is 14+

## Database Management Commands

```sql
-- List all tables
\dt

-- View table structure
\d users
\d exams

-- View all users
SELECT * FROM users;

-- View all exams
SELECT * FROM exams;

-- Drop all tables (CAREFUL!)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

## Next Steps

After successful database setup, you'll be ready for **STEP 2: Project Structure & Configuration**.
