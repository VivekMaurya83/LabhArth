/**
 * LabhArth AI — API Service
 *
 * Centralized HTTP client for backend API communication.
 * All API calls go through this service for consistent
 * error handling, auth headers, and base URL management.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

/**
 * Generic fetch wrapper with error handling.
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * Send a chat message to the AI assistant.
 */
export async function sendChatMessage(message, sessionId = null) {
  return apiRequest('/chat/', {
    method: 'POST',
    body: JSON.stringify({ message, session_id: sessionId }),
  });
}

/**
 * Search for government schemes.
 */
export async function searchSchemes(query, filters = {}) {
  const params = new URLSearchParams({ query, ...filters });
  return apiRequest(`/schemes/search?${params}`);
}

/**
 * Get full details of a specific scheme.
 */
export async function getSchemeDetails(schemeId) {
  return apiRequest(`/schemes/${schemeId}`);
}

/**
 * Check eligibility for a scheme.
 */
export async function checkEligibility(schemeId, profile) {
  return apiRequest('/eligibility/check', {
    method: 'POST',
    body: JSON.stringify({ scheme_id: schemeId, profile }),
  });
}

/**
 * Health check.
 */
export async function healthCheck() {
  return apiRequest('/health');
}

export default {
  sendChatMessage,
  searchSchemes,
  getSchemeDetails,
  checkEligibility,
  healthCheck,
};
