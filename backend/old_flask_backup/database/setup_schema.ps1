# ============================================
# Quick Schema Setup Script (Windows)
# Smart Proctoring System
# ============================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Smart Proctoring System - Schema Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$DB_NAME = "proctoring_system"
$DB_USER = "postgres"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# Step 1: Check PostgreSQL is running
Write-Host "Checking PostgreSQL status..." -ForegroundColor Yellow
$pgStatus = Get-Service -Name postgresql* -ErrorAction SilentlyContinue

if ($null -eq $pgStatus) {
    Write-Host "✗ PostgreSQL service not found. Please install PostgreSQL first." -ForegroundColor Red
    exit 1
}

if ($pgStatus.Status -ne "Running") {
    Write-Host "✗ PostgreSQL is not running. Starting service..." -ForegroundColor Yellow
    Start-Service $pgStatus.Name
    Start-Sleep -Seconds 3
}

Write-Host "✓ PostgreSQL is running" -ForegroundColor Green
Write-Host ""

# Step 2: Check if database exists
Write-Host "Checking if database exists..." -ForegroundColor Yellow
$dbExists = & psql -U $DB_USER -lqt | Select-String -Pattern $DB_NAME

if ($null -eq $dbExists) {
    Write-Host "Creating database: $DB_NAME" -ForegroundColor Yellow
    & createdb -U $DB_USER $DB_NAME
    Write-Host "✓ Database created" -ForegroundColor Green
} else {
    Write-Host "✓ Database already exists" -ForegroundColor Green
}

Write-Host ""

# Step 3: Execute schema
Write-Host "Executing schema.sql..." -ForegroundColor Yellow
$schemaPath = Join-Path $SCRIPT_DIR "schema.sql"
& psql -U $DB_USER -d $DB_NAME -f $schemaPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Schema executed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Schema execution failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Verify schema
Write-Host "Verifying schema..." -ForegroundColor Yellow
$verifyPath = Join-Path $SCRIPT_DIR "verify_schema.sql"
& psql -U $DB_USER -d $DB_NAME -f $verifyPath

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Schema Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Load seed data: psql -U $DB_USER -d $DB_NAME -f database/seed_data.sql"
Write-Host "2. Test connection: python models/db_test.py"
Write-Host ""
