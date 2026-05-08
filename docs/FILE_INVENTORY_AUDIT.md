# File Inventory for Third-Party Audit
## Generated: March 22, 2026

This document provides a machine-readable inventory of all Python (.py) and Markdown (.md) files in the AI Suite codebase, including file paths, line counts, and last-modified metadata.

---

## Python Files (228 files, 96,680 lines of code)

### Backend Entry Point
| File | Lines | Purpose |
|------|-------|---------|
| `/app/backend/server.py` | 828 | FastAPI application entry, router registration, middleware, startup/shutdown |

### Models (`/app/backend/models/`)
| File | Lines | Purpose |
|------|-------|---------|
| `/app/backend/models/__init__.py` | 2 | Package init |
| `/app/backend/models/schemas.py` | 165 | Pydantic data models |

### Route Modules (`/app/backend/routes/`) — 131 files
| File | Lines | Domain |
|------|-------|--------|
| `/app/backend/routes/__init__.py` | 152 | Package init with exports |
| `/app/backend/routes/admin_audit.py` | 685 | Admin audit logging |
| `/app/backend/routes/advanced_features.py` | 590 | Advanced platform features |
| `/app/backend/routes/ai_compliance.py` | 190 | AI compliance monitoring |
| `/app/backend/routes/ai_features.py` | 1061 | Core AI features (matching, analysis) |
| `/app/backend/routes/ai_productivity.py` | 1434 | AI productivity tools |
| `/app/backend/routes/ai_qa.py` | 490 | AI quality assurance |
| `/app/backend/routes/ai_talent.py` | 277 | AI talent matching |
| `/app/backend/routes/analytics.py` | 253 | Core analytics |
| `/app/backend/routes/analytics_funnel.py` | 339 | Funnel analytics |
| `/app/backend/routes/ats.py` | 664 | Applicant tracking system |
| `/app/backend/routes/audit_reports.py` | 524 | Audit report generation |
| `/app/backend/routes/auth.py` | 1544 | Authentication (all providers) |
| `/app/backend/routes/autofill.py` | 402 | Resume autofill |
| `/app/backend/routes/avatar.py` | 127 | AI avatar generation |
| `/app/backend/routes/batch.py` | 144 | Batch operations |
| `/app/backend/routes/behavioral.py` | 298 | Behavioral analysis |
| `/app/backend/routes/biometric.py` | 588 | Biometric authentication |
| `/app/backend/routes/capa.py` | 372 | CAPA management |
| `/app/backend/routes/cloud.py` | 549 | Cloud storage integration |
| `/app/backend/routes/companies.py` | 333 | Company profiles |
| `/app/backend/routes/compliance_alerts.py` | 298 | Compliance alert system |
| `/app/backend/routes/credentials.py` | 926 | Credential management |
| `/app/backend/routes/data_integrity.py` | 212 | Data integrity monitoring |
| `/app/backend/routes/dei_analytics.py` | 96 | DEI analytics |
| `/app/backend/routes/digest.py` | 321 | Email digest system |
| `/app/backend/routes/dragon.py` | 682 | Dragon scheduler interface |
| `/app/backend/routes/dragon_automator.py` | 1352 | Dragon automation rules |
| `/app/backend/routes/e2ee.py` | 146 | End-to-end encryption |
| `/app/backend/routes/email_settings.py` | 118 | Email configuration |
| `/app/backend/routes/employer_reviews.py` | 430 | Employer reviews |
| `/app/backend/routes/enterprise_api.py` | 846 | Enterprise API |
| `/app/backend/routes/enzi_ai.py` | 111 | ENZI AI assistant |
| `/app/backend/routes/enzi_automation.py` | 278 | ENZI automation |
| `/app/backend/routes/enzi_bots.py` | 880 | Bot marketplace |
| `/app/backend/routes/enzi_channel_templates.py` | 130 | Channel templates |
| `/app/backend/routes/enzi_domain.py` | 90 | Custom domain support |
| `/app/backend/routes/enzi_invites.py` | 271 | Invite system |
| `/app/backend/routes/enzi_meetings.py` | 164 | Meeting integration |
| `/app/backend/routes/enzi_notifications.py` | 120 | Notification preferences |
| `/app/backend/routes/enzi_payments.py` | 153 | Premium packages |
| `/app/backend/routes/enzi_sentiment.py` | 100 | Sentiment analysis |
| `/app/backend/routes/enzi_webhook_templates.py` | 115 | Webhook templates |
| `/app/backend/routes/feedback.py` | 333 | Feedback system |
| `/app/backend/routes/geolocation.py` | 219 | Geolocation services |
| `/app/backend/routes/global_compliance.py` | 158 | Global compliance |
| `/app/backend/routes/id_verification.py` | 322 | ID verification |
| `/app/backend/routes/interview.py` | 507 | Interview preparation |
| `/app/backend/routes/interview_calendar.py` | 722 | Interview scheduling |
| `/app/backend/routes/job_verification.py` | 109 | Job posting verification |
| `/app/backend/routes/jobs.py` | 1158 | Job CRUD and search |
| `/app/backend/routes/karau_accessibility.py` | 219 | Meeting accessibility |
| `/app/backend/routes/karau_ai.py` | 189 | KARAU AI features |
| `/app/backend/routes/karau_analytics.py` | 341 | Meeting analytics |
| `/app/backend/routes/karau_beamforming.py` | 285 | Audio beamforming |
| `/app/backend/routes/karau_biometric_verify.py` | 193 | Biometric feed verification |
| `/app/backend/routes/karau_breakout_lounges.py` | 219 | Breakout rooms |
| `/app/backend/routes/karau_calendar.py` | 367 | Calendar integration |
| `/app/backend/routes/karau_collaboration.py` | 417 | Collaborative tools |
| `/app/backend/routes/karau_director.py` | 131 | AI director mode |
| `/app/backend/routes/karau_enhanced_sentiment.py` | 243 | Enhanced sentiment |
| `/app/backend/routes/karau_extended.py` | 727 | Extended meeting features |
| `/app/backend/routes/karau_gamification.py` | 161 | Gamification |
| `/app/backend/routes/karau_ghost_booking.py` | 156 | Ghost booking prevention |
| `/app/backend/routes/karau_guest_verification.py` | 305 | Guest verification |
| `/app/backend/routes/karau_hardware_discovery.py` | 197 | Hardware discovery |
| `/app/backend/routes/karau_intelligence.py` | 297 | Meeting intelligence |
| `/app/backend/routes/karau_iot_control.py` | 247 | IoT room control |
| `/app/backend/routes/karau_meet.py` | 1227 | Core meeting management |
| `/app/backend/routes/karau_organizations.py` | 963 | Organization management |
| `/app/backend/routes/karau_polls_challenges.py` | 259 | Polls and challenges |
| `/app/backend/routes/karau_qr_entry.py` | 135 | QR code entry |
| `/app/backend/routes/karau_recordings.py` | 315 | Recording management |
| `/app/backend/routes/karau_replay.py` | 582 | Meeting replay |
| `/app/backend/routes/karau_scheduling.py` | 301 | Meeting scheduling |
| `/app/backend/routes/karau_security.py` | 323 | Meeting security |
| `/app/backend/routes/karau_sharing.py` | 115 | Meeting sharing |
| `/app/backend/routes/karau_simulation.py` | 287 | Simulation features |
| `/app/backend/routes/karau_slam_spatial.py` | 284 | SLAM spatial tracking |
| `/app/backend/routes/karau_sso.py` | 339 | Enterprise SSO |
| `/app/backend/routes/karau_webinar.py` | 1077 | Webinar management |
| `/app/backend/routes/karau_webrtc.py` | 137 | WebRTC signaling |
| `/app/backend/routes/karau_webxr.py` | 208 | XR/Vision Pro support |
| `/app/backend/routes/linkedin.py` | 271 | LinkedIn OAuth |
| `/app/backend/routes/lumi_ai.py` | 224 | ENZI AI features |
| `/app/backend/routes/lumi_buckets.py` | 211 | Message buckets |
| `/app/backend/routes/lumi_calendar.py` | 187 | Calendar integration |
| `/app/backend/routes/lumi_files.py` | 139 | File sharing |
| `/app/backend/routes/lumi_messenger.py` | 2466 | Core messenger |
| `/app/backend/routes/lumi_predict.py` | 154 | Behavioral predictions |
| `/app/backend/routes/lumi_templates.py` | 129 | Message templates |
| `/app/backend/routes/meeting_channel_sync.py` | 420 | Meeting-channel sync |
| `/app/backend/routes/meeting_infrastructure.py` | 188 | Meeting infrastructure |
| `/app/backend/routes/meeting_intelligence.py` | 549 | Meeting intelligence |
| `/app/backend/routes/meeting_notes.py` | 605 | Meeting notes |
| `/app/backend/routes/messages.py` | 166 | Legacy messages |
| `/app/backend/routes/ml_data.py` | 266 | ML data pipeline |
| `/app/backend/routes/ml_model.py` | 149 | ML model management |
| `/app/backend/routes/ml_predictor.py` | 172 | ML predictions |
| `/app/backend/routes/mutual_match.py` | 589 | Mutual matching |
| `/app/backend/routes/notifications.py` | 160 | Notifications |
| `/app/backend/routes/orcid_oauth.py` | 429 | ORCID OAuth |
| `/app/backend/routes/payments.py` | 801 | Payment processing |
| `/app/backend/routes/persona_verification.py` | 499 | Persona verification |
| `/app/backend/routes/platform_features.py` | 243 | Platform features |
| `/app/backend/routes/portal_access.py` | 253 | Portal access control |
| `/app/backend/routes/privacy.py` | 687 | Privacy management |
| `/app/backend/routes/production_metrics.py` | 300 | Production metrics |
| `/app/backend/routes/psv.py` | 1105 | Professional source verification |
| `/app/backend/routes/push.py` | 324 | Push notifications |
| `/app/backend/routes/push_notifications.py` | 318 | Push notification management |
| `/app/backend/routes/qa_practice.py` | 708 | QA practice |
| `/app/backend/routes/realtime_stt.py` | 417 | Real-time STT |
| `/app/backend/routes/recruiter.py` | 551 | Recruiter features |
| `/app/backend/routes/recruiter_rbac.py` | 913 | Recruiter RBAC |
| `/app/backend/routes/resume.py` | 355 | Resume management |
| `/app/backend/routes/scheduling.py` | 540 | General scheduling |
| `/app/backend/routes/search_engine.py` | 280 | Semantic search |
| `/app/backend/routes/skills.py` | 1501 | Skill assessments |
| `/app/backend/routes/smart_apply.py` | 298 | Smart Apply |
| `/app/backend/routes/talent_crm.py` | 372 | Talent CRM |
| `/app/backend/routes/talent_tools.py` | 220 | Talent tools |
| `/app/backend/routes/taxonomy.py` | 550 | Career taxonomy |
| `/app/backend/routes/translation.py` | 1957 | Translation management |
| `/app/backend/routes/translation_qa.py` | 990 | Translation QA |
| `/app/backend/routes/tutorials.py` | 988 | Video tutorials |
| `/app/backend/routes/video_analysis.py` | 572 | Video analysis |
| `/app/backend/routes/video_assets.py` | 217 | Video assets |
| `/app/backend/routes/video_interview.py` | 323 | Video interview |
| `/app/backend/routes/video_translation.py` | 294 | Video translation |
| `/app/backend/routes/webpush.py` | 677 | Web push |

