#!/usr/bin/env node
/**
 * WCAG axe-core audit script
 * Scans key routes against wcag2a, wcag2aa, wcag21aa, wcag22aa tag set
 * Output: /app/docs/security/axe-results/*.json + summary
 */
const { chromium } = require('playwright');
const { AxeBuilder } = require('@axe-core/playwright');
const fs = require('fs');
const path = require('path');

const BASE = process.env.AXE_BASE_URL || 'http://localhost:3000';
const OUT_DIR = '/app/docs/security/axe-results';

const ROUTES = [
  { slug: 'home', path: '/' },
  { slug: 'login', path: '/login' },
  { slug: 'register', path: '/register' },
  { slug: 'dashboard', path: '/dashboard' },
  { slug: 'jobs', path: '/jobs' },
  { slug: 'profile', path: '/profile' },
  { slug: 'messages', path: '/messages' },
  { slug: 'meetings', path: '/meetings' },
  { slug: 'assessment', path: '/assessment' },
  { slug: 'accreditation', path: '/accreditation' },
  { slug: 'admin', path: '/admin' },
  { slug: 'recruiter-dashboard', path: '/recruiter/dashboard' },
];

(async () => {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1366, height: 900 } });
  const page = await context.newPage();

  const summary = [];
  const allViolations = {};

  for (const route of ROUTES) {
    const url = `${BASE}${route.path}`;
    process.stdout.write(`Scanning ${url} ... `);
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      // Tiny pause for SPA hydration
      await page.waitForTimeout(800);

      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
        .analyze();

      const file = path.join(OUT_DIR, `${route.slug}.json`);
      fs.writeFileSync(file, JSON.stringify(results, null, 2));

      const counts = { critical: 0, serious: 0, moderate: 0, minor: 0 };
      results.violations.forEach(v => {
        counts[v.impact || 'minor'] = (counts[v.impact || 'minor'] || 0) + v.nodes.length;
        if (!allViolations[v.id]) allViolations[v.id] = { id: v.id, impact: v.impact, help: v.help, helpUrl: v.helpUrl, nodes: 0, pages: new Set() };
        allViolations[v.id].nodes += v.nodes.length;
        allViolations[v.id].pages.add(route.slug);
      });

      console.log(`${results.violations.length} violations (${counts.critical}C/${counts.serious}S/${counts.moderate}M/${counts.minor}m)`);
      summary.push({ route: route.path, total: results.violations.length, ...counts });
    } catch (e) {
      console.log(`FAIL: ${e.message.slice(0, 80)}`);
      summary.push({ route: route.path, error: e.message.slice(0, 200) });
    }
  }

  // Aggregate
  const aggregated = Object.values(allViolations)
    .map(v => ({ ...v, pages: Array.from(v.pages) }))
    .sort((a, b) => b.nodes - a.nodes);

  fs.writeFileSync(
    path.join(OUT_DIR, '_summary.json'),
    JSON.stringify({ scanned: ROUTES.length, summary, aggregated }, null, 2)
  );

  console.log('\n=== TOP RULE VIOLATIONS ===');
  aggregated.slice(0, 15).forEach(v => {
    console.log(`  [${(v.impact || '?').padEnd(8)}] ${v.id.padEnd(35)} ${String(v.nodes).padStart(4)} nodes across ${v.pages.length} pages`);
  });

  await browser.close();
})();
