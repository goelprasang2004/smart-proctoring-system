import { useRef, useEffect, useState } from 'react';
import { Camera, CameraOff, AlertTriangle, Users, UserX } from 'lucide-react';
import { FaceDetection } from '@mediapipe/face_detection';
import { Camera as MediaPipeCamera } from '@mediapipe/camera_utils';

const FaceMonitor = ({ onEvent, isActive, websocket }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const cameraRef = useRef(null);
    const faceDetectionRef = useRef(null);
    const lastEventTimeRef = useRef({});

    const [cameraReady, setCameraReady] = useState(false);
    const [faceCount, setFaceCount] = useState(0);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!isActive) return;

        initializeFaceDetection();

        // WebSocket Frame Stream
        let frameInterval;
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            frameInterval = setInterval(() => {
                sendFrameToBackend();
            }, 1000);
        }

        return () => {
            cleanup();
            if (frameInterval) clearInterval(frameInterval);
        };
    }, [isActive, websocket]); // Re-run if websocket connects later

    const sendFrameToBackend = () => {
        if (!videoRef.current || !canvasRef.current) return;

        // Use a temp canvas or the existing one?
        // Existing canvas has bounding boxes drawn on it! We want CLEAN frame.
        // So we need a temporary canvas to draw the video frame only.
        const video = videoRef.current;
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL('image/jpeg', 0.8);

        // Check WS state again
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify({ image: imageData }));
        }
    };

    const initializeFaceDetection = async () => {
        try {
            // Initialize MediaPipe Face Detection
            const faceDetection = new FaceDetection({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`;
                }
            });

            faceDetection.setOptions({
                model: 'full',
                minDetectionConfidence: 0.3
            });

            faceDetection.onResults(onFaceDetectionResults);
            faceDetectionRef.current = faceDetection;

            // Start camera
            await startCamera();
        } catch (err) {
            console.error('Face detection init error:', err);
            setError('Failed to initialize face detection');
        }
    };

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.onloadedmetadata = () => {
                    videoRef.current.play();
                    setCameraReady(true);

                    // Start MediaPipe camera
                    const camera = new MediaPipeCamera(videoRef.current, {
                        onFrame: async () => {
                            if (faceDetectionRef.current) {
                                await faceDetectionRef.current.send({ image: videoRef.current });
                            }
                        },
                        width: 640,
                        height: 480
                    });
                    camera.start();
                    cameraRef.current = camera;
                };
            }
        } catch (err) {
            console.error('Camera access error:', err);
            setError('Camera access denied. Please enable camera permissions.');
            triggerEvent('no_face', 'Camera access denied', 1.0);
        }
    };

    const onFaceDetectionResults = (results) => {
        const detections = results.detections || [];
        setFaceCount(detections.length);

        // Draw detection boxes
        drawDetections(detections);

        // Trigger events based on face count
        if (detections.length === 0) {
            triggerEvent('no_face', 'No face detected', 0.9);
        } else if (detections.length > 1) {
            triggerEvent('multiple_faces', `${detections.length} faces detected`, 0.95, {
                face_count: detections.length
            });
        }
    };

    const drawDetections = (detections) => {
        if (!canvasRef.current || !videoRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const video = videoRef.current;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Draw bounding boxes
        detections.forEach((detection) => {
            const box = detection.boundingBox;
            const x = box.xCenter * canvas.width - (box.width * canvas.width) / 2;
            const y = box.yCenter * canvas.height - (box.height * canvas.height) / 2;
            const w = box.width * canvas.width;
            const h = box.height * canvas.height;

            ctx.strokeStyle = detections.length > 1 ? '#ef4444' : '#10b981';
            ctx.lineWidth = 3;
            ctx.strokeRect(x, y, w, h);
        });
    };

    const triggerEvent = (eventType, description, confidence, extraMetadata = {}) => {
        // Throttle events - only send same event type once every 2 seconds
        const now = Date.now();
        const lastTime = lastEventTimeRef.current[eventType] || 0;

        if (now - lastTime < 2000) return; // Throttle

        lastEventTimeRef.current[eventType] = now;

        onEvent({
            event_type: eventType,
            description,
            metadata: {
                confidence_score: confidence,
                timestamp: new Date().toISOString(),
                source: 'mediapipe_face_detection',
                ...extraMetadata
            }
        });
    };

    const cleanup = () => {
        if (cameraRef.current) {
            cameraRef.current.stop();
        }
        if (videoRef.current && videoRef.current.srcObject) {
            videoRef.current.srcObject.getTracks().forEach(track => track.stop());
        }
    };

    return (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900 flex items-center">
                    <Camera className="h-5 w-5 mr-2 text-blue-600" />
                    Face Monitoring
                </h3>
                <div className="flex items-center space-x-2">
                    {cameraReady ? (
                        <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                            Active
                        </span>
                    ) : (
                        <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full">
                            Initializing...
                        </span>
                    )}
                </div>
            </div>

            {error ? (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
                    <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5 mr-2 flex-shrink-0" />
                    <span className="text-sm text-red-700">{error}</span>
                </div>
            ) : (
                <>
                    <div className="relative bg-gray-900 rounded-lg overflow-hidden mb-3">
                        <video
                            ref={videoRef}
                            className="w-full h-auto opacity-0 absolute"
                            playsInline
                            muted
                        />
                        <canvas
                            ref={canvasRef}
                            className="w-full h-auto"
                        />
                    </div>

                    <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center">
                            {faceCount === 0 ? (
                                <>
                                    <UserX className="h-4 w-4 text-red-500 mr-2" />
                                    <span className="text-red-700">No face detected</span>
                                </>
                            ) : faceCount === 1 ? (
                                <>
                                    <Users className="h-4 w-4 text-green-500 mr-2" />
                                    <span className="text-green-700">Face detected</span>
                                </>
                            ) : (
                                <>
                                    <Users className="h-4 w-4 text-red-500 mr-2" />
                                    <span className="text-red-700">{faceCount} faces detected</span>
                                </>
                            )}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default FaceMonitor;
