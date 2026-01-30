# Changelog

All notable changes to MedMatch will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-30

### Added

#### Core Features
- **Resume Parser**: AI-powered PDF/DOC/DOCX resume parsing
- **Job Search**: Multi-source job aggregation (JobSpy, Google CSE)
- **Authentication**: Email, Google OAuth, Apple Sign-In, Biometric (WebAuthn)
- **Stripe Integration**: Membership tiers and payment processing

#### AI Features
- **KARAU DRAGON AI**: Intelligent job search assistant
- **AI Cover Letter Generator**: Personalized cover letters
- **Interview Preparation**: AI-powered mock interviews
- **Voice Coaching**: Real-time voice analysis and feedback
- **Video Interview Practice**: TensorFlow.js facial expression analysis
- **Real-time Transcription**: WebSocket-based Whisper transcription

#### Admin & Monitoring
- **Admin Dashboard**: Centralized admin controls
- **ML Issue Predictor**: Rule-based + scikit-learn ensemble model
- **Auto-Rollback System**: Automatic system recovery
- **Admin Audit Logging**: Security and compliance tracking
- **ML Training Data Collection**: Event logging for model improvement
- **Production Metrics**: User engagement, business, and AI usage tracking

#### Desktop Application
- **Cross-platform**: Windows, macOS, Linux support
- **Auto-updates**: GitHub Releases integration
- **System Tray**: Quick access to key features
- **Offline Detection**: Graceful offline handling
- **Deep Linking**: `medmatch://` protocol support

#### Mobile Support
- **Expo Push Notifications**: iOS and Android push support
- **React Native**: Expo SDK 54 mobile app structure

### Security
- WebAuthn/FIDO2 biometric authentication
- Rate limiting with adaptive thresholds
- Role-based access control (RBAC)
- Admin action audit trail

### Performance
- Response caching
- Database index optimization
- Auto-scaling resource management
- Weekly automated maintenance

---

## [Unreleased]

### Planned
- APScheduler persistence with MongoDB
- Enhanced TensorFlow.js neural network model
- Comprehensive mobile app UI
- Production VAPID key management
