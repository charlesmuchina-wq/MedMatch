# MedMatch i18n Best Practices Documentation

## Overview

This document outlines the industry-standard internationalization (i18n) patterns implemented in MedMatch, based on CLDR standards, i18next best practices, and linguistic code switching guidelines.

## Implemented Patterns

### 1. Atomic Language Switching (CLDR Standard)

**Problem Solved:** Race conditions and UI flickering during language switches.

**Implementation:**
```javascript
const loadTranslationsAtomically = async (lang) => {
  // Step 1: Check localStorage cache (instant)
  // Step 2: Fetch pre-rendered translations (fast, ~100ms)  
  // Step 3: ATOMIC UPDATE - Apply all collected translations at once
  // Step 4: Load remaining AI translations in background (non-blocking)
}
```

**Key Principles:**
- Sequential loading with await (prevents race conditions)
- Fallback chain: Cached → Pre-rendered → AI
- Atomic state update (all translations applied at once)
- Loading gate prevents partial renders

### 2. Translation Fallback Chain

```
Priority Order:
1. localStorage cache (instant, 0ms)
2. Server pre-rendered translations (fast, ~100ms)
3. AI-generated translations (slow, 2-10s)
```

### 3. Progressive Enhancement

- **Bundled languages** (en, es, fr, de, zh): Instant loading
- **AI-powered languages** (55+ languages): Progressive loading with fallbacks

### 4. Loading States

- Sidebar: "Loading translations..." indicator
- Quick Actions: "Translating..." badge
- Progress bar for translation completion

## File Structure

```
/app/frontend/src/
├── utils/
│   └── i18n.jsx              # Main i18n provider with atomic switching
├── locales/
│   ├── en.json               # English (bundled)
│   ├── es.json               # Spanish (bundled)
│   ├── fr.json               # French (bundled)
│   ├── de.json               # German (bundled)
│   └── zh.json               # Chinese (bundled)

/app/backend/routes/
└── translation.py            # Translation API with pre-rendering
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/translate/prerender/{lang}` | GET | Get pre-rendered UI translations |
| `/api/translate/batch` | POST | Translate batch of texts via AI |
| `/api/translate/text` | POST | Translate single text |
| `/api/translate/languages` | GET | Get supported languages list |

## Supported Languages

### Bundled (Instant Loading) - PA-1 COMPLETE
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- **Japanese (ja)** ✅ NEW
- **Arabic (ar)** ✅ NEW
- **Hindi (hi)** ✅ NEW
- **Portuguese-BR (pt-BR)** ✅ NEW

### AI-Powered (Progressive Loading)
- Korean (ko)
- Swahili (sw)
- Hausa (ha)
- Yoruba (yo)
- Zulu (zu)
- Amharic (am)
- And 45+ more languages

## RTL (Right-to-Left) Support

Automatically applied for:
- Arabic (ar)
- Hebrew (he)
- Persian/Farsi (fa)
- Urdu (ur)

```javascript
document.documentElement.dir = rtl ? "rtl" : "ltr";
```

## Best Practices Checklist

- [x] Atomic language switching (no partial renders)
- [x] Translation fallback chain
- [x] Server-side pre-rendering for priority keys
- [x] Progressive loading with visible indicators
- [x] RTL layout support
- [x] localStorage caching for instant reload
- [x] Server-side caching (24-hour TTL)
- [x] Merge translations (don't replace)
- [x] Non-blocking background translation loading

## References

- [CLDR - Unicode Common Locale Data Repository](https://cldr.unicode.org/)
- [i18next Best Practices](https://www.i18next.com/overview/best-practices)
- [React Intl Documentation](https://formatjs.io/docs/react-intl/)
- [ICU MessageFormat](https://unicode-org.github.io/icu/userguide/format_parse/messages/)

---

*Last Updated: February 3, 2026*
