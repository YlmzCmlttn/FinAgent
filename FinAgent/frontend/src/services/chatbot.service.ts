import axios from 'axios';

interface ChatRequest {
    message: string;
    trace_id?: string;
}

interface ChatResponse {
    response: string;
    trace_id: string;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:4000';

export const chatbotService = {
    async sendMessage(message: string): Promise<ChatResponse> {
        try {
            const response = await axios.post<ChatResponse>(`${API_URL}/chat`, {
                message,
            });
            return response.data;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    },

    async checkHealth(): Promise<{ status: string }> {
        try {
            const response = await axios.get(`${API_URL}/health`);
            return response.data;
        } catch (error) {
            console.error('Error checking health:', error);
            throw error;
        }
    }
}; 