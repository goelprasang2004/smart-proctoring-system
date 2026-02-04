# Backend - Smart Proctoring System

Flask-based backend API for the Smart Proctoring System.

## Quick Start

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run database setup
psql -U postgres -d proctoring_db -f database/MANUAL_SETUP.sql

# Start server
python app.py
```

Server runs on `http://localhost:5000`

## Project Structure

```
backend/
├── api/                    # API routes
│   └── routes/
│       ├── auth.py        # Authentication endpoints
│       ├── exams.py       # Exam management
│       ├── proctoring.py  # Proctoring events
│       └── blockchain.py  # Blockchain audit
├── config/                 # Configuration
│   └── config.py          # Environment-based config
├── database/               # Database files
│   ├── schema.sql         # Original schema
│   ├── MANUAL_SETUP.sql   # Complete setup (USE THIS)
│   ├── seed_data.sql      # Sample data
│   └── verify_schema.sql  # Verification queries
├── middleware/             # Middleware
│   ├── auth_middleware.py # JWT validation, RBAC
│   └── rate_limit.py      # Rate limiting
├── models/                 # Data access layer
│   ├── user.py
│   ├── exam.py
│   ├── proctoring.py
│   ├── ai_analysis.py
│   ├── blockchain_log.py
│   └── database.py        # DB connection manager
├── services/               # Business logic
│   ├── auth_service.py
│   ├── exam_service.py
│   ├── proctoring_service.py
│   ├── blockchain_service.py
│   └── exam_session_security.py
├── utils/                  # Utilities
│   ├── logger.py          # Logging utility
│   └── blockchain_hasher.py # SHA-256 hashing
├── logs/                   # Application logs
├── app.py                  # Flask application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (DO NOT COMMIT)
└── .env.example            # Environment template
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Exams (Admin)
- `POST /api/exams` - Create exam
- `GET /api/exams` - List all exams
- `GET /api/exams/<id>` - Get exam details
- `PUT /api/exams/<id>` - Update exam
- `DELETE /api/exams/<id>` - Delete exam
- `PATCH /api/exams/<id>/status` - Update status

### Exams (Student)
- `GET /api/exams/available` - List available exams
- `GET /api/exams/<id>/details` - Get exam details

### Proctoring
- `POST /api/proctoring/event` - Log proctoring event (Student)
- `GET /api/proctoring/my-attempt/<id>` - Get own attempt (Student)
- `GET /api/proctoring/attempt/<id>` - Get attempt details (Admin)
- `GET /api/proctoring/attempt/<id>/events` - Get events (Admin)
- `GET /api/proctoring/attempt/<id>/ai-analysis` - Get AI analysis (Admin)
- `GET /api/proctoring/suspicious` - Get suspicious attempts (Admin)

### Blockchain (Admin Only)
- `GET /api/blockchain/summary` - Blockchain stats
- `GET /api/blockchain/verify` - Verify integrity
- `GET /api/blockchain/entity/<type>/<id>` - Get entity audit trail
- `GET /api/blockchain/events/<type>` - Filter by event type
- `GET /api/blockchain/attempt/<id>` - Get attempt audit trail
- `POST /api/blockchain/initialize` - Initialize genesis block
- `GET /api/blockchain/event-types` - List event types

### Health
- `GET /health` - Health check

## Environment Variables

Required in `.env`:

```
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=proctoring_db
DB_USER=postgres
DB_PASSWORD=your_password

# Flask
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key

# JWT
JWT_SECRET_KEY=your_jwt_secret
JWT_ACCESS_TOKEN_EXPIRES=900      # 15 minutes
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7 days

# Security
BCRYPT_ROUNDS=12
```

## Database Setup

```bash
# Option 1: Manual setup (recommended)
psql -U postgres -d proctoring_db -f database/MANUAL_SETUP.sql

# Option 2: Original schema + seed data
psql -U postgres -d proctoring_db -f database/schema.sql
psql -U postgres -d proctoring_db -f database/seed_data.sql
```

## Default Credentials

**Admin Account:**
- Email: `admin@gmail.com`
- Password: `StrongPassword123!`

## Security Features

- ✅ JWT Authentication (access + refresh tokens)
- ✅ Token rotation on refresh
- ✅ RBAC (Role-Based Access Control)
- ✅ Rate limiting (brute force protection)
- ✅ Bcrypt password hashing (12 rounds)
- ✅ Session security (concurrent attempt prevention)
- ✅ Blockchain audit logging (immutable)

## Testing

```bash
# Test authentication
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmail.com","password":"StrongPassword123!"}'

# Test health check
curl http://localhost:5000/health
```

## Production Deployment

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Documentation

See parent directory for comprehensive documentation:
- `README.md` - Complete system documentation
- `STEP*.md` - Step-by-step implementation guides
- `FRONTEND_PROCTORING_GUIDE.md` - Client-side proctoring

## Tech Stack

- Python 3.8+
- Flask 2.0+
- PostgreSQL 13+
- psycopg2 (PostgreSQL adapter)
- PyJWT (JWT tokens)
- bcrypt (password hashing)
- python-dotenv (environment variables)

## License

Educational/Demonstration purposes
