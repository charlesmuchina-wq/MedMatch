/**
 * Subdomain Detection Utility
 * Detects which subdomain the user is on and routes accordingly
 * 
 * Domain Structure:
 * - aikarau.com (main) → Portal Selector
 * - medmatch.aikarau.com → MedMatch Jobs
 * - careers.aikarau.com → MedMatch Jobs
 * - jobs.aikarau.com → MedMatch Jobs
 * - meet.aikarau.com → AI KARAU Meeting
 */

// List of subdomains that should go to MedMatch Jobs portal
const JOBS_SUBDOMAINS = ['medmatch', 'careers', 'jobs'];

// Subdomain for AI KARAU Meeting portal
const MEETING_SUBDOMAIN = 'meet';

// Main domain (no subdomain) shows portal selector
const MAIN_DOMAIN = 'aikarau.com';

/**
 * Get the current subdomain from the hostname
 * @returns {string|null} The subdomain or null if on main domain
 */
export const getSubdomain = () => {
  const hostname = window.location.hostname;
  
  // Handle localhost and preview URLs (no subdomain routing)
  if (hostname === 'localhost' || hostname.includes('preview.emergentagent.com')) {
    return null;
  }
  
  // Check if we're on aikarau.com domain
  if (!hostname.includes('aikarau.com')) {
    return null;
  }
  
  // Extract subdomain from hostname
  // e.g., "medmatch.aikarau.com" → "medmatch"
  // e.g., "aikarau.com" → null (main domain)
  const parts = hostname.split('.');
  
  // If hostname is exactly "aikarau.com", no subdomain
  if (parts.length === 2 && parts[0] === 'aikarau') {
    return null;
  }
  
  // If we have 3+ parts, the first part is the subdomain
  if (parts.length >= 3) {
    return parts[0].toLowerCase();
  }
  
  return null;
};

/**
 * Determine which portal to show based on subdomain
 * @returns {'portal-selector' | 'jobs' | 'meeting'} The portal type
 */
export const getPortalType = () => {
  const subdomain = getSubdomain();
  
  // No subdomain → show portal selector
  if (!subdomain) {
    return 'portal-selector';
  }
  
  // Jobs-related subdomains → go to MedMatch Jobs
  if (JOBS_SUBDOMAINS.includes(subdomain)) {
    return 'jobs';
  }
  
  // Meeting subdomain → go to AI KARAU Meeting
  if (subdomain === MEETING_SUBDOMAIN) {
    return 'meeting';
  }
  
  // Unknown subdomain → default to portal selector
  return 'portal-selector';
};

/**
 * Check if we should skip the portal selector
 * @returns {boolean} True if we should skip to a specific portal
 */
export const shouldSkipPortalSelector = () => {
  return getPortalType() !== 'portal-selector';
};

/**
 * Get the portal name for display purposes
 * @returns {string} Human-readable portal name
 */
export const getPortalName = () => {
  const portalType = getPortalType();
  switch (portalType) {
    case 'jobs':
      return 'MedMatch AI Jobs';
    case 'meeting':
      return 'AI KARAU Meeting';
    default:
      return 'AI KARAU';
  }
};

export default {
  getSubdomain,
  getPortalType,
  shouldSkipPortalSelector,
  getPortalName,
  JOBS_SUBDOMAINS,
  MEETING_SUBDOMAIN,
  MAIN_DOMAIN,
};
