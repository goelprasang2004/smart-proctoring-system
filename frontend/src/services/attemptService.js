import api from './api';

const attemptService = {
    // Start new exam attempt
    startAttempt: async (examId, sessionData) => {
        const response = await api.post('/attempts/start', {
            exam_id: examId,
            session_data: sessionData
        });
        return response.data.attempt;
    },

    // Get my attempts history
    getMyAttempts: async () => {
        const response = await api.get('/attempts/my-attempts');
        return response.data.attempts;
    },

    // Get attempt details
    getAttemptDetails: async (attemptId) => {
        const response = await api.get(`/attempts/${attemptId}`);
        return response.data.attempt;
    },

    // Submit exam attempt
    submitAttempt: async (attemptId, answers) => {
        const response = await api.post(`/attempts/${attemptId}/submit`, {
            answers
        });
        return response.data.submission;
    }
};

export default attemptService;
