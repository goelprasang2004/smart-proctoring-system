import { useRef, useEffect, useState } from 'react';
import { Mic, MicOff, Volume2, AlertTriangle } from 'lucide-react';

const VoiceMonitor = ({ onEvent, isActive }) => {
    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const microphoneRef = useRef(null);
    const animationFrameRef = useRef(null);
    const lastEventTimeRef = useRef({});

    const [micReady, setMicReady] = useState(false);
    const [audioLevel, setAudioLevel] = useState(0);
    const [error, setError] = useState('');
    const [isTalking, setIsTalking] = useState(false);

    useEffect(() => {
        if (!isActive) return;

        initializeAudio();

        return () => {
            cleanup();
        };
    }, [isActive]);

    const initializeAudio = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const analyser = audioContext.createAnalyser();
            const microphone = audioContext.createMediaStreamSource(stream);

            analyser.fftSize = 256;
            microphone.connect(analyser);

            audioContextRef.current = audioContext;
            analyserRef.current = analyser;
            microphoneRef.current = stream;

            setMicReady(true);
            startAnalysis();
        } catch (err) {
            console.error('Microphone access error:', err);
            setError('Microphone access denied. Please enable microphone permissions.');
            triggerEvent('voice_detection', 'Microphone access denied', 1.0);
        }
    };

    const startAnalysis = () => {
        const bufferLength = analyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        let talkingStartTime = null;
        let lastSpikeTime = null;

        const analyze = () => {
            if (!analyserRef.current) return;

            analyserRef.current.getByteFrequencyData(dataArray);

            // Calculate average volume
            const average = dataArray.reduce((a, b) => a + b) / bufferLength;
            const normalizedLevel = Math.min(100, (average / 255) * 100);

            setAudioLevel(normalizedLevel);

            const now = Date.now();

            // Detect talking (sustained audio above threshold)
            if (normalizedLevel > 20) {
                if (!talkingStartTime) {
                    talkingStartTime = now;
                    setIsTalking(true);
                } else if (now - talkingStartTime > 3000) {
                    // Talking for more than 3 seconds
                    triggerEvent('voice_detection', 'Continuous talking detected', 0.8, {
                        audio_level: normalizedLevel,
                        duration: now - talkingStartTime
                    });
                }
            } else {
                if (talkingStartTime) {
                    setIsTalking(false);
                    talkingStartTime = null;
                }
            }

            // Detect sudden audio spikes (background noise)
            if (normalizedLevel > 50) {
                if (!lastSpikeTime || now - lastSpikeTime > 5000) {
                    triggerEvent('voice_detection', 'High background noise detected', 0.7, {
                        audio_level: normalizedLevel
                    });
                    lastSpikeTime = now;
                }
            }

            animationFrameRef.current = requestAnimationFrame(analyze);
        };

        analyze();
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
                source: 'web_audio_api',
                ...extraMetadata
            }
        });
    };

    const cleanup = () => {
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
        }
        if (audioContextRef.current) {
            audioContextRef.current.close();
        }
        if (microphoneRef.current) {
            microphoneRef.current.getTracks().forEach(track => track.stop());
        }
    };

    return (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900 flex items-center">
                    <Mic className="h-5 w-5 mr-2 text-blue-600" />
                    Voice Monitoring
                </h3>
                <div className="flex items-center space-x-2">
                    {micReady ? (
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
                    {/* Audio Level Visualizer */}
                    <div className="mb-3">
                        <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                            <span>Audio Level</span>
                            <span>{Math.round(audioLevel)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                            <div
                                className={`h-full transition-all duration-100 ${audioLevel > 50 ? 'bg-red-500' : audioLevel > 20 ? 'bg-yellow-500' : 'bg-green-500'
                                    }`}
                                style={{ width: `${audioLevel}%` }}
                            />
                        </div>
                    </div>

                    {/* Status Indicator */}
                    <div className="flex items-center text-sm">
                        {isTalking ? (
                            <>
                                <Volume2 className="h-4 w-4 text-yellow-500 mr-2 animate-pulse" />
                                <span className="text-yellow-700">Voice detected</span>
                            </>
                        ) : (
                            <>
                                <MicOff className="h-4 w-4 text-gray-400 mr-2" />
                                <span className="text-gray-600">No voice detected</span>
                            </>
                        )}
                    </div>
                </>
            )}

            {/* Privacy Notice */}
            <div className="mt-3 pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-500">
                    🔒 No audio is recorded or sent. Only event metadata is logged.
                </p>
            </div>
        </div>
    );
};

export default VoiceMonitor;