### Service Modules (`/app/backend/services/`) — 71 files
| File | Lines | Purpose |
|------|-------|---------|
| `/app/backend/services/__init__.py` | 0 | Package init |
| `/app/backend/services/ai_compliance_service.py` | 585 | AI compliance engine |
| `/app/backend/services/ai_qa/__init__.py` | 86 | AI QA package |
| `/app/backend/services/ai_qa/audit_service.py` | 762 | AI audit service |
| `/app/backend/services/ai_qa/core_service.py` | 612 | AI QA core |
| `/app/backend/services/ai_qa/oversight_service.py` | 471 | AI oversight |
| `/app/backend/services/ai_qa/transparency_service.py` | 400 | AI transparency |
| `/app/backend/services/ai_supervisor.py` | 620 | AI supervisor orchestration |
| `/app/backend/services/ai_translation_generator.py` | 177 | AI translation |
| `/app/backend/services/audit_reports.py` | 996 | Audit report generation |
| `/app/backend/services/capa_service.py` | 635 | CAPA management |
| `/app/backend/services/capa_video_regen.py` | 75 | CAPA video regeneration |
| `/app/backend/services/career_pivot.py` | 441 | Career pivot analysis |
| `/app/backend/services/compliance_alerts.py` | 301 | Compliance alerts |
| `/app/backend/services/credly_service.py` | 317 | Credly badge integration |
| `/app/backend/services/data_integrity_service.py` | 868 | Data integrity |
| `/app/backend/services/did_avatar_service.py` | 471 | D-ID avatar service |
| `/app/backend/services/dragon_scheduler.py` | 1012 | Background job scheduler |
| `/app/backend/services/edge_tts_service.py` | 969 | Text-to-speech |
| `/app/backend/services/email_service.py` | 499 | Email service |
| `/app/backend/services/fresh_video_regen.py` | 329 | Video regeneration |
| `/app/backend/services/geolocation.py` | 461 | Geolocation service |
| `/app/backend/services/global_compliance_service.py` | 859 | Global compliance |
| `/app/backend/services/global_rate_limiter.py` | 379 | Rate limiting |
| `/app/backend/services/gual_integration.py` | 387 | GUAL integration |
| `/app/backend/services/job_liveness.py` | 407 | Job liveness monitoring |
| `/app/backend/services/job_sources.py` | 897 | Job source aggregation |
| `/app/backend/services/karau_meet/__init__.py` | 32 | KARAU meet package |
| `/app/backend/services/karau_meet/accessibility_service.py` | 329 | Accessibility |
| `/app/backend/services/karau_meet/ai_assistant_service.py` | 252 | AI meeting assistant |
| `/app/backend/services/karau_meet/ai_transcription_service.py` | 504 | AI transcription |
| `/app/backend/services/karau_meet/collaboration_service.py` | 429 | Collaboration |
| `/app/backend/services/karau_meet/email_service.py` | 304 | Meeting emails |
| `/app/backend/services/karau_meet/meeting_service.py` | 817 | Meeting management |
| `/app/backend/services/karau_meet/scheduling_service.py` | 445 | Scheduling |
| `/app/backend/services/karau_meet/security_service.py` | 652 | Meeting security |
| `/app/backend/services/karau_meet/translation_service.py` | 101 | Meeting translation |
| `/app/backend/services/karau_meet/turn_service.py` | 83 | TURN server |
| `/app/backend/services/karau_meet/webrtc_signaling.py` | 692 | WebRTC signaling |
| `/app/backend/services/meeting_notes_service.py` | 56 | Meeting notes |
| `/app/backend/services/ml_data_collector.py` | 491 | ML data collection |
| `/app/backend/services/ml_data_generator.py` | 285 | ML data generation |
| `/app/backend/services/ml_issue_predictor.py` | 559 | ML issue prediction |
| `/app/backend/services/ml_model_trainer.py` | 482 | ML model training |
| `/app/backend/services/object_storage.py` | 58 | Object storage |
| `/app/backend/services/pdf_export.py` | 730 | PDF export |
| `/app/backend/services/presentation_service.py` | 94 | Presentation service |
| `/app/backend/services/production_metrics.py` | 477 | Production metrics |
| `/app/backend/services/psv_service.py` | 724 | PSV verification |
| `/app/backend/services/question_bank.py` | 475 | Question bank |
| `/app/backend/services/regen_videos_v2.py` | 189 | Video regen v2 |
| `/app/backend/services/regenerate_regional_tutorials.py` | 176 | Regional tutorials |
| `/app/backend/services/regenerate_videos.py` | 329 | Video regeneration |
| `/app/backend/services/regenerate_with_presenter.py` | 359 | Presenter videos |
| `/app/backend/services/search_engine.py` | 529 | Semantic search |
| `/app/backend/services/smart_notifications.py` | 457 | Smart notifications |
| `/app/backend/services/taxonomy.py` | 571 | Taxonomy engine |
| `/app/backend/services/transcription_service.py` | 109 | Transcription |
| `/app/backend/services/translation_qa.py` | 556 | Translation QA |
| `/app/backend/services/trust_score.py` | 495 | Trust scoring |
| `/app/backend/services/tutorial_subtitles.py` | 1663 | Subtitle generation |
| `/app/backend/services/video_3_tutorials.py` | 210 | Video tutorials v3 |
| `/app/backend/services/video_asset_manager.py` | 597 | Video asset management |
| `/app/backend/services/video_faq.py` | 194 | Video FAQ |
| `/app/backend/services/video_generator.py` | 79 | Video generation |
| `/app/backend/services/video_pip.py` | 257 | Picture-in-picture |
| `/app/backend/services/video_storage.py` | 155 | Video storage |
| `/app/backend/services/video_with_highlights.py` | 397 | Video highlights |
| `/app/backend/services/video_with_screenshots.py` | 237 | Video screenshots |
| `/app/backend/services/video_with_voice.py` | 191 | Video with voice |
| `/app/backend/services/web_job_crawler.py` | 408 | Web job crawler |

