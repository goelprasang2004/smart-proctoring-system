# Deployment Guide - Exam Proctoring System

## Recommended Hosting Architecture

### Option 1: Free Tier / Student Project (Recommended for Testing)

**Frontend**: Vercel or Netlify  
**Backend**: Railway or Render  
**Database**: PostgreSQL on Neon or Supabase  
**Total Cost**: Free (with limitations)

### Option 2: Production Ready (Recommended for Real Use)

**Frontend**: Vercel Pro or Cloudflare Pages  
**Backend**: AWS EC2 / DigitalOcean Droplet / Railway Pro  
**Database**: AWS RDS PostgreSQL / DigitalOcean Managed Database  
**Storage**: AWS S3 / Cloudflare R2 (for video recordings)  
**CDN**: Cloudflare  
**Total Cost**: $20-50/month

### Option 3: Enterprise Scale

**Frontend**: Vercel Enterprise / AWS CloudFront + S3  
**Backend**: AWS ECS / Kubernetes on GCP  
**Database**: AWS RDS Multi-AZ or Aurora PostgreSQL  
**Storage**: AWS S3 + Glacier for archival  
**Monitoring**: Datadog / New Relic  
**Total Cost**: $500+/month

---

## Detailed Deployment Instructions

## 1. Frontend Deployment (React + Vite)

### A. Deploy to Vercel (Recommended - Free Tier Available)

**Why Vercel?**
- Optimized for React/Vite
- Automatic HTTPS
- Global CDN
- Zero configuration
- Generous free tier

**Steps:**

1. **Prepare your code**
```bash
cd frontend
npm install
npm run build  # Test production build
```

2. **Install Vercel CLI**
```bash
npm install -g vercel
```

3. **Login and Deploy**
```bash
vercel login
vercel --prod
```

4. **Configure Environment Variables** (in Vercel Dashboard)
```env
VITE_API_URL=https://your-backend-url.com/api/v1
```

5. **Custom Domain** (Optional)
- Go to Vercel Dashboard → Settings → Domains
- Add your domain (e.g., examproctoring.com)

**Alternative: Using Vercel GitHub Integration**
```bash
# Push to GitHub
git push origin main

# Connect GitHub repo to Vercel
# Visit: https://vercel.com/new
# Import your GitHub repository
# Framework Preset: Vite
# Root Directory: frontend
# Build Command: npm run build
# Output Directory: dist
```

### B. Deploy to Netlify (Alternative)

```bash
cd frontend
npm install -g netlify-cli
netlify login
netlify init
netlify deploy --prod
```

**netlify.toml** (in frontend folder):
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### C. Deploy to Cloudflare Pages

1. Go to Cloudflare Dashboard → Pages
2. Connect GitHub repository
3. Build settings:
   - Framework: Vite
   - Build command: `npm run build`
   - Build output: `dist`
   - Root directory: `frontend`

---

## 2. Backend Deployment (FastAPI + Python)

### A. Deploy to Railway (Recommended - Free Tier)

**Why Railway?**
- $5 free credit monthly
- PostgreSQL included
- Automatic HTTPS
- Simple deployment

**Steps:**

1. **Create `railway.json`** in project root:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. **Create `Procfile`** in backend folder:
```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

3. **Update `requirements.txt`** (backend folder):
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic-settings==2.1.0
opencv-python-headless==4.8.1.78
numpy==1.26.2
pycryptodome==3.19.0
python-dotenv==1.0.0
```

4. **Deploy**:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to Railway project
railway link

# Deploy
railway up
```

5. **Add PostgreSQL Database**:
- In Railway Dashboard → New → Database → PostgreSQL
- Copy `DATABASE_URL` from PostgreSQL service
- Add to backend environment variables

6. **Environment Variables** (Railway Dashboard):
```env
DATABASE_URL=postgresql://user:pass@host:port/dbname
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520
```

### B. Deploy to Render (Alternative)

**Steps:**

1. **Create `render.yaml`** in project root:
```yaml
services:
  - type: web
    name: proctoring-backend
    runtime: python
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: proctoring-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.11.0

databases:
  - name: proctoring-db
    databaseName: proctoring
    user: proctoring_user
```

2. **Deploy**:
- Visit render.com
- New → Blueprint
- Connect GitHub repo
- Render will auto-detect `render.yaml`

### C. Deploy to DigitalOcean App Platform

**Steps:**

1. **Create `.do/app.yaml`**:
```yaml
name: exam-proctoring
region: nyc
services:
- name: backend
  source:
    repo: your-github-repo
    branch: main
    path: /backend
  build_command: pip install -r requirements.txt
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8000
  http_port: 8000
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /api
  envs:
  - key: DATABASE_URL
    scope: RUN_TIME
    value: ${db.DATABASE_URL}
  - key: SECRET_KEY
    scope: RUN_TIME
    type: SECRET

databases:
- name: db
  engine: PG
  version: "15"
  production: true
```

2. Deploy via DigitalOcean CLI or Dashboard

### D. Deploy to AWS EC2 (Production)

**Steps:**

1. **Launch EC2 Instance**:
   - Ubuntu 22.04 LTS
   - t2.micro (free tier) or t3.small
   - Security Group: Allow 22, 80, 443

2. **SSH and Setup**:
```bash
ssh ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip nginx -y

