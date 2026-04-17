/**
 * Centralized API configuration for BookSmart AI.
 * Switch between LOCAL (Offline) and NGROK (Online) testing here.
 */

// LOCAL TESTING (Offline)
const LOCAL_API = 'http://localhost:8000';

// Current active API
export const API_URL = LOCAL_API;

console.log('Using API URL:', API_URL);
