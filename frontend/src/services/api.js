import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor - Add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        console.log('API Request:', config.method.toUpperCase(), config.url);
        console.log('Token from localStorage:', token ? token.substring(0, 20) + '...' : 'NO TOKEN');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log('Authorization header set:', config.headers.Authorization.substring(0, 30) + '...');
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor - Handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // If 401 and haven't retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            console.error('401 Unauthorized Error:');
            console.error('Request URL:', originalRequest.url);
            console.error('Request headers:', originalRequest.headers);
            console.error('Response:', error.response?.data);
            
            originalRequest._retry = true;

            // Check if we have a token at all
            const token = localStorage.getItem('access_token');
            if (!token) {
                // No token, redirect to login
                console.error('No token found in localStorage');
                localStorage.clear();
                window.location.href = '/login';
                return Promise.reject(error);
            }

            console.error('Token exists:', token.substring(0, 20) + '...');
            
            // Token exists but failed - don't automatically logout
            // Just let the error propagate so the UI can handle it
            console.error('Authentication failed. Please try logging in again.');
            
            // Only clear and redirect if this is a login endpoint error
            if (originalRequest.url?.includes('/login')) {
                return Promise.reject(error);
            }

            // For other 401s, suggest re-login but don't force it immediately
            return Promise.reject(error);
        }

        return Promise.reject(error);
    }
);

export default api;
