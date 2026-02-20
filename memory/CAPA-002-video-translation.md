# CAPA-002: Video Avatar Quality & Translation Coverage

## Corrective and Preventive Action Report

**CAPA Number:** CAPA-002  
**Date Opened:** February 20, 2026  
**Severity:** High  
**Status:** In Progress

---

## 1. Problem Description

### 1.1 Video Avatar Issues
| Issue | Affected Languages | Root Cause |
|-------|-------------------|------------|
| Unnatural mouth movements | sw, af, ha, zu | Source images have phone/accessories in frame |
| Unnatural neck/head | ar, tr | Poor pose for D-ID face animation |
| Robotic movements | pt, es | Static/unnatural source pose |
| No male representation | All | Design decision, not inclusive |

### 1.2 Translation Coverage Issues
| Issue | Impact | Root Cause |
|-------|--------|------------|
| Partial translations | User confusion | Pages not using useTranslation hook |
| Missing translations | UX degradation | Hardcoded strings in components |
| Inconsistent coverage | ~10 pages affected | No pseudo-localization testing |

---

## 2. Root Cause Analysis

### 2.1 Avatar Issues
- **Primary Cause:** Source images selected from stock photos without D-ID compatibility testing
- **Contributing Factors:**
  - Images with phones/accessories create artifacts
  - Non-frontal poses cause unnatural head movements
  - Lack of consistent lighting across regions

### 2.2 Translation Issues
- **Primary Cause:** Components implemented without i18n hooks
- **Contributing Factors:**
  - No pseudo-localization testing in CI/CD
  - Hardcoded strings not flagged during code review
  - Missing translation keys for new features

---

## 3. Affected Components

### Pages Without useTranslation (Hardcoded Strings)
1. AdminDashboard.jsx (~28 strings)
2. AdminDataIntegrityPage.jsx (~29 strings)
3. AdminRecruiterVerificationPage.jsx (~12 strings)
4. AdminReviewModerationPage.jsx (~16 strings)
5. BlindScreeningDashboard.jsx (~10 strings)
6. CompanyProfilePage.jsx (~13 strings)
7. ProductionMetricsPage.jsx (~28 strings)
8. RecruiterJobsPage.jsx (~17 strings)
9. ResumeProfilesPage.jsx (~11 strings)
10. VideoTutorialsPage.jsx (~8 strings)

**Estimated Total:** ~172 hardcoded strings to extract

---

## 4. Corrective Actions

### 4.1 Avatar Quality Fix (Phase 1)
| Action | Owner | Target |
|--------|-------|--------|
| Generate AI professional headshots | Agent | Day 1 |
| 50/50 male/female split per region | Agent | Day 1 |
| Regenerate all 21 videos | Agent | Day 1-2 |
| Validate natural animations | User | Day 2 |

### 4.2 Translation Coverage Fix (Phase 2)
| Action | Owner | Target |
|--------|-------|--------|
| Implement pseudo-localization | Agent | Day 2 |
| Extract hardcoded strings | Agent | Day 2-3 |
| Add to en.json translation file | Agent | Day 2-3 |
| Generate translations for all languages | Agent | Day 3 |

---

## 5. Preventive Actions

### 5.1 Avatar Quality Standards
- [ ] Create D-ID source image guidelines document
- [ ] Require frontal pose, neutral expression
- [ ] No accessories, phones, hands near face
- [ ] Consistent professional lighting

### 5.2 Translation Process Improvements
- [ ] Add pseudo-localization test to build process
- [ ] ESLint rule for hardcoded strings
- [ ] Code review checklist item for i18n
- [ ] Automated translation coverage report

---

## 6. Implementation Plan

### Phase 1: Avatar Regeneration (Priority)
```
1. Generate AI avatars (image_generation_tool)
   - African male, African female
   - Asian male, Asian female  
   - South Asian male, South Asian female
   - Middle Eastern male, Middle Eastern female
   - Latino male, Latina female
   - European male, European female

2. Language-Avatar Assignment (50/50 split)
   MALE avatars: de, fr, ja, zh, hi, ar, pt, sw, af, ha
   FEMALE avatars: es, it, ko, vi, tr, ru, pl, sv, zu, en, nl

3. Regenerate all videos via D-ID API
4. Update database records
5. Verify natural animation quality
```

### Phase 2: Translation Coverage
```
1. Create pseudo-locale (en-PSEUDO)
2. Run pseudo-localization test
3. Identify all hardcoded strings
4. Extract to en.json
5. Generate translations for all 30+ languages
6. Deploy and verify
```

---

## 7. Verification

### Acceptance Criteria
- [ ] All videos show natural head/mouth movements
- [ ] 50% male, 50% female avatars
- [ ] No phones/accessories visible
- [ ] All pages show pseudo-locale text when enabled
- [ ] 100% translation coverage for all bundled languages

---

## 8. Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Reported By | User | 2026-02-20 | ✅ |
| CAPA Owner | Agent | 2026-02-20 | In Progress |
| QA Verification | User | Pending | ⏳ |
| Closure | TBD | TBD | ⏳ |
