# Smart Proctoring System

A comprehensive AI-powered exam proctoring system with blockchain-based audit trail.

## Features

### 🎯 Core Features
- **Real-time AI Proctoring**: Multiple face detection, voice monitoring, object detection
- **Blockchain Audit Trail**: Immutable logging of all proctoring events
- **Exam Management**: Create, assign, and manage exams
- **Student Portal**: Take exams with real-time monitoring
- **Admin Dashboard**: View analytics, suspicious attempts, and blockchain logs

### 🔐 Security Features
- JWT-based authentication
- Role-based access control (Admin/Student)
- Auto-termination on violations
- Tab switch detection
- Copy/paste prevention
- Fullscreen enforcement

### 🤖 AI Proctoring Features
- **Face Detection**: MediaPipe-based face recognition
- **Multiple Face Detection**: Detects if multiple people are present
- **Voice Detection**: Real-time audio level monitoring
- **Object Detection**: TensorFlow COCO-SSD for phone detection
- **Tab Switch Detection**: Monitors browser activity
- **Behavioral Analysis**: Tracks suspicious patterns

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Authentication**: JWT with OAuth2
- **AI/ML**: OpenCV, MediaPipe
- **Blockchain**: Custom implementation with ECDSA signatures

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: TailwindCSS
- **AI Libraries**: MediaPipe Face Detection, TensorFlow.js
- **State Management**: Context API
- **HTTP Client**: Axios

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite by default)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create initial admin user
python create_initial_user.py

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## Default Credentials

### Admin
- Email: `admin@gmail.com`
- Password: `StrongPassword123!`

### Student
- Email: `student@example.com`
- Password: `TestStudent123!`

## Deployment

### Deploy to Render.com (Free)

1. Fork/Clone this repository
2. Create account on [Render.com](https://render.com)
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml` and deploy everything

The backend will automatically:
- Create a PostgreSQL database
- Set up environment variables
- Deploy the FastAPI application

### Environment Variables

For production deployment, set these variables:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520
```

## API Endpoints

### Authentication
- `POST /api/v1/login/access-token` - Login and get JWT token

### Exams (Admin)
- `GET /api/v1/exams/` - Get all exams
- `POST /api/v1/exams/` - Create new exam
- `GET /api/v1/exams/{exam_id}` - Get exam details
- `PATCH /api/v1/exams/{exam_id}/status/` - Update exam status
- `POST /api/v1/exams/{exam_id}/assign/` - Assign exam to students

### Exams (Student)
- `GET /api/v1/exams/available` - Get assigned exams
- `GET /api/v1/exams/{exam_id}/details` - Get exam details

### Attempts
- `POST /api/v1/attempts/start` - Start exam attempt
- `POST /api/v1/attempts/{attempt_id}/submit` - Submit exam
- `POST /api/v1/attempts/{attempt_id}/terminate` - Terminate exam
- `GET /api/v1/attempts/my-results` - Get student results

### Proctoring
- `WS /api/v1/proctoring/ws/{attempt_id}` - WebSocket for real-time monitoring
- `POST /api/v1/proctoring/event` - Log proctoring event

### Admin
- `GET /api/v1/admin/students` - Get all students
- `POST /api/v1/admin/students` - Create new student

### Blockchain
- `GET /api/v1/blockchain/summary` - Get blockchain statistics
- `GET /api/v1/blockchain/blocks` - Get blockchain blocks
- `GET /api/v1/blockchain/verify` - Verify blockchain integrity

## Project Structure

```
smart-proctoring-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── admin.py
│   │   │   │   ├── attempts.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── blockchain.py
│   │   │   │   ├── exams.py
│   │   │   │   └── proctoring.py
│   │   │   ├── api.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── blockchain.py
│   │   │   ├── exam.py
│   │   │   ├── exam_assignment.py
│   │   │   ├── proctoring.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── blockchain.py
│   │   │   ├── exam_service.py
│   │   │   └── proctoring.py
│   │   └── main.py
│   ├── requirements.txt
│   └── create_initial_user.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── proctoring/
│   │   │   │   ├── FaceMonitor.jsx
│   │   │   │   ├── VoiceMonitor.jsx
│   │   │   │   └── ObjectDetector.jsx
│   │   │   └── layouts/
│   │   ├── pages/
│   │   │   ├── admin/
│   │   │   └── student/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.js
└── render.yaml
```

## Features Demo

### Admin Dashboard
- Create and manage exams
- Assign exams to students
- View all exam attempts
- Monitor suspicious activities
- View blockchain audit trail

### Student Portal
- View assigned exams
- Take exams with proctoring
- Real-time face and voice monitoring
- View exam results

### Proctoring Features
- Continuous face detection
- Multiple face detection → Auto-terminate
- Voice level monitoring
- Tab switch detection → Auto-terminate
- Window blur detection → Auto-terminate
- Object detection (phones, etc.)
- All events logged to blockchain

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- MediaPipe for face detection
- TensorFlow.js for object detection
- FastAPI for the amazing backend framework
- React and Vite for the frontend
