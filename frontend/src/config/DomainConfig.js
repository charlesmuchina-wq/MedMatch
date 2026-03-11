/**
 * DomainConfig — Source of truth for all domain-to-portal routing
 * 
 * Each domain entry defines:
 * - portal: Which portal view to show (ecosystem|karau|enzi|medmatch|careers)
 * - title: Browser tab title
 * - tagline: Subtitle shown on login/landing
 * - audience: Target user type
 * - autoBundle: Whether to auto-bundle KARAU+ENZI
 * - standalone: Whether this domain operates independently from aikarau.com auth
 * - skipPortalSelector: Go straight to login/app without portal picker
 * - primaryColor: Brand accent color for this domain entry
 */

const DOMAIN_MAP = {
  // ═══════ Main Ecosystem ═══════
  'aikarau.com': {
    portal: 'ecosystem',
    title: 'MedMatch-AI KARAU',
    tagline: 'The Complete Recruitment & Communication Ecosystem',
    audience: 'recruiter',
    autoBundle: true,
    skipPortalSelector: false,
    primaryColor: '#00B894',
  },
  'ai.karau.com': {
    portal: 'ecosystem',
    title: 'AI KARAU Ecosystem',
    tagline: 'The Complete Recruitment & Communication Ecosystem',
    audience: 'recruiter',
    autoBundle: true,
    skipPortalSelector: false,
    primaryColor: '#00B894',
  },

  // ═══════ MedMatch (Company & Recruiter Focus) ═══════
  'medmatch.aikarau.com': {
    portal: 'medmatch',
    title: 'MedMatch AI — Enterprise Recruitment Platform',
    tagline: 'AI-powered internal recruitment, talent management & hiring intelligence for companies',
    audience: 'company',
    autoBundle: false,
    skipPortalSelector: true,
    primaryColor: '#00B894',
  },

  // ═══════ Job Seekers ═══════
  'careers.aikarau.com': {
    portal: 'careers',
    title: 'AI KARAU Careers',
    tagline: 'Find your next opportunity with AI-powered matching',
    audience: 'jobseeker',
    autoBundle: false,
    skipPortalSelector: true,
    primaryColor: '#00CEC9',
  },
  'jobs.aikarau.com': {
    portal: 'careers',
    title: 'AI KARAU Jobs',
    tagline: 'Discover opportunities in life sciences',
    audience: 'jobseeker',
    autoBundle: false,
    skipPortalSelector: true,
    primaryColor: '#00CEC9',
  },

  // ═══════ AI KARAU Meetings ═══════
  'connect.aikarau.com': {
    portal: 'karau',
    title: 'AI KARAU Connect',
    tagline: 'HD meetings with AI transcription & collaboration',
    audience: 'all',
    autoBundle: true,
    skipPortalSelector: true,
    primaryColor: '#6C5CE7',
  },
  'meet.aikarau.com': {
    portal: 'karau',
    title: 'AI KARAU Meet',
    tagline: 'Start or join a meeting',
    audience: 'all',
    autoBundle: true,
    skipPortalSelector: true,
    primaryColor: '#6C5CE7',
  },

  // ═══════ ENZI Messenger ═══════
  'enzi.aikarau.com': {
    portal: 'enzi',
    title: 'ENZI — Actionable Intelligence Messenger',
    tagline: 'Professional messaging powered by AI',
    audience: 'all',
    autoBundle: true,
    skipPortalSelector: true,
    primaryColor: '#00CEC9',
  },
  'enzilink.com': {
    portal: 'enzi',
    title: 'ENZI — Actionable Intelligence Messenger',
    tagline: 'Professional messaging powered by AI',
    audience: 'all',
    autoBundle: true,
    standalone: true,
    skipPortalSelector: true,
    primaryColor: '#00CEC9',
  },
};

// All registered domains for CORS
export const ALL_DOMAINS = [
  'https://aikarau.com',
  'https://www.aikarau.com',
  'https://ai.karau.com',
  'https://medmatch.aikarau.com',
  'https://careers.aikarau.com',
  'https://jobs.aikarau.com',
  'https://connect.aikarau.com',
  'https://meet.aikarau.com',
  'https://enzi.aikarau.com',
  'https://enzilink.com',
  'https://www.enzilink.com',
];

// Cookie domain mapping for shared auth
export const COOKIE_DOMAINS = {
  '.aikarau.com': ['aikarau.com', 'ai.karau.com', 'medmatch.aikarau.com', 'careers.aikarau.com', 'jobs.aikarau.com', 'connect.aikarau.com', 'meet.aikarau.com', 'enzi.aikarau.com'],
  '.enzilink.com': ['enzilink.com'],
};

/**
 * Resolve the current hostname to a domain config
 * Supports:
 * - Exact domain match (production)
 * - ?portal= query param (testing in any environment)
 * - Subdomain extraction from aikarau.com
 * - Preview/localhost fallback to ecosystem
 */
export function resolveDomainConfig(hostname, searchParams) {
  // 1. Check ?portal= param first (for testing)
  const portalParam = searchParams?.get('portal');
  if (portalParam) {
    const paramMap = {
      'karau': 'meet.aikarau.com',
      'meet': 'meet.aikarau.com',
      'connect': 'connect.aikarau.com',
      'enzi': 'enzi.aikarau.com',
      'enzilink': 'enzilink.com',
      'medmatch': 'medmatch.aikarau.com',
      'careers': 'careers.aikarau.com',
      'jobs': 'jobs.aikarau.com',
      'ecosystem': 'aikarau.com',
    };
    const mappedDomain = paramMap[portalParam.toLowerCase()];
    if (mappedDomain && DOMAIN_MAP[mappedDomain]) {
      return { ...DOMAIN_MAP[mappedDomain], resolvedFrom: `?portal=${portalParam}` };
    }
  }

  // 2. Exact hostname match
  if (DOMAIN_MAP[hostname]) {
    return { ...DOMAIN_MAP[hostname], resolvedFrom: hostname };
  }

  // 3. Check if hostname includes known base domain
  if (hostname.endsWith('.aikarau.com')) {
    const sub = hostname.replace('.aikarau.com', '');
    const fullDomain = `${sub}.aikarau.com`;
    if (DOMAIN_MAP[fullDomain]) {
      return { ...DOMAIN_MAP[fullDomain], resolvedFrom: fullDomain };
    }
  }

  // 4. Check for enzilink.com variants
  if (hostname === 'enzilink.com' || hostname === 'www.enzilink.com') {
    return { ...DOMAIN_MAP['enzilink.com'], resolvedFrom: 'enzilink.com' };
  }

  // 5. Default: ecosystem (portal selector) — for localhost, preview, unknown
  return {
    portal: 'ecosystem',
    title: 'MedMatch-AI KARAU',
    tagline: 'Choose your app',
    audience: 'all',
    autoBundle: true,
    skipPortalSelector: false,
    primaryColor: '#00B894',
    resolvedFrom: 'default',
  };
}

export default DOMAIN_MAP;
