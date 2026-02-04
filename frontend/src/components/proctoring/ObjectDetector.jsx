import { useRef, useEffect, useState } from 'react';
import { Smartphone, BookOpen, AlertTriangle, Eye } from 'lucide-react';
import * as tf from '@tensorflow/tfjs';
import * as cocoSsd from '@tensorflow-models/coco-ssd';

// Suspicious objects to detect
const SUSPICIOUS_OBJECTS = ['cell phone', 'book', 'laptop', 'remote', 'mouse'];

const ObjectDetector = ({ videoRef, onEvent, isActive }) => {
    const modelRef = useRef(null);
    const detectionLoopRef = useRef(null);
    const lastEventTimeRef = useRef({});

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [detectedObjects, setDetectedObjects] = useState([]);

    useEffect(() => {
        if (!isActive) return;

        loadModel();

        return () => {
            if (detectionLoopRef.current) {
                cancelAnimationFrame(detectionLoopRef.current);
            }
        };
    }, [isActive]);

    const loadModel = async () => {
        try {
            setLoading(true);

            // Initialize TensorFlow.js
            await tf.ready();
            console.log('TensorFlow.js ready');

            // Load COCO-SSD model
            const model = await cocoSsd.load({
                base: 'lite_mobilenet_v2' // Faster model for real-time
            });

            modelRef.current = model;
            console.log('COCO-SSD model loaded');
            setLoading(false);

            // Start detection loop
            startDetectionLoop();

        } catch (err) {
            console.error('Model loading error:', err);
            setError('Failed to load object detection model');
            setLoading(false);
        }
    };

    const startDetectionLoop = () => {
        const detect = async () => {
            if (!modelRef.current || !videoRef?.current || !isActive) {
                detectionLoopRef.current = requestAnimationFrame(detect);
                return;
            }

            const video = videoRef.current;

            // Check if video is ready
            if (video.readyState !== 4) {
                detectionLoopRef.current = requestAnimationFrame(detect);
                return;
            }

            try {
                // Run detection
                const predictions = await modelRef.current.detect(video);

                // Filter for suspicious objects
                const suspicious = predictions.filter(pred =>
                    SUSPICIOUS_OBJECTS.includes(pred.class) && pred.score > 0.5
                );

                setDetectedObjects(suspicious);

                // Trigger events for suspicious objects
                suspicious.forEach(obj => {
                    triggerSuspiciousEvent(obj);
                });

            } catch (err) {
                console.error('Detection error:', err);
            }

            // Continue loop (slower rate to reduce CPU usage)
            setTimeout(() => {
                detectionLoopRef.current = requestAnimationFrame(detect);
            }, 500); // Run every 500ms
        };

        detect();
    };

    const triggerSuspiciousEvent = (detection) => {
        const eventType = getEventType(detection.class);
        const now = Date.now();
        const lastTime = lastEventTimeRef.current[eventType] || 0;

        // Throttle - only trigger same event type every 3 seconds
        if (now - lastTime < 3000) return;

        lastEventTimeRef.current[eventType] = now;

        const description = `${detection.class} detected with ${(detection.score * 100).toFixed(0)}% confidence`;

        onEvent({
            event_type: eventType,
            description,
            metadata: {
                object_class: detection.class,
                confidence_score: detection.score,
                bounding_box: detection.bbox,
                timestamp: new Date().toISOString(),
                source: 'tensorflow_coco_ssd'
            }
        });
    };

    const getEventType = (objectClass) => {
        switch (objectClass) {
            case 'cell phone':
                return 'suspicious_behavior';
            case 'book':
                return 'suspicious_behavior';
            case 'laptop':
                return 'suspicious_behavior';
            default:
                return 'suspicious_behavior';
        }
    };

    const getObjectIcon = (objectClass) => {
        switch (objectClass) {
            case 'cell phone':
                return <Smartphone className="h-4 w-4" />;
            case 'book':
                return <BookOpen className="h-4 w-4" />;
            default:
                return <Eye className="h-4 w-4" />;
        }
    };

    if (!isActive) return null;

    return (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900 flex items-center">
                    <Eye className="h-5 w-5 mr-2 text-purple-600" />
                    Object Detection
                </h3>
                <div className="flex items-center space-x-2">
                    {loading ? (
                        <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full">
                            Loading AI...
                        </span>
                    ) : error ? (
                        <span className="text-xs px-2 py-1 bg-red-100 text-red-800 rounded-full">
                            Error
                        </span>
                    ) : (
                        <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                            Active
                        </span>
                    )}
                </div>
            </div>

            {error ? (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-start">
                    <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 mr-2 flex-shrink-0" />
                    <span className="text-sm text-red-700">{error}</span>
                </div>
            ) : loading ? (
                <div className="p-4 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-2"></div>
                    <p className="text-sm text-gray-600">Loading object detection AI...</p>
                </div>
            ) : (
                <div className="space-y-2">
                    {detectedObjects.length > 0 ? (
                        detectedObjects.map((obj, index) => (
                            <div
                                key={index}
                                className="flex items-center justify-between p-2 bg-red-50 border border-red-200 rounded-lg"
                            >
                                <div className="flex items-center text-red-700">
                                    {getObjectIcon(obj.class)}
                                    <span className="ml-2 text-sm font-medium capitalize">
                                        {obj.class} detected!
                                    </span>
                                </div>
                                <span className="text-sm text-red-600 font-medium">
                                    {(obj.score * 100).toFixed(0)}%
                                </span>
                            </div>
                        ))
                    ) : (
                        <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-center">
                            <span className="text-sm text-green-700">
                                ✓ No suspicious objects detected
                            </span>
                        </div>
                    )}

                    <div className="mt-2 text-xs text-gray-500">
                        <p>Monitoring for: phones, books, laptops</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ObjectDetector;