### Test Files (`/app/backend/tests/`) — 10 files
| File | Lines | Tests | Gate |
|------|-------|-------|------|
| `/app/backend/tests/test_phase1_functional.py` | 839 | 59 | G1 |
| `/app/backend/tests/test_phase2_reliability.py` | 618 | 31 | G2 |
| `/app/backend/tests/test_phase3_regression.py` | 826 | 41 | G3 |
| `/app/backend/tests/test_phase4_deployment_readiness.py` | 488 | 54 | G4 |
| `/app/backend/tests/test_iteration220_features.py` | 417 | 19 | CI/CD |
| `/app/backend/tests/test_iteration_210.py` | 318 | - | Feature |
| `/app/backend/tests/test_smart_apply_iteration215.py` | 258 | - | Feature |
| `/app/backend/tests/test_smart_apply_iteration214.py` | 207 | - | Feature |
| `/app/backend/tests/test_phases_2_4.py` | 144 | - | Combined |
| `/app/backend/tests/test_passkeys_iteration213.py` | 117 | - | Feature |

### Scripts (`/app/backend/scripts/`) — 4 files
| File | Lines | Purpose |
|------|-------|---------|
| `/app/backend/scripts/seed_data.py` | 334 | Database seeding |
| `/app/backend/scripts/translate_missing_keys.py` | 214 | Translation gap filler |
| `/app/backend/scripts/translate_priority_keys.py` | 373 | Priority translation |
| `/app/backend/scripts/sync_translations.py` | 113 | Translation sync |

