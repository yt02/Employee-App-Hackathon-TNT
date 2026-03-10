import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// IMPORTANT: For production deployment, use the Azure backend URL
// For local development, replace with your computer's local IP (e.g., http://192.168.x.x:8000/api)
const API_BASE_URL = 'https://tnt-bc5-chatbot-api.azurewebsites.net/api';
//const API_BASE_URL = 'http://192.168.100.237:8000/api'; // Local development only

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to normalize success values (handles both boolean and string)
const normalizeSuccess = (value) => {
  return value === true || value === 'true' || value === 1;
};

// ============================================
// AUTHENTICATION
// ============================================

export const login = async (username, password) => {
  try {
    const response = await api.post('/auth/login', { username, password });

    if (response.data && response.data.success) {
      const userData = response.data.data;
      console.log('Login successful, saving user:', userData.user_id);
      await AsyncStorage.setItem('user', JSON.stringify(userData));
      return { success: true, data: userData };
    }

    return {
      success: false,
      message: response.data?.message || 'Invalid username or password'
    };
  } catch (error) {
    console.error('Login API error:', error);
    const message = error.response?.data?.detail || error.response?.data?.message || 'Connection error';
    return { success: false, message };
  }
};

export const logout = async () => {
  await AsyncStorage.removeItem('user');
};

