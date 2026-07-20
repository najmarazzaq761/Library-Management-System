import { apiClient } from './apiClient';

export const notificationService = {
  list: () => apiClient.get('/notifications'),
  read: (notifId) => apiClient.post(`/notifications/${notifId}/read`),
  triggerOverdueJob: () => apiClient.post('/loans/overdue/notify')
};
