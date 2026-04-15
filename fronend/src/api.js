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

api.interceptors.response.use(
    (response) => response,
    (error) => {
        // If token is missing/expired, avoid endless polling errors: logout and redirect.
        const status = error?.response?.status;
        if (status === 401) {
            try {
                localStorage.removeItem('access_token');
                localStorage.removeItem('username');
                localStorage.removeItem('last_room_id');
            } catch (_) {
                // ignore storage errors
            }
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default api;
