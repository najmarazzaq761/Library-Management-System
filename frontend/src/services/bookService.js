import { apiClient } from './apiClient';

export const bookService = {
  list: (skip = 0, limit = 100) => apiClient.get(`/books?skip=${skip}&limit=${limit}`),
  search: (query) => apiClient.get(`/books/search?title=${encodeURIComponent(query)}&author=${encodeURIComponent(query)}`),
  add: (title, author, isbn, availableCopies = 1) => apiClient.post('/books', {
    title,
    author,
    isbn,
    available_copies: availableCopies
  })
};
