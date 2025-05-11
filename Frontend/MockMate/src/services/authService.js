import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const authService = {
  async login(data) {
    try {
      const response = await axios.post(`${API_URL}/login/`, data, {
        withCredentials: true
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data;
      }
      throw error;
    }
  },

  async register(data) {
    try {
      const response = await axios.post(`${API_URL}/user/`, data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data;
      }
      throw error;
    }
  },

  async logout() {
    try {
      await axios.post(`${API_URL}/logout/`, {}, {
        withCredentials: true
      });
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw error.response.data;
      }
      throw error;
    }
  }
};

export default authService; 