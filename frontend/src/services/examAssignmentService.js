/**
 * Exam Assignment Service
 * =======================
 * API calls for exam assignment operations
 */

import api from './api';

const examAssignmentService = {
    /**
     * Assign exam to students (admin-only)
     * @param {string} examId - Exam UUID
     * @param {Array<string>} studentIds - Array of student UUIDs
     * @returns {Promise} Assignment results
     */
    assignExamToStudents: async (examId, studentIds) => {
        try {
            const response = await api.post(`/exams/${examId}/assign/`, {
                student_ids: studentIds
            });
            return response.data;
        } catch (error) {
            throw error.response?.data?.error || 'Failed to assign exam';
        }
    },

    /**
     * Get all assignments for an exam (admin-only)
     * @param {string} examId - Exam UUID
     * @returns {Promise} List of assignments
     */
    getExamAssignments: async (examId) => {
        try {
            const response = await api.get(`/exams/${examId}/assignments`);
            return response.data;
        } catch (error) {
            throw error.response?.data?.error || 'Failed to fetch assignments';
        }
    },

    /**
     * Remove assignment (admin-only)
     * @param {string} examId - Exam UUID
     * @param {string} studentId - Student UUID
     * @returns {Promise} Success message
     */
    removeAssignment: async (examId, studentId) => {
        try {
            const response = await api.delete(`/exams/${examId}/assign/${studentId}`);
            return response.data;
        } catch (error) {
            throw error.response?.data?.error || 'Failed to remove assignment';
        }
    },

    /**
     * Get student's assigned exams (admin-only)
     * @param {string} studentId - Student UUID
     * @returns {Promise} List of assigned exams
     */
    getStudentAssignedExams: async (studentId) => {
        try {
            const response = await api.get(`/exams/students/${studentId}/assigned-exams`);
            return response.data;
        } catch (error) {
            throw error.response?.data?.error || 'Failed to fetch student assignments';
        }
    },

    /**
     * Get available exams for the logged-in student
     * This is handled by the exam service's getAvailableExams method
     * @returns {Promise} List of available assigned exams
     */
    getAvailableExamsForStudent: async (studentId) => {
        try {
            const response = await api.get(`/exams/available`);
            return response.data.exams;
        } catch (error) {
            throw error.response?.data?.error || 'Failed to fetch available exams';
        }
    }
};

export default examAssignmentService;
