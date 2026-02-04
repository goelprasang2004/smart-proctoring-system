import api from './api';

const resultsService = {
    // Get my results
    getMyResults: async () => {
        const response = await api.get('/results/my-results');
        return response.data.results;
    },

    // Get detailed result with answer breakdown
    getDetailedResult: async (attemptId) => {
        const response = await api.get(`/results/${attemptId}/detailed`);
        return response.data.result;
    }
};

export default resultsService;
