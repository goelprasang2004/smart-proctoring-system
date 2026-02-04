import api from './api';

const authService = {
    // Login
    login: async (email, password) => {
        const params = new URLSearchParams();
        params.append('username', email); // FastAPI OAuth2 expects 'username'
        params.append('password', password);

        const response = await api.post('/login/access-token', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        console.log('Login Response:', response.data);
        const { access_token, token_type, user } = response.data;

        // Store tokens
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('token_type', token_type);
        localStorage.setItem('user', JSON.stringify(user));
        
        console.log('Token saved:', access_token);
        console.log('User saved:', user);

        return { user, access_token };
    },

    // Register
    register: async (userData) => {
        const response = await api.post('/auth/register', userData);
        return response.data;
    },

    // Get current user
    getCurrentUser: async () => {
        const response = await api.get('/auth/me');
        return response.data.user;
    },

    // Logout
    logout: async () => {
        try {
            await api.post('/auth/logout');
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Clear local storage
            localStorage.clear();
        }
    },

    // Check if user is authenticated
    isAuthenticated: () => {
        return !!localStorage.getItem('access_token');
    },

    // Get stored user
    getStoredUser: () => {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
};

export default authService;