### Utilities (`/app/backend/util/` and `/app/backend/utils/`) — 7 files
| File | Lines | Purpose |
|------|-------|---------|
| `/app/backend/utils/__init__.py` | 3 | Package init |
| `/app/backend/utils/config.py` | 45 | Configuration |
| `/app/backend/utils/database.py` | 38 | Database utilities |
| `/app/backend/utils/push_service.py` | 262 | Push notification service |
| `/app/backend/util/batch_translate.py` | 127 | Batch translation |
| `/app/backend/util/propagate_i18n.py` | 49 | i18n propagation |
| `/app/backend/util/retry_translate.py` | 95 | Translation retry |
| `/app/backend/util/translate_locales_v5.py` | 134 | Locale translation v5 |

---

## Markdown Files (44 files)

### Root Documentation
| File | Lines | Purpose |
|------|-------|---------|
| `/app/README.md` | 1 | Project readme |
| `/app/CHANGELOG.md` | 48 | Root changelog |
| `/app/ROADMAP.md` | 24 | Root roadmap |

### Docs Directory (`/app/docs/`)
| File | Lines | Purpose |
|------|-------|---------|
| `/app/docs/DEPLOYMENT_READINESS.md` | 278 | Deployment readiness checklist |
| `/app/docs/DEVELOPMENT_ANALYST_REPORT_22_03_2026.md` | 139 | Development analyst report |
| `/app/docs/GAP_ASSESSMENT.md` | 434 | Competitive gap assessment |
| `/app/docs/PAYPAL_INTEGRATION.md` | 270 | PayPal integration guide |
| `/app/docs/PRODUCTION_LAUNCH_PLAYBOOK.md` | 204 | Production launch playbook |
| `/app/docs/STRIPE_WEBHOOK_GUIDE.md` | 265 | Stripe webhook setup |
| `/app/docs/SYSTEM_REQUIREMENTS_AUDIT.md` | NEW | System requirements (this audit) |
| `/app/docs/TESTING_STRATEGY_RESULTS.md` | 159 | Testing strategy and results |
| `/app/docs/guides/AVATAR_VIDEO_LIBRARY.md` | 183 | Avatar video library |
| `/app/docs/guides/AVATAR_VIDEO_SCRIPTS.md` | 106 | Avatar video scripts |
| `/app/docs/guides/EXPO_BUILD_GUIDE.md` | 150 | Expo mobile build guide |
| `/app/docs/guides/NAVIGATION_GUIDE.md` | 243 | App navigation guide |
| `/app/docs/guides/PENDING_INTEGRATIONS_GUIDE.md` | 502 | Pending integrations |

