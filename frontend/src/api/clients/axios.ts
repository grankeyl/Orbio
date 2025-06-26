import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_APP_API_URL,
  timeout: 100000,
  headers: {
    "Content-Type": "application/json"
  }
});

export const nftsApi = axios.create({
  baseURL: import.meta.env.VITE_APP_API_NFTS_URL,
  timeout: 100000
});