/**
 * Advanced Proctoring Service
 * Edge-native AI processing, behavioral biometrics, and stress detection
 */

class AdvancedProctoringService {
    constructor() {
        this.keystrokeBuffer = [];
        this.mouseBuffer = [];
        this.baselineTyping = null;
        this.baselineMouse = null;
        this.stressLevel = 0;
        this.tfModel = null;
    }

    /**
     * Initialize TensorFlow.js for edge-native processing
     */
    async initializeTensorFlow() {
        try {
            // Load TensorFlow.js (assumes it's loaded via CDN in index.html)
            if (typeof tf === 'undefined') {
                console.warn('TensorFlow.js not loaded');
                return false;
            }

            // Load pre-trained face detection model (BlazeFace)
            this.tfModel = await tf.loadGraphModel('https://tfhub.dev/tensorflow/tfjs-model/blazeface/1/default/1', { fromTFHub: true });
            return true;
        } catch (error) {
            console.error('Failed to load TensorFlow model:', error);
            return false;
        }
    }

    /**
     * Edge-native face detection using TensorFlow.js
     * Returns metadata only, no raw video sent to server
     */
    async detectFacesLocal(videoElement) {
        if (!this.tfModel) return null;

        try {
            const predictions = await this.tfModel.estimateFaces(videoElement, false);
            
            const metadata = {
                timestamp: Date.now(),
                faceCount: predictions.length,
                faces: predictions.map(pred => ({
                    probability: pred.probability,
                    boundingBox: pred.topLeft.concat(pred.bottomRight),
                })),
                anomalies: []
            };

            // Detect anomalies
            if (predictions.length === 0) {
                metadata.anomalies.push({ type: 'no_face', confidence: 0.95 });
            } else if (predictions.length > 1) {
                metadata.anomalies.push({ type: 'multiple_faces', confidence: 0.98 });
            } else if (predictions[0].probability < 0.7) {
                metadata.anomalies.push({ type: 'low_face_confidence', confidence: predictions[0].probability });
            }

            return metadata;
        } catch (error) {
            console.error('Face detection error:', error);
            return null;
        }
    }

    /**
     * Keystroke Dynamics - Continuous Behavioral Biometrics
     * Tracks typing rhythm to detect impostor mid-exam
     */
    captureKeystroke(event) {
        const keystroke = {
            key: event.key,
            timestamp: Date.now(),
            duration: 0, // Will be calculated on keyup
            pressure: event.pressure || 0
        };

        // Store for analysis
        this.keystrokeBuffer.push(keystroke);

        // Keep only last 100 keystrokes
        if (this.keystrokeBuffer.length > 100) {
            this.keystrokeBuffer.shift();
        }

        // If baseline not set, establish it after 50 keystrokes
        if (!this.baselineTyping && this.keystrokeBuffer.length >= 50) {
            this.baselineTyping = this.calculateTypingProfile(this.keystrokeBuffer);
        }

        // Check for behavioral change
        if (this.baselineTyping && this.keystrokeBuffer.length >= 20) {
            const currentProfile = this.calculateTypingProfile(this.keystrokeBuffer.slice(-20));
            const deviation = this.compareProfiles(this.baselineTyping, currentProfile);
            
            if (deviation > 0.35) { // 35% deviation threshold
                return {
                    anomaly: 'typing_pattern_change',
                    confidence: Math.min(deviation, 0.975),
                    message: 'Abrupt change in typing pattern detected'
                };
            }
        }

        return null;
    }

    /**
     * Mouse Movement Pattern Analysis
     */
    captureMouseMovement(event) {
        const movement = {
            x: event.clientX,
            y: event.clientY,
            timestamp: Date.now(),
            type: event.type // mousemove, click, etc.
        };

        this.mouseBuffer.push(movement);

        if (this.mouseBuffer.length > 200) {
            this.mouseBuffer.shift();
        }

        // Establish baseline
        if (!this.baselineMouse && this.mouseBuffer.length >= 100) {
            this.baselineMouse = this.calculateMouseProfile(this.mouseBuffer);
        }

        // Detect changes
        if (this.baselineMouse && this.mouseBuffer.length >= 50) {
            const currentProfile = this.calculateMouseProfile(this.mouseBuffer.slice(-50));
            const deviation = this.compareProfiles(this.baselineMouse, currentProfile);
            
            if (deviation > 0.40) {
                return {
                    anomaly: 'mouse_pattern_change',
                    confidence: Math.min(deviation, 0.975),
                    message: 'Unusual mouse movement pattern detected'
                };
            }
        }

        return null;
    }

    /**
     * Calculate typing profile (average timing between keystrokes)
     */
    calculateTypingProfile(keystrokes) {
        if (keystrokes.length < 2) return null;

        const intervals = [];
        for (let i = 1; i < keystrokes.length; i++) {
            intervals.push(keystrokes[i].timestamp - keystrokes[i - 1].timestamp);
        }

        return {
            avgInterval: intervals.reduce((a, b) => a + b, 0) / intervals.length,
            stdDev: this.calculateStdDev(intervals),
            wpm: (60000 / (intervals.reduce((a, b) => a + b, 0) / intervals.length)) * 5 // words per minute
        };
    }

