/**
 * LabhArth AI — API Service
 *
 * Centralized HTTP client for backend API communication.
 * All API calls go through this service for consistent
 * error handling, base URL management, and request routing.
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
      let errorMessage = `API error: ${response.status}`;
      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
        } else if (typeof errorData.detail === 'object') {
          errorMessage = JSON.stringify(errorData.detail);
        }
      }
      throw new Error(errorMessage);
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
  return apiRequest('/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      session_id: sessionId
    }),
  });
}

/**
 * Search for government schemes via semantic search.
 */
export async function searchSchemes(query, filters = {}, limit = 10) {
  return apiRequest('/search', {
    method: 'POST',
    body: JSON.stringify({
      query: query || '',
      category: filters.category || null,
      state: filters.state || null,
      limit: parseInt(limit, 10) || 10
    })
  });
}

/**
 * Get full details of a specific scheme.
 */
export async function getSchemeDetails(schemeId) {
  return apiRequest(`/schemes/${schemeId}`);
}

/**
 * Check eligibility for a specific scheme.
 */
export async function checkEligibility(schemeId, profile) {
  // Normalize age and income_annual to numeric values
  const normalizedProfile = {
    ...profile,
    age: profile.age ? parseInt(profile.age, 10) : null,
    income_annual: profile.income_annual ? parseFloat(profile.income_annual) : null
  };

  return apiRequest('/eligibility/check', {
    method: 'POST',
    body: JSON.stringify({
      scheme_id: schemeId,
      profile: normalizedProfile
    }),
  });
}

/**
 * Check eligibility across multiple candidate schemes (bulk).
 */
export async function evaluateBulkEligibility(profile) {
  // Normalize age and income_annual to numeric values
  const normalizedProfile = {
    ...profile,
    age: profile.age ? parseInt(profile.age, 10) : null,
    income_annual: profile.income_annual ? parseFloat(profile.income_annual) : null
  };

  return apiRequest('/eligibility', {
    method: 'POST',
    body: JSON.stringify(normalizedProfile),
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
  evaluateBulkEligibility,
  healthCheck,
};