# Clone repository
git clone https://github.com/your-repo/exam-proctoring.git
cd exam-proctoring/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres createdb proctoring_db
sudo -u postgres createuser proctoring_user
```

3. **Create systemd service** (`/etc/systemd/system/proctoring.service`):
```ini
[Unit]
Description=Exam Proctoring FastAPI
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/exam-proctoring/backend
Environment="PATH=/home/ubuntu/exam-proctoring/backend/venv/bin"
ExecStart=/home/ubuntu/exam-proctoring/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Start service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable proctoring
sudo systemctl start proctoring
```

5. **Configure Nginx** (`/etc/nginx/sites-available/proctoring`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

6. **Enable SSL with Let's Encrypt**:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 3. Database Migration (SQLite → PostgreSQL)

### Update Backend Configuration

**backend/app/core/config.py**:
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Use PostgreSQL in production
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/proctoring_db"
    )
    # ... rest of config
```

### Migration Steps

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# The app will auto-create tables on first run
# Or use Alembic for proper migrations:

pip install alembic
alembic init migrations
```

**Create migration** (`migrations/env.py`):
```python
from app.core.database import Base
from app.models.user import User
from app.models.exam import Exam, ExamAttempt
from app.models.proctoring import ProctoringLog
from app.models.blockchain import BlockchainBlock
from app.models.exam_assignment import ExamAssignment

target_metadata = Base.metadata
```

```bash
# Generate migration
alembic revision --autogenerate -m "initial"

# Apply migration
alembic upgrade head
```

---

## 4. Environment Variables Setup

### Frontend (.env.production)
```env
VITE_API_URL=https://api.yoursite.com/api/v1
VITE_WS_URL=wss://api.yoursite.com/api/v1
```

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Security
SECRET_KEY=generate-a-strong-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# CORS Origins
BACKEND_CORS_ORIGINS=["https://yourfrontend.com","https://www.yourfrontend.com"]

# Optional: AWS S3 for video storage
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=exam-proctoring-videos
```

---

## 5. Recommended Full Stack Setup

### Quick Start (Best for Testing)

```bash
# 1. Deploy Backend to Railway
railway login
cd backend
railway init
railway up
# Copy the Railway URL (e.g., https://yourapp.up.railway.app)

# 2. Deploy Frontend to Vercel
cd ../frontend
# Update .env.production with Railway URL
echo "VITE_API_URL=https://yourapp.up.railway.app/api/v1" > .env.production
vercel --prod

# Done! Your app is live
```

### Production Setup (Scalable)

**Infrastructure**:
- Frontend: Vercel (Global CDN)
- Backend: AWS EC2 or DigitalOcean Droplet
- Database: AWS RDS PostgreSQL
- Storage: AWS S3
- Domain: Cloudflare (DNS + DDoS protection)

**Monthly Cost**: ~$40-80

---

## 6. Post-Deployment Checklist

- [ ] Change SECRET_KEY to a secure random value
- [ ] Set up PostgreSQL instead of SQLite
- [ ] Configure CORS origins to your frontend domain
- [ ] Enable HTTPS on both frontend and backend
- [ ] Set up monitoring (Sentry for errors, Datadog for performance)
- [ ] Configure automatic backups for database
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Test WebSocket connections for proctoring
- [ ] Verify blockchain integrity after deployment
- [ ] Load test with 100+ concurrent users
- [ ] Set up email service for notifications
- [ ] Configure video storage (S3 or equivalent)
- [ ] Implement rate limiting for API endpoints
- [ ] Set up log aggregation (Papertrail, Loggly)

---

## 7. Monitoring and Scaling

### Add Health Check Endpoint

**backend/app/main.py**:
```python
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

### Scaling Recommendations

**< 100 users**: Single server (Railway/Render free tier)  
**100-1000 users**: 2-3 servers with load balancer  
**1000-10000 users**: Auto-scaling group (AWS ECS/K8s)  
**10000+ users**: Multi-region deployment with CDN

---

## Quick Commands Reference

```bash
# Deploy frontend to Vercel
cd frontend && vercel --prod

# Deploy backend to Railway
cd backend && railway up

# Check backend logs
railway logs

# Run database migrations
railway run alembic upgrade head

# View frontend build logs
vercel logs
```

---

## Support and Troubleshooting

**Common Issues**:

1. **CORS Errors**: Update `BACKEND_CORS_ORIGINS` in backend config
2. **WebSocket Fails**: Ensure wss:// protocol and proper proxy config
3. **Database Connection Fails**: Check DATABASE_URL format
4. **Build Fails**: Verify Node/Python versions match requirements

**Get Help**:
- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

---

## Estimated Costs

| Tier | Users | Monthly Cost | Services |
|------|-------|--------------|----------|
| Free | <100 | $0 | Railway + Vercel + Neon |
| Starter | 100-500 | $25 | Railway Pro + Vercel + Railway PG |
| Growth | 500-2000 | $75 | DigitalOcean + Vercel Pro + Managed DB |
| Scale | 2000-10000 | $300 | AWS/GCP Multi-region |
| Enterprise | 10000+ | $1000+ | Custom infrastructure |

---

**Recommendation**: Start with Railway (backend) + Vercel (frontend) + Neon (PostgreSQL) for free, then upgrade to paid tiers as you grow.
