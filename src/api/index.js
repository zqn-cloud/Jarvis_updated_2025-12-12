import axios from 'axios';

// Create an axios instance
const apiClient = axios.create({
  baseURL: 'http://localhost:3000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

export default {
  getEvents() {
    return apiClient.get('/events');
  },
  createEvent(event) {
    return apiClient.post('/events', event);
  },
  getCalendarTypes() {
    return apiClient.get('/calendar-types');
  },
  createCalendarType(type) {
    return apiClient.post('/calendar-types', type);
  },
  getReminders() {
    return apiClient.get('/reminders');
  }
};

