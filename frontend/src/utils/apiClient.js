/**
 * MedMatch API Client with Resilience Features
 * Handles rate limiting, retries, caching, and request batching
 * Designed for 1M+ users scale
 */

// ============== Configuration ==============
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

const CONFIG = {
  // Retry configuration
  maxRetries: 5,
  baseDelay: 1000, // 1 second
  maxDelay: 32000, // 32 seconds max
  jitterFactor: 0.3, // 30% jitter
  
  // Cache configuration
  cacheEnabled: true,
  defaultCacheTTL: 300000, // 5 minutes
  maxCacheSize: 500,
  
  // Batch configuration
  batchEnabled: true,
  batchDelay: 50, // ms to wait before sending batch
  maxBatchSize: 10,
  
  // Request timeout
  requestTimeout: 30000, // 30 seconds
};

// ============== Local Cache ==============
class LocalCache {
  constructor(maxSize = CONFIG.maxCacheSize) {
    this.cache = new Map();
    this.maxSize = maxSize;
    this.hits = 0;
    this.misses = 0;
  }

  generateKey(url, params = {}) {
    const paramStr = JSON.stringify(params, Object.keys(params).sort());
    return `${url}:${paramStr}`;
  }

  get(url, params = {}) {
    const key = this.generateKey(url, params);
    const entry = this.cache.get(key);
    
    if (!entry) {
      this.misses++;
      return null;
    }
    
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      this.misses++;
      return null;
    }
    
    this.hits++;
    return entry.data;
  }

  set(url, data, params = {}, ttl = CONFIG.defaultCacheTTL) {
    const key = this.generateKey(url, params);
    
    // Evict oldest if at capacity
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, {
      data,
      expiresAt: Date.now() + ttl,
      createdAt: Date.now()
    });
  }

  invalidate(urlPattern) {
    for (const key of this.cache.keys()) {
      if (key.includes(urlPattern)) {
        this.cache.delete(key);
      }
    }
  }

  clear() {
    this.cache.clear();
  }

  getStats() {
    const total = this.hits + this.misses;
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      hits: this.hits,
      misses: this.misses,
      hitRate: total > 0 ? ((this.hits / total) * 100).toFixed(1) + '%' : '0%'
    };
  }
}

// ============== Request Batcher ==============
class RequestBatcher {
  constructor() {
    this.pendingRequests = new Map();
    this.batchTimers = new Map();
  }

  async batch(endpoint, requests) {
    return new Promise((resolve, reject) => {
      const batchKey = endpoint;
      
      if (!this.pendingRequests.has(batchKey)) {
        this.pendingRequests.set(batchKey, []);
      }
      
      this.pendingRequests.get(batchKey).push({ requests, resolve, reject });
      
      // Set timer for batch execution
      if (!this.batchTimers.has(batchKey)) {
        this.batchTimers.set(batchKey, setTimeout(() => {
          this.executeBatch(batchKey);
        }, CONFIG.batchDelay));
      }
      
      // Execute immediately if batch is full
      if (this.pendingRequests.get(batchKey).length >= CONFIG.maxBatchSize) {
        clearTimeout(this.batchTimers.get(batchKey));
        this.batchTimers.delete(batchKey);
        this.executeBatch(batchKey);
      }
    });
  }

