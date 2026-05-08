#!/usr/bin/env node
/**
 * WCAG axe-core audit script — supports both batch (default routes) and CLI single-URL modes.
 *
 * Excluded permanently: #emergent-badge is injected by the preview environment only.
 * It does not exist in production builds. Excluding to prevent false positives in CI.
 *
 * USAGE
 * Batch mode (scans default ROUTES list):
 *   node scripts/wcag_audit.cjs
 *
 * Single-URL mode (used by ACC-01..05 pytest gate + CI):
 *   node scripts/wcag_audit.cjs --url http://localhost:3000/login \
 *     --tags wcag2a,wcag2aa,wcag21aa,wcag22aa \
 *     --exclude "#emergent-badge" \
 *     --format json \
 *     --save axe-results/login.json
 */
const { chromium } = require('playwright');
const { AxeBuilder } = require('@axe-core/playwright');
const fs = require('fs');
const path = require('path');

// --- Permanent excludes (CI false-positive safelist) -----------------------
// Excluded: #emergent-badge is injected by the preview environment only.
// It does not exist in production builds. Excluding to prevent false positives in CI.
const PERMANENT_EXCLUDES = ['#emergent-badge'];

// --- CLI arg parsing -------------------------------------------------------
function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
      args[k] = v;
    }
  }
  return args;
}

const args = parseArgs(process.argv);
const SINGLE_URL = args.url;
const TAGS = (args.tags || 'wcag2a,wcag2aa,wcag21aa,wcag22aa').split(',').map(s => s.trim());
const USER_EXCLUDES = args.exclude
  ? (Array.isArray(args.exclude) ? args.exclude : [args.exclude])
  : [];
const ALL_EXCLUDES = [...new Set([...PERMANENT_EXCLUDES, ...USER_EXCLUDES])];
const FORMAT = args.format || 'json';
const SAVE_PATH = args.save;

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

async function scanOne(page, url) {
  await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(800);

  let builder = new AxeBuilder({ page }).withTags(TAGS);
  for (const sel of ALL_EXCLUDES) {
    builder = builder.exclude(sel);
  }
  return await builder.analyze();
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1366, height: 900 } });
  const page = await context.newPage();

  // ----- Single-URL mode (CI / pytest gate) -----
  if (SINGLE_URL) {
    try {
      const results = await scanOne(page, SINGLE_URL);
      if (SAVE_PATH) {
        const outPath = path.isAbsolute(SAVE_PATH) ? SAVE_PATH : path.join(process.cwd(), SAVE_PATH);
        fs.mkdirSync(path.dirname(outPath), { recursive: true });
        fs.writeFileSync(outPath, JSON.stringify(results, null, 2));
      }
      // Print to stdout for pytest to consume
      process.stdout.write(JSON.stringify(results));
      await browser.close();
      process.exit(0);
    } catch (e) {
      process.stderr.write(`axe scan failed: ${e.message}\n`);
      await browser.close();
      process.exit(2);
    }
  }

  // ----- Batch mode -----
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

  const summary = [];
  const allViolations = {};

  for (const route of ROUTES) {
    const url = `${BASE}${route.path}`;
    process.stdout.write(`Scanning ${url} ... `);
    try {
      const results = await scanOne(page, url);
      fs.writeFileSync(path.join(OUT_DIR, `${route.slug}.json`), JSON.stringify(results, null, 2));

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

  const aggregated = Object.values(allViolations)
    .map(v => ({ ...v, pages: Array.from(v.pages) }))
    .sort((a, b) => b.nodes - a.nodes);

  const summaryFile = SAVE_PATH || path.join(OUT_DIR, '_summary.json');
  fs.mkdirSync(path.dirname(path.isAbsolute(summaryFile) ? summaryFile : path.join(process.cwd(), summaryFile)), { recursive: true });
  fs.writeFileSync(
    path.isAbsolute(summaryFile) ? summaryFile : path.join(process.cwd(), summaryFile),
    JSON.stringify({ scanned: ROUTES.length, excludes: ALL_EXCLUDES, tags: TAGS, summary, aggregated, violations: aggregated }, null, 2)
  );

  console.log('\n=== TOP RULE VIOLATIONS ===');
  aggregated.slice(0, 15).forEach(v => {
    console.log(`  [${(v.impact || '?').padEnd(8)}] ${v.id.padEnd(35)} ${String(v.nodes).padStart(4)} nodes across ${v.pages.length} pages`);
  });
  console.log(`Permanent excludes applied: ${ALL_EXCLUDES.join(', ')}`);

  await browser.close();
})();
