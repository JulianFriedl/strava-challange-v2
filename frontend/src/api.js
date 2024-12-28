export const API_BASE_URL = "http://localhost:8080/api"

export const apiRequest = async (endpoint, options = {}) => {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            credentials: 'include', // Include cookies for session management
            headers: {
                'Content-Type': 'application/json',
                ...(options.headers || {}),
            },
            ...options,
        });

        if (response.status === 401) {
            window.location.href = '/';
            return null;
        }

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        throw error;
    }
};
