#!/usr/bin/env node
/**
 * Authenticated WCAG axe-core audit — logs in first, then scans gated routes
 */
const { chromium } = require('playwright');
const { AxeBuilder } = require('@axe-core/playwright');
const fs = require('fs');
const path = require('path');

const BASE = process.env.AXE_BASE_URL || 'http://localhost:3000';
const OUT_DIR = '/app/docs/security/axe-results-auth';
const ADMIN_EMAIL = 'admin@medmatch.com';
const ADMIN_PASS = 'Swampdrainer2026!';

const ROUTES = [
  { slug: 'dashboard', path: '/dashboard' },
  { slug: 'jobs', path: '/jobs' },
  { slug: 'profile', path: '/profile' },
  { slug: 'messages', path: '/messages' },
  { slug: 'meetings', path: '/meetings' },
  { slug: 'admin', path: '/admin' },
  { slug: 'recruiter-dashboard', path: '/recruiter/dashboard' },
];

(async () => {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1366, height: 900 } });
  const page = await context.newPage();

  // Login
  console.log('Logging in as', ADMIN_EMAIL);
  await page.goto(`${BASE}/login`, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(800);

  // Inject auth token directly via API + localStorage (bypass UI login flow)
  console.log('Fetching auth token from API for', ADMIN_EMAIL);
  const apiBase = (process.env.REACT_APP_BACKEND_URL || BASE).replace(/\/$/, '');
  const loginRes = await fetch(`${apiBase}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: ADMIN_EMAIL, password: ADMIN_PASS }),
  });
  const loginData = await loginRes.json();
  const token = loginData.access_token || loginData.token;
  if (!token) {
    console.error('Login failed:', JSON.stringify(loginData).slice(0, 200));
    process.exit(1);
  }
  console.log('Token acquired (len=', token.length, '), role=', loginData.user?.role || 'n/a');

  // Visit login page first to set localStorage on the right origin
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.evaluate(({ tok, user }) => {
    localStorage.setItem('medmatch-token', tok);
    localStorage.setItem('token', tok);
    localStorage.setItem('session_token', tok);
    if (user) localStorage.setItem('medmatch-user', JSON.stringify(user));
    localStorage.setItem('medmatch-consent-granted', 'true');
  }, { tok: token, user: loginData.user });

  const summary = [];
  const allViolations = {};

  for (const route of ROUTES) {
    const url = `${BASE}${route.path}`;
    process.stdout.write(`Scanning ${url} ... `);
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(1200);

      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
        .analyze();

      fs.writeFileSync(path.join(OUT_DIR, `${route.slug}.json`), JSON.stringify(results, null, 2));

      const counts = { critical: 0, serious: 0, moderate: 0, minor: 0 };
      results.violations.forEach(v => {
        const sev = v.impact || 'minor';
        counts[sev] = (counts[sev] || 0) + v.nodes.length;
        if (!allViolations[v.id]) allViolations[v.id] = { id: v.id, impact: v.impact, help: v.help, nodes: 0, pages: new Set() };
        allViolations[v.id].nodes += v.nodes.length;
        allViolations[v.id].pages.add(route.slug);
      });
      console.log(`${results.violations.length} rules · ${counts.critical}C/${counts.serious}S/${counts.moderate}M/${counts.minor}m`);
      summary.push({ route: route.path, total: results.violations.length, ...counts, finalUrl: page.url() });
    } catch (e) {
      console.log(`FAIL: ${e.message.slice(0, 80)}`);
      summary.push({ route: route.path, error: e.message.slice(0, 200) });
    }
  }

  const aggregated = Object.values(allViolations)
    .map(v => ({ ...v, pages: Array.from(v.pages) }))
    .sort((a, b) => b.nodes - a.nodes);

  fs.writeFileSync(path.join(OUT_DIR, '_summary.json'),
    JSON.stringify({ scanned: ROUTES.length, summary, aggregated }, null, 2));

  console.log('\n=== TOP RULE VIOLATIONS (Authenticated) ===');
  aggregated.slice(0, 20).forEach(v => {
    console.log(`  [${(v.impact || '?').padEnd(8)}] ${v.id.padEnd(35)} ${String(v.nodes).padStart(4)} nodes / ${v.pages.length} pages`);
  });

  await browser.close();
})();
