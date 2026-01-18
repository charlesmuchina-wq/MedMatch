import { openDB } from 'idb';
import React from 'react';

// IndexedDB Configuration
const DB_NAME = 'medmatch-offline';
const DB_VERSION = 1;

// Store names
const STORES = {
  JOBS: 'cached_jobs',
  RESUME: 'cached_resume',
  USER: 'cached_user',
  MESSAGES: 'cached_messages',
  SETTINGS: 'cached_settings',
  PENDING_ACTIONS: 'pending_actions',
  SYNC_META: 'sync_metadata'
};

// Initialize IndexedDB
const initDB = async () => {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      // Cached Jobs Store
      if (!db.objectStoreNames.contains(STORES.JOBS)) {
        const jobsStore = db.createObjectStore(STORES.JOBS, { keyPath: 'id' });
        jobsStore.createIndex('savedAt', 'savedAt');
        jobsStore.createIndex('source', 'source');
      }

      // Cached Resume Store
      if (!db.objectStoreNames.contains(STORES.RESUME)) {
        db.createObjectStore(STORES.RESUME, { keyPath: 'id' });
      }

      // Cached User Store
      if (!db.objectStoreNames.contains(STORES.USER)) {
        db.createObjectStore(STORES.USER, { keyPath: 'id' });
      }

      // Cached Messages Store
      if (!db.objectStoreNames.contains(STORES.MESSAGES)) {
        const messagesStore = db.createObjectStore(STORES.MESSAGES, { keyPath: 'id' });
        messagesStore.createIndex('conversationId', 'conversationId');
      }

      // Settings Store
      if (!db.objectStoreNames.contains(STORES.SETTINGS)) {
        db.createObjectStore(STORES.SETTINGS, { keyPath: 'key' });
      }

      // Pending Actions Store (for offline sync)
      if (!db.objectStoreNames.contains(STORES.PENDING_ACTIONS)) {
        const actionsStore = db.createObjectStore(STORES.PENDING_ACTIONS, { 
          keyPath: 'id', 
          autoIncrement: true 
        });
        actionsStore.createIndex('createdAt', 'createdAt');
        actionsStore.createIndex('type', 'type');
      }

      // Sync Metadata Store
      if (!db.objectStoreNames.contains(STORES.SYNC_META)) {
        db.createObjectStore(STORES.SYNC_META, { keyPath: 'key' });
      }
    }
  });
};

// ============== Offline Storage Manager ==============

