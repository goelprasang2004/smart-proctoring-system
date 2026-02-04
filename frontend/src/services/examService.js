import api from './api';

const examService = {
    // Student: Get available exams
    getAvailableExams: async () => {
        const response = await api.get('/exams/available');
        return response.data.exams;
    },

    // Student: Get exam details (without questions)
    getExamDetails: async (examId) => {
        const response = await api.get(`/exams/${examId}/details`);
        return response.data.exam;
    },

    // Admin: Get all exams
    getAllExams: async (filters = {}) => {
        const params = new URLSearchParams(filters).toString();
        const url = params ? `/exams/?${params}` : '/exams/';
        const response = await api.get(url);
        return response.data.exams || response.data;
    },

    // Admin: Get exam by ID (with config)
    getExamById: async (examId) => {
        const response = await api.get(`/exams/${examId}`);
        return response.data.exam;
    },

    // Admin: Create exam
    createExam: async (examData) => {
        const response = await api.post('/exams/', examData);
        return response.data.exam;
    },

    // Admin: Update exam
    updateExam: async (examId, examData) => {
        const response = await api.put(`/exams/${examId}/`, examData);
        return response.data.exam;
    },

    // Admin: Delete exam
    deleteExam: async (examId) => {
        const response = await api.delete(`/exams/${examId}/`);
        return response.data;
    },

    // Admin: Change exam status
    changeExamStatus: async (examId, status) => {
        const response = await api.patch(`/exams/${examId}/status/`, { status });
        return response.data.exam;
    },

    // Student: Start exam attempt
    startAttempt: async (examId, sessionData = {}) => {
        const response = await api.post('/attempts/start/', {
            exam_id: examId,
            session_data: sessionData
        });
        return response.data.attempt;
    },

    // Student: Submit exam attempt
    submitAttempt: async (attemptId, answers) => {
        const response = await api.post(`/attempts/${attemptId}/submit/`, { answers });
        return response.data.submission;
    },

    // Student: Terminate attempt (auto-called on violation)
    terminateAttempt: async (attemptId, data) => {
        const response = await api.post(`/attempts/${attemptId}/terminate/`, data);
        return response.data;
    }
};

export default examService;
