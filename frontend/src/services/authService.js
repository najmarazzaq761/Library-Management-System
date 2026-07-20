import { apiClient } from './apiClient';

export const authService = {
  login: (email, password) => apiClient.postUrlEncoded('/login', {
    username: email,
    password: password
  }),
  signup: (name, email, password, role = 'member') => apiClient.post('/signup', {
    name,
    email,
    password,
    role
  }),
  listMembers: () => apiClient.get('/members')
};