class OfflineStorageManager {
  constructor() {
    this.db = null;
    this.isOnline = navigator.onLine;
    this.syncInProgress = false;
    this.listeners = new Set();

    // Listen for online/offline events
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());
  }

  async init() {
    if (!this.db) {
      this.db = await initDB();
    }
    return this.db;
  }

  // ============== Event Handlers ==============

  handleOnline() {
    this.isOnline = true;
    this.notifyListeners({ type: 'online' });
    this.syncPendingActions();
  }

  handleOffline() {
    this.isOnline = false;
    this.notifyListeners({ type: 'offline' });
  }

  addListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notifyListeners(event) {
    this.listeners.forEach(cb => cb(event));
  }

  // ============== Jobs Cache ==============

  async cacheJobs(jobs) {
    const db = await this.init();
    const tx = db.transaction(STORES.JOBS, 'readwrite');
    const store = tx.objectStore(STORES.JOBS);

    for (const job of jobs) {
      await store.put({
        ...job,
        savedAt: new Date().toISOString(),
        offlineCached: true
      });
    }

    await tx.done;
    await this.updateSyncMeta('jobs', { lastSync: new Date().toISOString(), count: jobs.length });
  }

  async getCachedJobs(options = {}) {
    const db = await this.init();
    const tx = db.transaction(STORES.JOBS, 'readonly');
    const store = tx.objectStore(STORES.JOBS);

    let jobs = await store.getAll();

    // Apply filters
    if (options.source) {
      jobs = jobs.filter(j => j.source === options.source);
    }

    // Sort by savedAt descending
    jobs.sort((a, b) => new Date(b.savedAt) - new Date(a.savedAt));

    // Apply limit
    if (options.limit) {
      jobs = jobs.slice(0, options.limit);
    }

    return jobs;
  }

  async clearJobsCache() {
    const db = await this.init();
    await db.clear(STORES.JOBS);
  }

  // ============== Resume Cache ==============

  async cacheResume(resume) {
    const db = await this.init();
    await db.put(STORES.RESUME, {
      id: 'current_resume',
      ...resume,
      cachedAt: new Date().toISOString()
    });
  }

  async getCachedResume() {
    const db = await this.init();
    return db.get(STORES.RESUME, 'current_resume');
  }

  // ============== User Cache ==============

  async cacheUser(user) {
    const db = await this.init();
    await db.put(STORES.USER, {
      id: 'current_user',
      ...user,
      cachedAt: new Date().toISOString()
    });
  }

  async getCachedUser() {
    const db = await this.init();
    return db.get(STORES.USER, 'current_user');
  }

  // ============== Messages Cache ==============

  async cacheMessages(conversationId, messages) {
    const db = await this.init();
    const tx = db.transaction(STORES.MESSAGES, 'readwrite');
    const store = tx.objectStore(STORES.MESSAGES);

    for (const msg of messages) {
      await store.put({
        ...msg,
        conversationId,
        cachedAt: new Date().toISOString()
      });
    }

    await tx.done;
  }

  async getCachedMessages(conversationId) {
    const db = await this.init();
    const tx = db.transaction(STORES.MESSAGES, 'readonly');
    const index = tx.objectStore(STORES.MESSAGES).index('conversationId');
    return index.getAll(conversationId);
  }

  // ============== Pending Actions (Offline Queue) ==============

  async queueAction(action) {
    const db = await this.init();
    await db.add(STORES.PENDING_ACTIONS, {
      ...action,
      createdAt: new Date().toISOString(),
      status: 'pending'
    });

    this.notifyListeners({ type: 'actionQueued', action });
  }

  async getPendingActions() {
    const db = await this.init();
    return db.getAll(STORES.PENDING_ACTIONS);
  }

  async removePendingAction(id) {
    const db = await this.init();
    await db.delete(STORES.PENDING_ACTIONS, id);
  }

  async syncPendingActions() {
    if (this.syncInProgress || !this.isOnline) return;

    this.syncInProgress = true;
    this.notifyListeners({ type: 'syncStart' });

    try {
      const actions = await this.getPendingActions();

      for (const action of actions) {
        try {
          await this.executePendingAction(action);
          await this.removePendingAction(action.id);
          this.notifyListeners({ type: 'actionSynced', action });
        } catch (error) {
          console.error('Failed to sync action:', action, error);
          this.notifyListeners({ type: 'actionFailed', action, error });
        }
      }

      this.notifyListeners({ type: 'syncComplete' });
    } finally {
      this.syncInProgress = false;
    }
  }

  async executePendingAction(action) {
    const API = process.env.REACT_APP_BACKEND_URL;

    switch (action.type) {
      case 'SAVE_JOB':
        await fetch(`${API}/api/jobs/${action.payload.jobId}/save`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(action.payload)
        });
        break;

      case 'APPLY_JOB':
        await fetch(`${API}/api/jobs/${action.payload.jobId}/apply`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(action.payload)
        });
        break;

      case 'SEND_MESSAGE':
        await fetch(`${API}/api/messages`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(action.payload)
        });
        break;

      default:
        console.warn('Unknown action type:', action.type);
    }
  }

  // ============== Sync Metadata ==============

  async updateSyncMeta(key, data) {
    const db = await this.init();
    await db.put(STORES.SYNC_META, { key, ...data });
  }

  async getSyncMeta(key) {
    const db = await this.init();
    return db.get(STORES.SYNC_META, key);
  }

  // ============== Settings ==============

  async setSetting(key, value) {
    const db = await this.init();
    await db.put(STORES.SETTINGS, { key, value });
  }

  async getSetting(key) {
    const db = await this.init();
    const result = await db.get(STORES.SETTINGS, key);
    return result?.value;
  }

  // ============== Storage Info ==============

  async getStorageInfo() {
    const db = await this.init();
    
    const jobsCount = await db.count(STORES.JOBS);
    const messagesCount = await db.count(STORES.MESSAGES);
    const pendingCount = await db.count(STORES.PENDING_ACTIONS);
    const jobsMeta = await this.getSyncMeta('jobs');

    return {
      jobs: { count: jobsCount, lastSync: jobsMeta?.lastSync },
      messages: { count: messagesCount },
      pendingActions: { count: pendingCount },
      isOnline: this.isOnline
    };
  }

  async clearAllCache() {
    const db = await this.init();
    await Promise.all([
      db.clear(STORES.JOBS),
      db.clear(STORES.RESUME),
      db.clear(STORES.MESSAGES),
      db.clear(STORES.PENDING_ACTIONS),
      db.clear(STORES.SYNC_META)
    ]);
  }
}

// Export singleton instance
export const offlineStorage = new OfflineStorageManager();

// React Hook for offline status
export const useOfflineStatus = () => {
  const [isOnline, setIsOnline] = React.useState(navigator.onLine);
  const [pendingCount, setPendingCount] = React.useState(0);
  const [lastSync, setLastSync] = React.useState(null);

  React.useEffect(() => {
    const updateStatus = async () => {
      const info = await offlineStorage.getStorageInfo();
      setPendingCount(info.pendingActions.count);
      setLastSync(info.jobs.lastSync);
    };

    const unsubscribe = offlineStorage.addListener((event) => {
      if (event.type === 'online') setIsOnline(true);
      if (event.type === 'offline') setIsOnline(false);
      updateStatus();
    });

    updateStatus();
    return unsubscribe;
  }, []);

  return { isOnline, pendingCount, lastSync };
};

// Import React for the hook
import React from 'react';

export default offlineStorage;
