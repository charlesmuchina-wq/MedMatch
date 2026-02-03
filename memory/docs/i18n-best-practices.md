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
| `/api/translate/memory/store` | POST | Store translation in memory (TMX) |
| `/api/translate/memory/lookup` | GET | Lookup translation from memory |
| `/api/translate/memory/stats` | GET | Translation memory statistics |
| `/api/translate/memory/analytics` | GET | Enhanced TM analytics (Admin) |
| `/api/translate/quality/score` | POST | Score translation quality |
| `/api/translate/quality/batch-score` | POST | Batch score translations |
| `/api/translate/quality/stats` | GET | Quality statistics (Admin) |
| `/api/translate/analytics/dashboard` | GET | Full analytics dashboard (Admin) |
| `/api/translate/gender-rules` | GET | Get linguistic gender rules for all languages |
| `/api/translate/gender-rules/{lang}` | GET | Get gender rules for a specific language |
| `/api/translate/gender-aware` | POST | Translate with explicit grammatical gender |
| `/api/translate/gender-variants` | POST | Get all gender variants of a translation |

## Supported Languages

### Bundled (Instant Loading) - COMPLETE
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- Arabic (ar)
- Hindi (hi)
- Portuguese-BR (pt-BR)
- **All 16 African Languages** ✅ NEW (sw, ha, yo, ig, zu, xh, af, am, om, so, rw, sn, ny, tw, wo, lg)

### AI-Powered (Progressive Loading)
- Korean (ko)
- And 40+ more languages

## RTL (Right-to-Left) Support

Automatically applied for:
- Arabic (ar)
- Hebrew (he)
- Persian/Farsi (fa)
- Urdu (ur)

```javascript
document.documentElement.dir = rtl ? "rtl" : "ltr";
```

## Linguistic Gender Support (NEW - CLDR-based)

MedMatch now supports grammatical gender-aware translations following ICU MessageFormat principles.

### Why Grammatical Gender Matters

In many languages (Spanish, French, German, Arabic, Hindi, etc.), adjectives, participles, and pronouns must agree with the gender of the person being addressed. For example:
- **English:** "You are connected"
- **Spanish (masculine):** "Estás conectado"
- **Spanish (feminine):** "Estás conectada"
- **French (masculine):** "Bienvenu"
- **French (feminine):** "Bienvenue"

### Supported Gendered Languages

| Language | Gender System | Available Forms |
|----------|---------------|-----------------|
| Spanish, French, Italian, Portuguese | Binary | masculine, feminine |
| German, Russian, Polish | Ternary | masculine, feminine, neuter |
| Arabic, Hebrew, Hindi | Binary | masculine, feminine |
| Dutch | Common/Neuter | common, neuter |

### User Preference

Users can set their grammatical gender preference in Settings → Language → Grammatical Gender:
- **Masculine**: Use masculine grammatical forms
- **Feminine**: Use feminine grammatical forms  
- **Neutral**: Use neutral/inclusive forms where available
- **Auto**: Use language default (typically masculine for historical reasons)

### Implementation

```javascript
// Frontend: useGenderAwareTranslation hook
import { useGenderAwareTranslation } from '@/utils/i18n';

const { translated, isLoading } = useGenderAwareTranslation(
  "Welcome back",
  "feminine", // user's gender preference
  { context: "dashboard greeting" }
);

// Or use the GenderText component
<GenderText text="You are connected" gender="feminine" />
```

```python
# Backend: Gender-aware translation endpoint
POST /api/translate/gender-aware
{
    "text": "Welcome back",
    "target_language": "es",
    "grammatical_gender": "feminine",
    "context": "dashboard greeting"
}
# Response: { "translated": "Bienvenida" }
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
- [x] **Linguistic gender awareness (NEW)**
- [x] **User gender preference settings (NEW)**

## References

- [CLDR - Unicode Common Locale Data Repository](https://cldr.unicode.org/)
- [i18next Best Practices](https://www.i18next.com/overview/best-practices)
- [React Intl Documentation](https://formatjs.io/docs/react-intl/)
- [ICU MessageFormat](https://unicode-org.github.io/icu/userguide/format_parse/messages/)
- [Gender-Inclusive Language Guidelines (UN)](https://www.un.org/en/gender-inclusive-language/guidelines.shtml)

---

*Last Updated: February 3, 2026*
