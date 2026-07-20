import { apiClient } from './apiClient';

export const loanService = {
  list: () => apiClient.get('/loans'),
  borrow: (bookId, memberId = null) => apiClient.post('/books/loan', {
    book_id: bookId,
    member_id: memberId
  }),
  returnBook: (loanId) => apiClient.post(`/loans/${loanId}/return`)
};
