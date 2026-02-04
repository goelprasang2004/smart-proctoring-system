import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Clock, AlertTriangle, Send, Camera, Mic, CheckCircle, XCircle } from 'lucide-react';
import FaceMonitor from '../components/proctoring/FaceMonitor';
import VoiceMonitor from '../components/proctoring/VoiceMonitor';
import proctoringService from '../services/proctoringService';
import examService from '../services/examService';

const ExamSessionPage = () => {
    const { examId } = useParams();
    const navigate = useNavigate();

    // Setup phase states
    const [setupPhase, setSetupPhase] = useState(true);
    const [cameraPermission, setCameraPermission] = useState(null); // null, 'granted', 'denied'
    const [micPermission, setMicPermission] = useState(null);
    const [setupStream, setSetupStream] = useState(null);
    const setupVideoRef = useRef(null);

    const [exam, setExam] = useState(null);
    const [loading, setLoading] = useState(false);
    const [attemptId, setAttemptId] = useState(null);
    const [events, setEvents] = useState([]);
    const [timeRemaining, setTimeRemaining] = useState(0);
    const [proctoringActive, setProctoringActive] = useState(false);
    const [answers, setAnswers] = useState({});

    // Request permissions on mount
    useEffect(() => {
        requestPermissions();
        return () => {
            // Cleanup setup stream
            if (setupStream) {
                setupStream.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    // Set video source when stream is ready
    useEffect(() => {
        if (setupVideoRef.current && setupStream) {
            setupVideoRef.current.srcObject = setupStream;
        }
    }, [setupStream]);

    const requestPermissions = async () => {
        try {
            // Request both camera and microphone
            const stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });

            // Both granted
            setCameraPermission('granted');
            setMicPermission('granted');
            setSetupStream(stream);

        } catch (err) {
            console.error('Permission error:', err);

            // Try to get individual permissions
            try {
                const videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
                setCameraPermission('granted');
                setSetupStream(videoStream);
            } catch {
                setCameraPermission('denied');
            }

            try {
                await navigator.mediaDevices.getUserMedia({ audio: true });
                setMicPermission('granted');
            } catch {
                setMicPermission('denied');
            }
        }
    };

    const handleStartExam = async () => {
        if (cameraPermission !== 'granted' || micPermission !== 'granted') {
            alert('Please grant both camera and microphone permissions to start the exam.');
            return;
        }

        // Stop setup stream before starting exam
        if (setupStream) {
            setupStream.getTracks().forEach(track => track.stop());
            setSetupStream(null);
        }

        setSetupPhase(false);
        setLoading(true);

        try {
            // Request fullscreen mode
            try {
                await document.documentElement.requestFullscreen();
            } catch (err) {
                console.warn('Fullscreen request failed:', err);
                alert('Warning: Fullscreen mode is recommended for exams. Some features may not work properly.');
            }

            // Start exam attempt
            const attemptData = await examService.startAttempt(examId, {
                userAgent: navigator.userAgent,
                screen: {
                    width: window.screen.width,
                    height: window.screen.height
                }
            });

            setAttemptId(attemptData.id);

            const examData = {
                id: examId,
                title: attemptData.exam_title,
                duration_minutes: attemptData.duration_minutes,
                exam_config: attemptData.exam_config
            };

            setExam(examData);
            setProctoringActive(true);
            setTimeRemaining(attemptData.duration_minutes * 60);

            // Initialize WebSocket for proctoring
            initializeProctoringWebSocket(attemptData.id);

        } catch (err) {
            console.error('Failed to start exam:', err);
            alert('Failed to start exam: ' + (err.response?.data?.error || err.message));
            navigate('/exams');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!exam || !attemptId) return;

        // Timer countdown
        const timer = setInterval(() => {
            setTimeRemaining(prev => {
                if (prev <= 1) {
                    handleSubmit();
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        // Detect tab switch
        const handleVisibilityChange = () => {
            if (document.hidden) {
                handleProctoringEvent({
                    event_type: 'tab_switch',
                    description: 'Student switched tab or window',
                    metadata: {
                        timestamp: new Date().toISOString(),
                        source: 'browser_api'
                    }
                });
            }
        };

        // Detect window blur
        const handleBlur = () => {
            handleProctoringEvent({
                event_type: 'window_blur',
                description: 'Window lost focus',
                metadata: {
                    timestamp: new Date().toISOString(),
                    source: 'browser_api'
                }
            });
        };

        // Prevent copy-paste
        const handleCopy = (e) => {
            e.preventDefault();
            handleProctoringEvent({
                event_type: 'copy_attempt',
                description: 'Student attempted to copy content',
                metadata: {
                    timestamp: new Date().toISOString(),
                    source: 'browser_api'
                }
            });
            alert('Copying is disabled during the exam!');
        };

        const handlePaste = (e) => {
            e.preventDefault();
            handleProctoringEvent({
                event_type: 'paste_attempt',
                description: 'Student attempted to paste content',
                metadata: {
                    timestamp: new Date().toISOString(),
                    source: 'browser_api'
                }
            });
            alert('Pasting is disabled during the exam!');
        };

        const handleCut = (e) => {
            e.preventDefault();
            handleProctoringEvent({
                event_type: 'cut_attempt',
                description: 'Student attempted to cut content',
                metadata: {
                    timestamp: new Date().toISOString(),
                    source: 'browser_api'
                }
            });
        };

        // Prevent right-click context menu
        const handleContextMenu = (e) => {
            e.preventDefault();
            handleProctoringEvent({
                event_type: 'right_click_attempt',
                description: 'Student attempted to open context menu',
                metadata: {
                    timestamp: new Date().toISOString(),
                    source: 'browser_api'
                }
            });
        };

        // Prevent print screen and screenshots
        const handleKeyDown = (e) => {
            // Prevent PrintScreen, Ctrl+P, Ctrl+Shift+I (DevTools)
            if (
                e.key === 'PrintScreen' ||
                (e.ctrlKey && e.key === 'p') ||
                (e.ctrlKey && e.shiftKey && e.key === 'I') ||
                (e.ctrlKey && e.shiftKey && e.key === 'J') ||
                (e.ctrlKey && e.shiftKey && e.key === 'C') ||
                e.key === 'F12'
            ) {
                e.preventDefault();
                handleProctoringEvent({
                    event_type: 'restricted_key_attempt',
                    description: `Student attempted restricted key: ${e.key}`,
                    metadata: {
                        timestamp: new Date().toISOString(),
                        key: e.key,
                        source: 'browser_api'
                    }
                });
                alert('This action is not allowed during the exam!');
            }
        };

        // Detect fullscreen exit
        const handleFullscreenChange = () => {
            if (!document.fullscreenElement) {
                handleProctoringEvent({
                    event_type: 'fullscreen_exit',
                    description: 'Student exited fullscreen mode',
                    metadata: {
                        timestamp: new Date().toISOString(),
                        source: 'browser_api'
                    }
                });
                // Try to re-enter fullscreen
                setTimeout(() => {
                    if (proctoringActive && !document.fullscreenElement) {
                        document.documentElement.requestFullscreen().catch(err => {
                            console.warn('Could not re-enter fullscreen:', err);
                        });
                    }
                }, 100);
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('blur', handleBlur);
        document.addEventListener('copy', handleCopy);
        document.addEventListener('paste', handlePaste);
        document.addEventListener('cut', handleCut);
        document.addEventListener('contextmenu', handleContextMenu);
        document.addEventListener('keydown', handleKeyDown);
        document.addEventListener('fullscreenchange', handleFullscreenChange);

        return () => {
            clearInterval(timer);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            window.removeEventListener('blur', handleBlur);
            document.removeEventListener('copy', handleCopy);
            document.removeEventListener('paste', handlePaste);
            document.removeEventListener('cut', handleCut);
            document.removeEventListener('contextmenu', handleContextMenu);
            document.removeEventListener('keydown', handleKeyDown);
            document.removeEventListener('fullscreenchange', handleFullscreenChange);
        };
    }, [exam, attemptId]);

    // WebSocket Reference
    const wsRef = useRef(null);

    const initializeProctoringWebSocket = (id) => {
        wsRef.current = proctoringService.connectToProctoring(
            id,
            (data) => {
                // Handle messages from backend
                if (data.anomalies && data.anomalies.length > 0) {
                    data.anomalies.forEach(anomaly => {
                        handleProctoringEvent({
                            event_type: anomaly,
                            description: `Detected ${anomaly}`,
                            metadata: { source: 'ai_backend', timestamp: new Date().toISOString() }
                        });
                    });
                }
            },
            (error) => {
                console.error("Proctoring connection error", error);
            }
        );
    };

    // Pass WebSocket to FaceMonitor
    useEffect(() => {
        // This is just to ensure FaceMonitor gets the updated WS if it changes/reconnects
    }, [wsRef.current]);

    const autoTerminate = async (reason, eventType) => {
        if (!attemptId) return;

        // Prevent multiple termination calls
        if (!proctoringActive) return;
        setProctoringActive(false);

        try {
            await examService.terminateAttempt(attemptId, {
                reason,
                event_type: eventType,
                metadata: {
                    terminated_at: new Date().toISOString()
                }
            });

            alert(`Exam Terminated: ${reason}`);
            navigate('/exams');
        } catch (err) {
            console.error('Failed to terminate exam:', err);
            alert('Exam terminated due to violation.');
            navigate('/exams');
        }
    };

    const handleProctoringEvent = async (event) => {
        if (!attemptId) return;

        // Auto-terminate checks
        if (event.event_type === 'multiple_faces') {
            await autoTerminate('Multiple persons detected', 'multiple_faces');
            return;
        }

        if (event.event_type === 'tab_switch') {
            await autoTerminate('Tab/Window switch detected', 'tab_switch');
            return;
        }

        if (event.event_type === 'window_blur') {
            // Optional: You could allow 1 warning for blur, but user asked for strict "close ho jave"
            // Uncomment check below if you want to be lenient
            // if (blurCount > 1) { ... }
            await autoTerminate('Window lost focus', 'window_blur');
            return;
        }

        try {
            await proctoringService.logEvent(
                attemptId,
                event.event_type,
                event.description,
                event.metadata
            );

            setEvents(prev => [{
                ...event,
                timestamp: new Date().toISOString()
            }, ...prev].slice(0, 10));

        } catch (err) {
            console.error('Failed to log event:', err);
        }
    };

    const handleAnswerSelect = (questionId, answer) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: answer
        }));
    };

    const handleSubmit = async () => {
        if (!attemptId) return;

        if (!window.confirm('Are you sure you want to submit your exam? This action cannot be undone.')) {
            return;
        }

        setProctoringActive(false);

        try {
            // Close WebSocket if open
            if (wsRef.current) {
                wsRef.current.close();
            }
            await examService.submitAttempt(attemptId, answers);
            alert('Exam submitted successfully!');
            navigate('/dashboard');
        } catch (err) {
            console.error('Failed to submit exam:', err);
            alert('Failed to submit exam: ' + (err.response?.data?.error || err.message));
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // Setup Phase Screen
    if (setupPhase) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-8">
                    <h1 className="text-2xl font-bold text-gray-900 text-center mb-2">
                        Exam Setup
                    </h1>
                    <p className="text-gray-600 text-center mb-8">
                        Please grant camera and microphone access to start the exam
                    </p>

                    {/* Camera Preview */}
                    <div className="bg-gray-900 rounded-lg overflow-hidden mb-6 aspect-video relative">
                        {cameraPermission === 'granted' ? (
                            <video
                                ref={setupVideoRef}
                                autoPlay
                                playsInline
                                muted
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center">
                                <div className="text-center">
                                    <Camera className="w-16 h-16 text-gray-600 mx-auto mb-2" />
                                    <p className="text-gray-400">
                                        {cameraPermission === 'denied'
                                            ? 'Camera access denied'
                                            : 'Requesting camera access...'}
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Permission Status */}
                    <div className="space-y-3 mb-8">
                        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                            <div className="flex items-center">
                                <Camera className="w-5 h-5 text-gray-600 mr-3" />
                                <span className="font-medium">Camera</span>
                            </div>
                            {cameraPermission === 'granted' ? (
                                <div className="flex items-center text-green-600">
                                    <CheckCircle className="w-5 h-5 mr-1" />
                                    <span>Ready</span>
                                </div>
                            ) : cameraPermission === 'denied' ? (
                                <div className="flex items-center text-red-600">
                                    <XCircle className="w-5 h-5 mr-1" />
                                    <span>Denied</span>
                                </div>
                            ) : (
                                <span className="text-gray-500">Checking...</span>
                            )}
                        </div>

                        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                            <div className="flex items-center">
                                <Mic className="w-5 h-5 text-gray-600 mr-3" />
                                <span className="font-medium">Microphone</span>
                            </div>
                            {micPermission === 'granted' ? (
                                <div className="flex items-center text-green-600">
                                    <CheckCircle className="w-5 h-5 mr-1" />
                                    <span>Ready</span>
                                </div>
                            ) : micPermission === 'denied' ? (
                                <div className="flex items-center text-red-600">
                                    <XCircle className="w-5 h-5 mr-1" />
                                    <span>Denied</span>
                                </div>
                            ) : (
                                <span className="text-gray-500">Checking...</span>
                            )}
                        </div>
                    </div>

                    {/* Warning if permissions denied */}
                    {(cameraPermission === 'denied' || micPermission === 'denied') && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                            <div className="flex items-start">
                                <AlertTriangle className="w-5 h-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                                <div>
                                    <p className="text-red-800 font-medium">Permission Required</p>
                                    <p className="text-red-700 text-sm mt-1">
                                        Please allow camera and microphone access in your browser settings and refresh the page.
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Start Button */}
                    <button
                        onClick={handleStartExam}
                        disabled={cameraPermission !== 'granted' || micPermission !== 'granted'}
                        className={`w-full py-4 rounded-lg font-semibold text-lg transition-all ${cameraPermission === 'granted' && micPermission === 'granted'
                            ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            }`}
                    >
                        {cameraPermission === 'granted' && micPermission === 'granted'
                            ? 'Start Exam'
                            : 'Waiting for Permissions...'}
                    </button>

                    <button
                        onClick={() => navigate('/exams')}
                        className="w-full mt-3 py-3 text-gray-600 hover:text-gray-900 font-medium"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Top Bar */}
            <div className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <h1 className="text-xl font-semibold text-gray-900">{exam?.title}</h1>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center text-lg font-semibold text-gray-900">
                                <Clock className="h-5 w-5 mr-2" />
                                {formatTime(timeRemaining)}
                            </div>
                            <button
                                onClick={handleSubmit}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center"
                            >
                                <Send className="h-4 w-4 mr-2" />
                                Submit
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main Exam Area */}
                    <div className="lg:col-span-2">
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <h2 className="text-lg font-semibold text-gray-900 mb-4">Exam Questions</h2>
                            <div className="space-y-6">
                                {exam?.exam_config?.questions && exam.exam_config.questions.length > 0 ? (
                                    exam.exam_config.questions.map((question, index) => (
                                        <div key={question.id || index} className="p-4 border border-gray-200 rounded-lg">
                                            <div className="mb-3">
                                                <span className="text-sm font-medium text-blue-600">Question {index + 1}</span>
                                                <span className="ml-2 text-sm text-gray-500">({question.points || 10} points)</span>
                                            </div>
                                            <p className="text-gray-900 font-medium mb-4">{question.text}</p>

                                            {question.type === 'multiple_choice' && question.options && (
                                                <div className="space-y-2">
                                                    {question.options.map((option, optIndex) => (
                                                        <label
                                                            key={optIndex}
                                                            className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${answers[question.id] === option
                                                                ? 'border-blue-500 bg-blue-50'
                                                                : 'border-gray-200 hover:bg-gray-50'
                                                                }`}
                                                        >
                                                            <input
                                                                type="radio"
                                                                name={`question-${question.id}`}
                                                                value={option}
                                                                checked={answers[question.id] === option}
                                                                onChange={(e) => handleAnswerSelect(question.id, e.target.value)}
                                                                className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                                                            />
                                                            <span className="ml-3 text-gray-900">{option}</span>
                                                        </label>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    ))
                                ) : (
                                    <div className="p-8 text-center text-gray-500">
                                        <p className="mb-2">No questions available for this exam</p>
                                        <p className="text-sm">Please contact your administrator</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Proctoring Sidebar */}
                    <div className="lg:col-span-1 space-y-4">
                        <FaceMonitor
                            onEvent={handleProctoringEvent}
                            isActive={proctoringActive}
                            websocket={wsRef.current}
                        />

                        {/* Voice Monitor */}
                        <VoiceMonitor
                            onEvent={handleProctoringEvent}
                            isActive={proctoringActive}
                        />

                        {/* Event Log */}
                        <div className="bg-white rounded-lg border border-gray-200 p-4">
                            <h3 className="font-semibold text-gray-900 mb-3">Recent Events</h3>
                            {events.length === 0 ? (
                                <p className="text-sm text-gray-500">No events logged</p>
                            ) : (
                                <div className="space-y-2">
                                    {events.map((event, index) => (
                                        <div key={index} className="text-xs p-2 bg-gray-50 rounded border border-gray-200">
                                            <div className="font-medium text-gray-900">{event.event_type}</div>
                                            <div className="text-gray-600">{event.description}</div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ExamSessionPage;