### Memory & Planning (`/app/memory/`)
| File | Lines | Purpose |
|------|-------|---------|
| `/app/memory/PRD.md` | 72 | Product requirements document |
| `/app/memory/CHANGELOG.md` | 170 | Implementation changelog |
| `/app/memory/ROADMAP.md` | 155 | Implementation roadmap |
| `/app/memory/EXECUTIVE_SUMMARY.md` | 439 | Executive summary |
| `/app/memory/FUNCTIONAL_ASSESSMENT.md` | 221 | Functional assessment |
| `/app/memory/GAP_ASSESSMENT.md` | 92 | Gap assessment |
| `/app/memory/OAUTH_SETUP_GUIDE.md` | 397 | OAuth setup guide |
| `/app/memory/REFACTORING_GUIDE.md` | 198 | Refactoring guide |
| `/app/memory/DEPLOYMENT_RUNBOOK.md` | 154 | Deployment runbook |
| `/app/memory/STRESS_TEST_REPORT.md` | 152 | Stress test report |
| `/app/memory/CAPA-002-video-translation.md` | 154 | CAPA: Video translation |
| `/app/memory/CAPA/CAPA-2026-001-AI-Translation.md` | 232 | CAPA: AI translation |
| `/app/memory/CAPA/CAPA-Tracker.md` | 40 | CAPA tracker |
| `/app/memory/docs/i18n-best-practices.md` | 199 | i18n best practices |
| `/app/memory/docs/live-test-guide.md` | 63 | Live test guide |

