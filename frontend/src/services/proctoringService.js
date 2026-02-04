import api from './api';

const proctoringService = {
    // Student: Log proctoring event
    logEvent: async (attemptId, eventType, description, metadata = {}) => {
        const response = await api.post('/proctoring/event', {
            attempt_id: attemptId,
            event_type: eventType,
            description,
            metadata
        });
        return response.data;
    },

    // WebSocket Connection
    connectToProctoring: (attemptId, onMessage, onError) => {
        const wsUrl = `ws://localhost:8000/api/v1/proctoring/ws/${attemptId}`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Connected to Proctoring WebSocket');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            onMessage(data);
        };

        ws.onerror = (error) => {
            console.error('WebSocket Error:', error);
            if (onError) onError(error);
        };

        ws.onclose = () => {
            console.log('Proctoring WebSocket Disconnected');
        };

        return ws;
    },

    // Send frame to backend
    sendFrame: (ws, imageData) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ image: imageData }));
        }
    },

    // Student: Get my attempt proctoring data
    getMyAttemptData: async (attemptId) => {
        const response = await api.get(`/proctoring/my-attempt/${attemptId}`);
        return response.data.summary;
    },

    // Admin: Get complete attempt proctoring data
    getAttemptProctoring: async (attemptId) => {
        const response = await api.get(`/proctoring/attempt/${attemptId}`);
        return response.data;
    },

    // Admin: Get attempt events
    getAttemptEvents: async (attemptId, eventType = null) => {
        const params = eventType ? `?event_type=${eventType}` : '';
        const response = await api.get(`/proctoring/attempt/${attemptId}/events${params}`);
        return response.data.events;
    },

    // Admin: Get attempt AI analysis
    getAttemptAIAnalysis: async (attemptId, analysisType = null) => {
        const params = analysisType ? `?analysis_type=${analysisType}` : '';
        const response = await api.get(`/proctoring/attempt/${attemptId}/ai-analysis${params}`);
        return response.data.analyses;
    },

    // Admin: Get suspicious attempts
    getSuspiciousAttempts: async (confidenceThreshold = 0.7, minEventCount = 5) => {
        const response = await api.get('/proctoring/suspicious', {
            params: {
                confidence_threshold: confidenceThreshold,
                min_event_count: minEventCount
            }
        });
        return response.data.suspicious_attempts;
    }
};

export default proctoringService;
