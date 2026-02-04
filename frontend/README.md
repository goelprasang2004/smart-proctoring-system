# Smart Proctoring System - Frontend

Production-ready React frontend for the Smart Proctoring System with client-side AI proctoring.

## Features

### 🎯 Core Functionality
- **Student Dashboard** - View and take available exams
- **Admin Dashboard** - Manage exams, view analytics
- **Real-time Proctoring** - Face and voice monitoring during exams
- **Blockchain Audit** - View immutable audit trails

### 🤖 AI Proctoring (Browser-Side Only)
- **Face Detection** - MediaPipe Face Detection API
  - No face detection
  - Multiple faces detection
  - Face position monitoring
- **Voice Monitoring** - Web Audio API
  - Continuous talking detection
  - Background noise detection
  - Audio level visualization

**Privacy:** No images, videos, or audio recordings are stored or sent to the backend. Only structured JSON event metadata is transmitted.

## Tech Stack

- **Framework:** React 18 + Vite
- **Styling:** Tailwind CSS
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **AI:** MediaPipe Face Detection, Web Audio API
- **Icons:** Lucide React
- **Charts:** Recharts

## Setup

### Prerequisites
- Node.js 18+ 
- Backend API running on http://localhost:5000

### Installation

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Set environment variable (optional)
echo "VITE_API_URL=http://localhost:5000/api" > .env

# Start development server
npm run dev
```

Server runs on `http://localhost:5173`

## Project Structure

```
src/
├── components/
│   ├── layout/          # Navbar, Layout
│   └── proctoring/      # FaceMonitor, VoiceMonitor
├── contexts/            # AuthContext
├── pages/               # LoginPage, DashboardPage, ExamSessionPage
├── services/            # API services (auth, exam, proctoring, blockchain)
├── utils/               # Constants, helpers
└── App.jsx              # Main app with routing
```

## Environment Variables

Create `.env` file:

```
VITE_API_URL=http://localhost:5000/api
```

## Available Scripts

```bash
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview production build
```

## Key Components

### Proctoring Components

1. **FaceMonitor** (`components/proctoring/FaceMonitor.jsx`)
   - MediaPipe face detection
   - Real-time video canvas with detection boxes
   - Throttled event logging (2s interval)

2. **VoiceMonitor**  (`components/proctoring/VoiceMonitor.jsx`)
   - Web Audio API analysis
   - Audio level visualization
   - Talking/noise detection

### Pages

1. **LoginPage** - Authentication with demo credentials
2. **DashboardPage** - Student exam list
3. **ExamSessionPage** - Exam taking with live proctoring

## Security & Privacy

### Data Handling
- **Tokens:** Stored in localStorage with automatic refresh
- **No Biometric Storage:** Face/voice data processed client-side only
- **Event Metadata Only:** JSON events sent to backend:
  ```json
  {
    "event_type": "multiple_faces",
    "description": "2 faces detected",
    "metadata": {
      "confidence_score": 0.95,
      "timestamp": "2026-01-18T...",
      "source": "mediapipe_face_detection"
    }
  }
  ```

### Browser Permissions Required
- Camera access (for face detection)
- Microphone access (for voice monitoring)

## Demo Credentials

**Admin:**
- Email: `admin@gmail.com`
- Password: `StrongPassword123!`

**Student:**
- Email: `student@example.com`
- Password: `TestStudent123!`

## Production Build

```bash
npm run build
# Output: dist/
```

Deploy `dist/` folder to:
- Vercel
- Netlify
- Any static hosting

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## API Integration

All API calls use Axios with automatic:
- Token injection
- Token refresh on 401
- Error handling

### Services
- `authService` - Login, register, logout
- `examService` - Exam CRUD operations
- `proctoringService` - Event logging
- `blockchainService` - Audit trail queries

## Development Notes

### Event Throttling
Proctoring events are throttled to prevent backend spam:
- Same event type: Max once per 2 seconds
- Different event types: Logged immediately

### State Management
- **AuthContext:** User authentication state
- **Local State:** Component-specific (React hooks)
- No global state library needed

## Troubleshooting

### Camera/Mic Not Working
1. Check browser permissions
2. Ensure HTTPS in production
3. Check browser console for errors

### API Connection Failed
1. Verify backend is running
2. Check VITE_API_URL in `.env`
3. Check CORS configuration on backend

## License

Educational/Demonstration purposes

---

**Built with privacy-first AI proctoring** 🔒
