/**
 * Centralized API configuration for BookSmart AI.
 * Switch between LOCAL (Offline) and NETWORK (Local LAN) testing here.
 */

// LOCAL TESTING (Offline)
const LOCAL_API = 'http://localhost:8000';

// NETWORK TESTING (Local LAN)
const NETWORK_API = 'http://192.168.0.123:8000';

// Current active API
export const API_URL = NETWORK_API;

console.log('Using API URL:', API_URL);
