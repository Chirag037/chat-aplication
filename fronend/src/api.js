import axios from 'axios';

const api = axios.create({
    baseURL: window.location.origin,
});

api.interceptors.request.use((config) => {
    // List of endpoints that don't require authentication
    const publicEndpoints = ['/api/login/', '/api/register/', '/api/health/'];

    const isPublic = publicEndpoints.some(endpoint => config.url.endsWith(endpoint));
    const token = localStorage.getItem('access_token');

    // Only attach the token if it exists and the endpoint is not public
    if (token && !isPublic) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }

    return config;
}, (error) => {
    return Promise.reject(error);
});

export default api;
