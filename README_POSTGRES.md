# PostgreSQL & pgAdmin Setup Guide

This guide explains how to set up, connect, and verify the PostgreSQL database for the Exam Proctoring System using pgAdmin.

## Prerequisites
- **PostgreSQL** installed and running (v13+ recommended).
- **pgAdmin 4** installed.
- **Python Backend** configured with `DATABASE_URL` in `.env`.

---

## 1. Database Creation

Open **pgAdmin 4** or use the command line (`psql`) to create the database.

### Using SQL Query Tool (in pgAdmin)
1.  Right-click on **Databases** > **Create** > **Database...**.
2.  Name it `exam_proctoring_db` (or whatever matches your `.env`).
3.  **OR** run this query:

```sql
CREATE DATABASE exam_proctoring_db;
```

## 2. User & Privileges

If you are not using the default `postgres` user, create a dedicated user:

```sql
CREATE USER proctor_admin WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE exam_proctoring_db TO proctor_admin;
```

Update your backend `.env` file:
```env
DATABASE_URL=postgresql://proctor_admin:secure_password@localhost:5432/exam_proctoring_db
```

---

## 3. Verify Tables

Once the backend starts, it automatically creates tables via SQLAlchemy (`Base.metadata.create_all`).

To verify tables in **pgAdmin**:
1.  Navigate to **Servers** > **[Your Server]** > **Databases** > **exam_proctoring_db**.
2.  Go to **Schemas** > **public** > **Tables**.
3.  You should see:
    - `users`
    - `exams` (if implemented)
    - `proctoring_logs`
    - `blockchain_blocks` (or similar for blockchain logs)

## 4. Example Verification Queries

Right-click the database and select **Query Tool**.

### Check Users
```sql
SELECT id, email, is_active, role FROM users;
```

### Check Proctoring Logs (Real-time Events)
```sql
SELECT * FROM proctoring_logs 
ORDER BY timestamp DESC 
LIMIT 10;
```

### Check Blockchain Integrity
The system stores immutable logs using SHA-256.

```sql
SELECT id, prev_hash, data_hash, timestamp 
FROM blockchain_blocks 
ORDER BY id ASC;
```

### Check Exam Attempts
```sql
SELECT * FROM exam_attempts 
WHERE status = 'completed';
```
