import api from './api';

const blockchainService = {
    // Get blockchain summary
    getSummary: async () => {
        const response = await api.get('/blockchain/summary');
        return response.data.summary;
    },

    // Verify blockchain integrity
    verifyIntegrity: async (limit = 1000) => {
        const response = await api.get(`/blockchain/verify?limit=${limit}`);
        return response.data.verification;
    },

    // Get entity audit trail
    getEntityAuditTrail: async (entityType, entityId) => {
        const response = await api.get(`/blockchain/entity/${entityType}/${entityId}`);
        return response.data.audit_trail;
    },

    // Get events by type
    getEventsByType: async (eventType, limit = 100) => {
        const response = await api.get(`/blockchain/events/${eventType}?limit=${limit}`);
        return response.data;
    },

    // Get attempt audit trail
    getAttemptAuditTrail: async (attemptId) => {
        const response = await api.get(`/blockchain/attempt/${attemptId}`);
        return response.data.audit_trail;
    },

    // Initialize genesis block
    initializeGenesis: async () => {
        const response = await api.post('/blockchain/initialize');
        return response.data;
    },

    // Get event types
    getEventTypes: async () => {
        const response = await api.get('/blockchain/event-types');
        return response.data.event_types;
    }
};

export default blockchainService;
