#!/bin/bash
# ============================================
# Quick Schema Setup Script
# Smart Proctoring System
# ============================================

echo "=========================================="
echo "Smart Proctoring System - Schema Setup"
echo "=========================================="
echo ""

# Variables
DB_NAME="proctoring_system"
DB_USER="postgres"

# Step 1: Check if database exists
echo "Checking if database exists..."
DB_EXISTS=$(psql -U $DB_USER -lqt | cut -d \| -f 1 | grep -w $DB_NAME | wc -l)

if [ $DB_EXISTS -eq 0 ]; then
    echo "Creating database: $DB_NAME"
    createdb -U $DB_USER $DB_NAME
    echo "✓ Database created"
else
    echo "✓ Database already exists"
fi

echo ""

# Step 2: Execute schema
echo "Executing schema.sql..."
psql -U $DB_USER -d $DB_NAME -f database/schema.sql

if [ $? -eq 0 ]; then
    echo "✓ Schema executed successfully"
else
    echo "✗ Schema execution failed"
    exit 1
fi

echo ""

# Step 3: Verify schema
echo "Verifying schema..."
psql -U $DB_USER -d $DB_NAME -f database/verify_schema.sql

echo ""
echo "=========================================="
echo "Schema Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Load seed data: psql -U $DB_USER -d $DB_NAME -f database/seed_data.sql"
echo "2. Test connection: python models/db_test.py"
echo ""
