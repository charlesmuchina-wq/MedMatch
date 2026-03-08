/**
 * ENZI E2EE - End-to-End Encryption utilities
 * Uses Web Crypto API for ECDH key exchange + AES-GCM encryption
 */

const DB_NAME = 'enzi_e2ee';
const STORE_NAME = 'keys';

// IndexedDB for persistent key storage
const openDB = () => new Promise((resolve, reject) => {
  const req = indexedDB.open(DB_NAME, 1);
  req.onupgradeneeded = (e) => { e.target.result.createObjectStore(STORE_NAME); };
  req.onsuccess = (e) => resolve(e.target.result);
  req.onerror = (e) => reject(e.target.error);
});

const storeKey = async (key, value) => {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    tx.objectStore(STORE_NAME).put(value, key);
    tx.oncomplete = () => resolve();
    tx.onerror = (e) => reject(e.target.error);
  });
};

const getKey = async (key) => {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const req = tx.objectStore(STORE_NAME).get(key);
    req.onsuccess = () => resolve(req.result);
    req.onerror = (e) => reject(e.target.error);
  });
};

/**
 * Generate ECDH key pair for E2EE
 */
export const generateKeyPair = async () => {
  const keyPair = await window.crypto.subtle.generateKey(
    { name: 'ECDH', namedCurve: 'P-256' },
    true,
    ['deriveKey']
  );

  // Export public key as JWK
  const publicKeyJwk = await window.crypto.subtle.exportKey('jwk', keyPair.publicKey);
  const privateKeyJwk = await window.crypto.subtle.exportKey('jwk', keyPair.privateKey);

  // Store private key locally (never leaves device)
  await storeKey('privateKey', privateKeyJwk);
  await storeKey('publicKey', publicKeyJwk);

  return { publicKey: JSON.stringify(publicKeyJwk), privateKey: privateKeyJwk };
};

/**
 * Get stored private key
 */
export const getPrivateKey = async () => {
  const jwk = await getKey('privateKey');
  if (!jwk) return null;
  return window.crypto.subtle.importKey(
    'jwk', jwk,
    { name: 'ECDH', namedCurve: 'P-256' },
    false, ['deriveKey']
  );
};

/**
 * Get stored public key JWK string
 */
export const getPublicKeyJwk = async () => {
  const jwk = await getKey('publicKey');
  return jwk ? JSON.stringify(jwk) : null;
};

/**
 * Derive shared AES key from my private key + partner's public key
 */
export const deriveSharedKey = async (partnerPublicKeyJwk) => {
  const privateKey = await getPrivateKey();
  if (!privateKey) throw new Error('No private key found');

  const partnerKey = await window.crypto.subtle.importKey(
    'jwk', typeof partnerPublicKeyJwk === 'string' ? JSON.parse(partnerPublicKeyJwk) : partnerPublicKeyJwk,
    { name: 'ECDH', namedCurve: 'P-256' },
    false, []
  );

  return window.crypto.subtle.deriveKey(
    { name: 'ECDH', public: partnerKey },
    privateKey,
    { name: 'AES-GCM', length: 256 },
    false, ['encrypt', 'decrypt']
  );
};

/**
 * Encrypt a message with AES-GCM
 */
export const encryptMessage = async (text, sharedKey) => {
  const encoder = new TextEncoder();
  const iv = window.crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await window.crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    sharedKey,
    encoder.encode(text)
  );

  return {
    encrypted: btoa(String.fromCharCode(...new Uint8Array(encrypted))),
    iv: btoa(String.fromCharCode(...iv))
  };
};

/**
 * Decrypt a message with AES-GCM
 */
export const decryptMessage = async (encryptedBase64, ivBase64, sharedKey) => {
  try {
    const encrypted = Uint8Array.from(atob(encryptedBase64), c => c.charCodeAt(0));
    const iv = Uint8Array.from(atob(ivBase64), c => c.charCodeAt(0));
    const decrypted = await window.crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      sharedKey,
      encrypted
    );
    return new TextDecoder().decode(decrypted);
  } catch {
    return '[Encrypted message - unable to decrypt]';
  }
};

/**
 * Check if E2EE is supported in this browser
 */
export const isE2EESupported = () => {
  return typeof window !== 'undefined' && 
    window.crypto?.subtle && 
    typeof indexedDB !== 'undefined';
};