  async executeBatch(batchKey) {
    const pending = this.pendingRequests.get(batchKey) || [];
    this.pendingRequests.delete(batchKey);
    this.batchTimers.delete(batchKey);
    
    if (pending.length === 0) return;
    
    try {
      // Combine all requests into single batch request
      const batchPayload = pending.map(p => p.requests);
      
      const response = await fetch(`${API_BASE_URL}/api/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requests: batchPayload }),
        credentials: 'include'
      });
      
      const results = await response.json();
      
      // Resolve individual promises
      pending.forEach((p, idx) => {
        if (results.responses && results.responses[idx]) {
          p.resolve(results.responses[idx]);
        } else {
          p.reject(new Error('Batch response missing'));
        }
      });
    } catch (error) {
      // Reject all pending promises
      pending.forEach(p => p.reject(error));
    }
  }
}

// ============== Exponential Backoff with Jitter ==============
class RetryStrategy {
  static calculateDelay(attempt, retryAfterHeader = null) {
    // If server specifies Retry-After, respect it
    if (retryAfterHeader) {
      const retryAfter = parseInt(retryAfterHeader, 10);
      if (!isNaN(retryAfter)) {
        return retryAfter * 1000; // Convert to ms
      }
      // Handle HTTP-date format
      const retryDate = new Date(retryAfterHeader);
      if (!isNaN(retryDate.getTime())) {
        return Math.max(0, retryDate.getTime() - Date.now());
      }
    }
    
    // Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s
    const exponentialDelay = Math.min(
      CONFIG.baseDelay * Math.pow(2, attempt),
      CONFIG.maxDelay
    );
    
    // Add jitter to prevent thundering herd
    const jitter = exponentialDelay * CONFIG.jitterFactor * Math.random();
    
    return exponentialDelay + jitter;
  }

  static shouldRetry(status, attempt) {
    if (attempt >= CONFIG.maxRetries) return false;
    
    // Retry on rate limiting (429) and server errors (5xx)
    return status === 429 || status === 503 || (status >= 500 && status < 600);
  }
}

// ============== Resilient API Client ==============
class ResilientAPIClient {
  constructor() {
    this.cache = new LocalCache();
    this.batcher = new RequestBatcher();
    this.requestCount = 0;
    this.errorCount = 0;
    this.rateLimitCount = 0;
  }

  async request(url, options = {}) {
    const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;
    const method = options.method || 'GET';
    const cacheKey = options.cacheKey || url;
    const cacheTTL = options.cacheTTL || CONFIG.defaultCacheTTL;
    const skipCache = options.skipCache || false;
    
    // Check cache for GET requests
    if (method === 'GET' && CONFIG.cacheEnabled && !skipCache) {
      const cached = this.cache.get(cacheKey, options.params);
      if (cached) {
        return { data: cached, fromCache: true };
      }
    }
    
    let lastError = null;
    let attempt = 0;
    
    while (attempt <= CONFIG.maxRetries) {
      try {
        this.requestCount++;
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.requestTimeout);
        
        const response = await fetch(fullUrl, {
          ...options,
          signal: controller.signal,
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-Client-Version': '2.2.0',
            'X-Request-ID': this.generateRequestId(),
            ...this.getAuthHeaders(),
            ...options.headers
          }
        });
        
        clearTimeout(timeoutId);
        
        // Handle rate limiting
        if (response.status === 429) {
          this.rateLimitCount++;
          const retryAfter = response.headers.get('Retry-After');
          
          if (RetryStrategy.shouldRetry(429, attempt)) {
            const delay = RetryStrategy.calculateDelay(attempt, retryAfter);
            console.warn(`Rate limited. Retrying in ${delay}ms (attempt ${attempt + 1})`);
            await this.sleep(delay);
            attempt++;
            continue;
          }
        }
        
        // Handle server errors with retry
        if (response.status >= 500 && RetryStrategy.shouldRetry(response.status, attempt)) {
          const delay = RetryStrategy.calculateDelay(attempt);
          console.warn(`Server error ${response.status}. Retrying in ${delay}ms`);
          await this.sleep(delay);
          attempt++;
          continue;
        }
        
        // Parse response
        const data = await response.json();
        
        if (!response.ok) {
          throw new APIError(data.detail || data.message || 'Request failed', response.status, data);
        }
        
        // Cache successful GET responses
        if (method === 'GET' && CONFIG.cacheEnabled && !skipCache) {
          this.cache.set(cacheKey, data, options.params, cacheTTL);
        }
        
        return { data, fromCache: false, status: response.status };
        
      } catch (error) {
        this.errorCount++;
        lastError = error;
        
        if (error.name === 'AbortError') {
          throw new APIError('Request timeout', 408);
        }
        
        // Network errors - retry with backoff
        if (!error.status && attempt < CONFIG.maxRetries) {
          const delay = RetryStrategy.calculateDelay(attempt);
          console.warn(`Network error. Retrying in ${delay}ms`);
          await this.sleep(delay);
          attempt++;
          continue;
        }
        
        throw error;
      }
    }
    
    throw lastError || new APIError('Max retries exceeded', 503);
  }

  // Convenience methods
  async get(url, params = {}, options = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    return this.request(fullUrl, { ...options, method: 'GET', params });
  }

  async post(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async put(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async delete(url, options = {}) {
    return this.request(url, { ...options, method: 'DELETE' });
  }

  // Batch multiple requests
  async batchRequests(requests) {
    if (!CONFIG.batchEnabled) {
      // Fall back to individual requests
      return Promise.all(requests.map(r => this.request(r.url, r.options)));
    }
    
    return this.batcher.batch('/batch', requests);
  }

  // Cache management
  invalidateCache(pattern) {
    this.cache.invalidate(pattern);
  }

  clearCache() {
    this.cache.clear();
  }

  getCacheStats() {
    return this.cache.getStats();
  }

  // Client stats
  getStats() {
    return {
      totalRequests: this.requestCount,
      errors: this.errorCount,
      rateLimits: this.rateLimitCount,
      errorRate: this.requestCount > 0 
        ? ((this.errorCount / this.requestCount) * 100).toFixed(2) + '%' 
        : '0%',
      cache: this.cache.getStats()
    };
  }

  // Utilities
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  generateRequestId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    if (token) {
      return { 'Authorization': `Bearer ${token}` };
    }
    return {};
  }
}

// ============== API Error Class ==============
class APIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

// ============== Singleton Instance ==============
const apiClient = new ResilientAPIClient();

// ============== Pre-configured API Methods ==============
const api = {
  // Auth
  login: (credentials) => apiClient.post('/api/auth/login', credentials),
  logout: () => apiClient.post('/api/auth/logout'),
  getProfile: () => apiClient.get('/api/auth/me', {}, { cacheTTL: 60000 }),
  
  // Jobs - with caching
  searchJobs: (params) => apiClient.get('/api/jobs/search', params, { cacheTTL: 120000 }),
  getSavedJobs: () => apiClient.get('/api/saved-jobs', {}, { cacheTTL: 60000 }),
  saveJob: (job) => {
    apiClient.invalidateCache('/api/saved-jobs');
    return apiClient.post('/api/saved-jobs', job);
  },
  
  // Resume
  getResume: () => apiClient.get('/api/resume', {}, { cacheTTL: 300000 }),
  
  // Cached static data (long TTL)
  getLanguages: () => apiClient.get('/api/cached/languages', {}, { cacheTTL: 3600000 }),
  getIDLevels: () => apiClient.get('/api/cached/id-levels', {}, { cacheTTL: 3600000 }),
  getCompanies: () => apiClient.get('/api/companies/', {}, { cacheTTL: 300000 }),
  
  // Q&A Practice
  generateAnswer: (data) => apiClient.post('/api/qa-practice/generate-answer', data),
  getFavorites: () => apiClient.get('/api/qa-practice/favorites', {}, { cacheTTL: 60000 }),
  saveFavorite: (data) => {
    apiClient.invalidateCache('/api/qa-practice/favorites');
    return apiClient.post('/api/qa-practice/favorites/save', data);
  },
  
  // Notifications
  getNotificationPrefs: () => apiClient.get('/api/notifications/preferences', {}, { cacheTTL: 60000 }),
  getNotificationHistory: () => apiClient.get('/api/notifications/history'),
  
  // System
  getHealth: () => apiClient.get('/api/health', {}, { skipCache: true }),
  getSupervisorStatus: () => apiClient.get('/api/supervisor/status', {}, { skipCache: true }),
  
  // Direct access to client
  client: apiClient,
  
  // Get client stats
  getStats: () => apiClient.getStats()
};

export { api, apiClient, APIError, CONFIG };
export default api;
