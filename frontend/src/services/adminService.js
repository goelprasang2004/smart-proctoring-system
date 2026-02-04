/**
 * Admin Service
 * =============
 * API calls for admin-specific operations
 */

import api from './api';

const adminService = {
    /**
     * Create a new student account (admin-only)
     * @param {Object} studentData - Student account data
     * @param {string} studentData.email - Student email
     * @param {string} studentData.password - Student password
     * @param {string} studentData.full_name - Student full name
     * @returns {Promise} Created student data
     */
    createStudent: async (studentData) => {
        try {
            const response = await api.post('/admin/students', studentData);
            return response.data;
        } catch (error) {
            throw error.response?.data?.error || 'Failed to create student account';
        }
    },

    /**
     * Get all students (admin-only)
     * @returns {Promise} List of all students
     */
    getAllStudents: async () => {
        try {
            const response = await api.get('/admin/students');
            return response.data;
        } catch (error) {
            throw error.response?.data?.error || 'Failed to fetch students';
        }
    }
};

export default adminService;