export const getCurrentUser = async () => {
  const userStr = await AsyncStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

// ============================================
// LEAVE MANAGEMENT
// ============================================

export const getLeaveBalance = async (userId) => {
  const response = await api.get(`/leave/balance/${userId}`);
  return response.data;
};

export const applyLeave = async (userId, leaveData) => {
  const response = await api.post(`/leave/apply/${userId}`, leaveData);
  return response.data;
};

export const getLeaveHistory = async (userId) => {
  const response = await api.get(`/leave/history/${userId}`);
  return response.data;
};

// ============================================
// MEETING ROOMS
// ============================================

export const getRooms = async () => {
  const response = await api.get('/rooms/list');
  return response.data;
};

export const bookRoom = async (userId, bookingData) => {
  const response = await api.post(`/rooms/book/${userId}`, bookingData);
  return response.data;
};

export const getUserBookings = async (userId) => {
  const response = await api.get(`/rooms/bookings/${userId}`);
  return response.data;
};

export const cancelBooking = async (bookingId, userId) => {
  const response = await api.delete(`/rooms/cancel/${bookingId}/${userId}`);
  return response.data;
};

// ============================================
// CALENDAR
// ============================================

export const getEvents = async (userId) => {
  const response = await api.get(`/calendar/events/${userId}`);
  return response.data;
};

export const createEvent = async (userId, eventData) => {
  const response = await api.post(`/calendar/events/${userId}`, eventData);
  return response.data;
};

// ============================================
// TICKETING
// ============================================

export const getTickets = async (userId) => {
  const response = await api.get(`/tickets/${userId}`);
  return response.data;
};

export const createTicket = async (userId, ticketData) => {
  const response = await api.post(`/tickets/create/${userId}`, ticketData);
  return response.data;
};

// ============================================
// ATTENDANCE
// ============================================

export const clockIn = async (userId) => {
  return { success: true, message: "Clocked in" };
};

export const clockOut = async (userId) => {
  return { success: true, message: "Clocked out" };
};

export const getAttendance = async (userId) => {
  return { success: true, data: [] };
};

export const getAttendanceSummary = async (userId, month) => {
  return { success: true, data: { present: 20, absent: 0, late: 1 } };
};

// ============================================
// VISITOR
// ============================================

export const getVisitors = async (hostId) => {
  const response = await api.get(`/visitors?host_employee_id=${hostId}`);
  return response.data;
};

export const registerVisitor = async (visitorData) => {
  const response = await api.post('/visitors/register', visitorData);
  return response.data;
};

export const checkInVisitor = async (visitorId) => {
  const response = await api.post(`/visitors/check-in/${visitorId}`);
  return response.data;
};

export const checkOutVisitor = async (visitorId) => {
  const response = await api.post(`/visitors/check-out/${visitorId}`);
  return response.data;
};

// ============================================
// SHUTTLE
// ============================================

export const getShuttleRoutes = async () => {
  const response = await api.get('/shuttle/routes');
  return response.data;
};

export const bookShuttle = async (userId, bookingData) => {
  const response = await api.post(`/shuttle/book/${userId}`, bookingData);
  return response.data;
};

export const getShuttleBookings = async (userId) => {
  const response = await api.get(`/shuttle/bookings/${userId}`);
  return response.data;
};

export const cancelShuttleBooking = async (bookingId, userId) => {
  const response = await api.post(`/shuttle/cancel/${bookingId}/${userId}`);
  return response.data;
};

// ============================================
// TRAINING
// ============================================

export const getTrainingCourses = async () => {
  const response = await api.get('/training/courses');
  return response.data;
};

export const enrollCourse = async (userId, enrollmentData) => {
  const response = await api.post(`/training/enroll/${userId}`, enrollmentData);
  return response.data;
};

export const getEnrollments = async (userId) => {
  const response = await api.get(`/training/enrollments/${userId}`);
  return response.data;
};

export const completeCourse = async (enrollmentId, userId) => {
  const response = await api.post(`/training/complete/${enrollmentId}/${userId}`);
  return response.data;
};

// ============================================
// WELLNESS
// ============================================

export const getWellnessActivities = async () => {
  const response = await api.get('/wellness/activities');
  return response.data;
};

export const joinWellnessActivity = async (userId, activityData) => {
  const response = await api.post(`/wellness/join/${userId}`, activityData);
  return response.data;
};

export const logWellness = async (userId, logData) => {
  const response = await api.post(`/wellness/log/${userId}`, logData);
  return response.data;
};

export const getWellnessStats = async (userId) => {
  const response = await api.get(`/wellness/stats/${userId}`);
  return response.data;
};

// ============================================
// AI CHATBOT
// ============================================

import { Platform } from 'react-native';

const getChatbotBaseUrl = () => {
  // Production: Use Azure backend
  return 'https://tnt-bc5-chatbot-api.azurewebsites.net';

  // Local development: Use your computer's IP
  // return 'http://192.168.100.237:8000';
};

const chatApi = axios.create({
  baseURL: getChatbotBaseUrl(),
  timeout: 60000, // Chatbot might take a bit longer to process
  headers: {
    'Content-Type': 'application/json',
  },
});

// The basic static send function
export const sendChatMessageStatic = async (message, userId) => {
  try {
    const response = await chatApi.post('/chat', { message, user_id: userId });
    return response.data;
  } catch (error) {
    console.error('Chat API Error:', error);
    throw error;
  }
};

import EventSource from 'react-native-sse';

// Streaming text using react-native-sse (React Native fetch doesn't support streams natively)
export const sendChatMessageStream = (message, userId, onEvent) => {
  return new Promise((resolve, reject) => {
    try {
      const url = `${getChatbotBaseUrl()}/chat/stream`;

      const es = new EventSource(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, user_id: userId }),
      });

      es.addEventListener('open', () => {
        // Stream started
      });

      es.addEventListener('message', (event) => {
        if (event.data) {
          try {
            const parsedEvent = JSON.parse(event.data);
            if (onEvent) onEvent(parsedEvent);

            // Check if backend signaled completion explicitly to close connection
            if (parsedEvent.type === 'done') {
              es.close();
              resolve();
            }
          } catch (e) {
            console.error('Error parsing SSE json:', e, event.data);
          }
        }
      });

      es.addEventListener('error', (event) => {
        if (event.type === 'error' && event.message === 'EventSource closed') {
          // Normal closure by server
          es.close();
          resolve();
        } else {
          console.error('SSE Error Event:', event);
          es.close();
          reject(new Error(event.message || 'Stream error'));
        }
      });

    } catch (error) {
      console.error('Chat Stream API Error:', error);
      reject(error);
    }
  });
};

export const confirmChatAction = async (confirmPayload) => {
  try {
    const response = await chatApi.post('/chat/confirm', confirmPayload);
    return response.data;
  } catch (error) {
    console.error('Error confirming chat action:', error);
    throw error;
  }
};