    /**
     * Calculate mouse profile
     */
    calculateMouseProfile(movements) {
        if (movements.length < 2) return null;

        const velocities = [];
        const accelerations = [];
        
        for (let i = 1; i < movements.length; i++) {
            const dx = movements[i].x - movements[i - 1].x;
            const dy = movements[i].y - movements[i - 1].y;
            const dt = movements[i].timestamp - movements[i - 1].timestamp;
            
            if (dt > 0) {
                const velocity = Math.sqrt(dx * dx + dy * dy) / dt;
                velocities.push(velocity);
            }
        }

        return {
            avgVelocity: velocities.reduce((a, b) => a + b, 0) / velocities.length,
            stdDev: this.calculateStdDev(velocities)
        };
    }

    /**
     * Compare two behavioral profiles
     */
    compareProfiles(baseline, current) {
        if (!baseline || !current) return 0;

        // Calculate normalized difference
        const avgDiff = Math.abs(baseline.avgInterval - current.avgInterval) / baseline.avgInterval;
        const stdDiff = Math.abs(baseline.stdDev - current.stdDev) / (baseline.stdDev || 1);

        return (avgDiff + stdDiff) / 2;
    }

    /**
     * Calculate standard deviation
     */
    calculateStdDev(values) {
        const avg = values.reduce((a, b) => a + b, 0) / values.length;
        const squareDiffs = values.map(value => Math.pow(value - avg, 2));
        return Math.sqrt(squareDiffs.reduce((a, b) => a + b, 0) / values.length);
    }

    /**
     * Stress Detection using rPPG (Remote Photoplethysmography)
     * Analyzes subtle color changes in face to estimate heart rate
     */
    async detectStressLevel(videoElement) {
        // This is a simplified version - full rPPG requires advanced signal processing
        // Here we'll use a heuristic based on movement and behavioral patterns
        
        const indicators = {
            excessiveMovement: this.detectExcessiveMovement(),
            rapidTyping: this.keystrokeBuffer.length > 50 && this.baselineTyping?.wpm > 80,
            erraticMouse: this.mouseBuffer.length > 100 && this.baselineMouse?.stdDev > 0.5,
        };

        // Calculate stress score (0-1)
        const stressScore = Object.values(indicators).filter(v => v).length / Object.keys(indicators).length;
        this.stressLevel = stressScore;

        if (stressScore > 0.7) {
            return {
                stressLevel: 'high',
                score: stressScore,
                recommendation: 'Consider taking a 30-second mindfulness break',
                shouldSuggestBreak: true
            };
        } else if (stressScore > 0.4) {
            return {
                stressLevel: 'medium',
                score: stressScore,
                recommendation: 'Take deep breaths and stay calm'
            };
        }

        return {
            stressLevel: 'low',
            score: stressScore
        };
    }

    /**
     * Detect excessive movement (stress indicator)
     */
    detectExcessiveMovement() {
        if (this.mouseBuffer.length < 50) return false;
        
        const recentMovements = this.mouseBuffer.slice(-50);
        let rapidChanges = 0;

        for (let i = 1; i < recentMovements.length; i++) {
            const distance = Math.sqrt(
                Math.pow(recentMovements[i].x - recentMovements[i - 1].x, 2) +
                Math.pow(recentMovements[i].y - recentMovements[i - 1].y, 2)
            );
            
            if (distance > 100) { // Large movement
                rapidChanges++;
            }
        }

        return rapidChanges > 15; // More than 15 rapid movements in 50 samples
    }

    /**
     * Generate QR code data for smartphone pairing
     */
    generatePairingQR(attemptId, sessionToken) {
        const pairingData = {
            attemptId,
            sessionToken,
            timestamp: Date.now(),
            type: 'secondary_camera'
        };

        return JSON.stringify(pairingData);
    }

    /**
     * Detect hidden electronic devices using device orientation/magnetometer
     * (This is a simulation - actual implementation would require device API access)
     */
    async detectHiddenDevices() {
        if ('DeviceOrientationEvent' in window) {
            return new Promise((resolve) => {
                let readings = [];
                
                const handler = (event) => {
                    readings.push({
                        alpha: event.alpha,
                        beta: event.beta,
                        gamma: event.gamma,
                        timestamp: Date.now()
                    });

                    if (readings.length >= 10) {
                        window.removeEventListener('deviceorientation', handler);
                        
                        // Analyze for anomalies (nearby magnetic fields)
                        const anomaly = this.analyzeMagneticAnomalies(readings);
                        resolve(anomaly);
                    }
                };

                window.addEventListener('deviceorientation', handler);
                
                // Timeout after 3 seconds
                setTimeout(() => {
                    window.removeEventListener('deviceorientation', handler);
                    resolve(null);
                }, 3000);
            });
        }

        return null;
    }

    /**
     * Analyze magnetometer readings for hidden devices
     */
    analyzeMagneticAnomalies(readings) {
        // Calculate variance in readings
        const alphaVariance = this.calculateStdDev(readings.map(r => r.alpha));
        const betaVariance = this.calculateStdDev(readings.map(r => r.beta));
        
        // High variance could indicate nearby electronic device
        if (alphaVariance > 50 || betaVariance > 50) {
            return {
                detected: true,
                confidence: 0.65,
                message: 'Possible electronic device detected nearby'
            };
        }

        return null;
    }

    /**
     * Reset behavioral baselines (for new session)
     */
    reset() {
        this.keystrokeBuffer = [];
        this.mouseBuffer = [];
        this.baselineTyping = null;
        this.baselineMouse = null;
        this.stressLevel = 0;
    }
}

export default new AdvancedProctoringService();
