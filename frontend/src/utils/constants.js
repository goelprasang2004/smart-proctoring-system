// API Constants and Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Event types matching backend
export const PROCTORING_EVENTS = {
    FACE_DETECTION: 'face_detection',
    VOICE_DETECTION: 'voice_detection',
    STRESS_ALERT: 'stress_alert',
    TAB_SWITCH: 'tab_switch',
    WINDOW_BLUR: 'window_blur',
    MULTIPLE_FACES: 'multiple_faces',
    NO_FACE: 'no_face',
    SUSPICIOUS_BEHAVIOR: 'suspicious_behavior',
    COPY_ATTEMPT: 'copy_attempt',
    PASTE_ATTEMPT: 'paste_attempt',
    CUT_ATTEMPT: 'cut_attempt',
    RIGHT_CLICK_ATTEMPT: 'right_click_attempt',
    RESTRICTED_KEY_ATTEMPT: 'restricted_key_attempt',
    FULLSCREEN_EXIT: 'fullscreen_exit',
    SCREEN_RECORDING: 'screen_recording_detected'
};

// User roles
export const USER_ROLES = {
    ADMIN: 'admin',
    STUDENT: 'student',
    PROCTOR: 'proctor'
};

// Exam statuses
export const EXAM_STATUS = {
    DRAFT: 'draft',
    SCHEDULED: 'scheduled',
    ACTIVE: 'active',
    COMPLETED: 'completed',
    CANCELLED: 'cancelled'
};

// Attempt statuses
export const ATTEMPT_STATUS = {
    IN_PROGRESS: 'in_progress',
    SUBMITTED: 'submitted',
    AUTO_SUBMITTED: 'auto_submitted',
    ABANDONED: 'abandoned'
};

// Event severity (for UI display)
export const EVENT_SEVERITY = {
    [PROCTORING_EVENTS.FACE_DETECTION]: 'low',
    [PROCTORING_EVENTS.VOICE_DETECTION]: 'low',
    [PROCTORING_EVENTS.STRESS_ALERT]: 'medium',
    [PROCTORING_EVENTS.TAB_SWITCH]: 'medium',
    [PROCTORING_EVENTS.WINDOW_BLUR]: 'medium',
    [PROCTORING_EVENTS.MULTIPLE_FACES]: 'high',
    [PROCTORING_EVENTS.NO_FACE]: 'high',
    [PROCTORING_EVENTS.SUSPICIOUS_BEHAVIOR]: 'high',
    [PROCTORING_EVENTS.COPY_ATTEMPT]: 'high',
    [PROCTORING_EVENTS.PASTE_ATTEMPT]: 'high',
    [PROCTORING_EVENTS.CUT_ATTEMPT]: 'high',
    [PROCTORING_EVENTS.RIGHT_CLICK_ATTEMPT]: 'medium',
    [PROCTORING_EVENTS.RESTRICTED_KEY_ATTEMPT]: 'high',
    [PROCTORING_EVENTS.FULLSCREEN_EXIT]: 'high',
    [PROCTORING_EVENTS.SCREEN_RECORDING]: 'critical'
};

// Proctoring thresholds
export const PROCTORING_THRESHOLDS = {
    FACE_CHECK_INTERVAL: 1000, // Check face every 1 second
    VOICE_CHECK_INTERVAL: 500, // Check voice every 0.5 seconds
    EVENT_THROTTLE: 2000, // Send events max once per 2 seconds (same type)
    MAX_RETRIES: 3
};

// Toast/notification durations
export const NOTIFICATION_DURATION = {
    SUCCESS: 3000,
    ERROR: 5000,
    WARNING: 4000,
    INFO: 3000
};