### Backend Documentation
| File | Lines | Purpose |
|------|-------|---------|
| `/app/backend/PRODUCTION_CONFIG.md` | 222 | Production configuration |

### Desktop Documentation (`/app/desktop/`)
| File | Lines | Purpose |
|------|-------|---------|
| `/app/desktop/README.md` | 160 | Desktop app readme |
| `/app/desktop/assets/README.md` | 54 | Desktop assets readme |

### Mobile Documentation (`/app/mobile/`)
| File | Lines | Purpose |
|------|-------|---------|
| `/app/mobile/README.md` | 141 | Mobile app readme |
| `/app/mobile/IOS_DEPLOYMENT_GUIDE.md` | 409 | iOS deployment guide |
| `/app/mobile/ios-build-guide.md` | 223 | iOS build guide |
| `/app/mobile/testflight-setup-guide.md` | 352 | TestFlight setup guide |

### Frontend Documentation
| File | Lines | Purpose |
|------|-------|---------|
| `/app/frontend/README.md` | 70 | Frontend readme |

### Test Reports (Markdown)
| File | Lines | Purpose |
|------|-------|---------|
| `/app/test_reports/comprehensive_assessment_feb5_2026.md` | 256 | Comprehensive assessment |
| `/app/test_reports/functional_assessment_report.md` | 225 | Functional assessment |
| `/app/test_result.md` | 102 | Test results summary |

### Other
| File | Lines | Purpose |
|------|-------|---------|
| `/app/image_testing.md` | 16 | Image testing notes |

---

## CI/CD Configuration
| File | Purpose |
|------|---------|
| `/app/.github/workflows/test.yml` | GitHub Actions CI/CD pipeline |

## Environment Configuration
| File | Purpose |
|------|---------|
| `/app/backend/.env` | Backend environment variables (54 keys) |
| `/app/frontend/.env` | Frontend environment variables (7 keys) |
| `/app/backend/requirements.txt` | Python dependencies (212 packages) |
| `/app/frontend/package.json` | Frontend dependencies (59 + 12 dev) |

---

*End of File Inventory*
