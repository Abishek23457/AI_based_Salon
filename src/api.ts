/**
 * Centralized API configuration for BookSmart AI.
 * Switch between LOCAL (Offline) and NGROK (Online) testing here.
 */

// Check if VITE_API_URL environment variable is provided, otherwise default to local
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

console.log('Using API URL:', API_URL);
