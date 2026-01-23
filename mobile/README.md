# MedMatch Mobile App

Native mobile application for MedMatch job search platform, built with Expo SDK 54 and React Native 0.81.

## Features

- 📱 Cross-platform (iOS, Android, Web)
- 🔐 Secure authentication with biometrics
- 📄 Resume upload and parsing
- 💼 AI-powered job matching
- 🎤 Voice interview practice
- 📹 Video interview with facial analysis
- 🆔 ID verification
- 🔔 Push notifications
- 🌙 Dark mode support

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (Mac) or Android Studio (for emulators)
- Expo Go app (for physical device testing)

### Installation

```bash
# Navigate to mobile directory
cd /app/mobile

# Install dependencies
npm install
# or
yarn install

# Start development server
npm start
# or
expo start
```

### Running on Device

1. **iOS Simulator**: Press `i` in terminal
2. **Android Emulator**: Press `a` in terminal
3. **Physical Device**: Scan QR code with Expo Go app

## Project Structure

```
mobile/
├── app/                    # Expo Router screens
│   ├── (auth)/            # Auth screens (login, register)
│   ├── (tabs)/            # Tab navigation screens
│   ├── job/               # Job detail screens
│   ├── interview/         # Interview practice screens
│   └── _layout.tsx        # Root layout
├── components/            # Reusable components
├── contexts/              # React contexts
│   ├── AuthContext.tsx    # Authentication state
│   ├── ThemeContext.tsx   # Theme/dark mode
│   └── NotificationContext.tsx
├── services/              # API services
│   └── api.ts             # API client
├── assets/                # Images, fonts, etc.
├── app.json              # Expo configuration
└── package.json
```

## API Integration

The mobile app connects to the same backend as the web application. Configure the API URL in `app.json` or via environment variables:

```env
EXPO_PUBLIC_API_URL=https://your-api-url.com
```

## Building for Production

### Using EAS Build

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure build
eas build:configure

# Build for iOS
eas build --platform ios

# Build for Android
eas build --platform android

# Build for both
eas build --platform all
```

### Submitting to Stores

```bash
# Submit to App Store
eas submit --platform ios

# Submit to Play Store
eas submit --platform android
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `EXPO_PUBLIC_API_URL` | Backend API base URL |
| `EXPO_PUBLIC_GOOGLE_CLIENT_ID` | Google OAuth client ID |

## Key Dependencies

- **expo** ~54.0.0 - Expo SDK
- **expo-router** ~4.0.0 - File-based routing
- **react-native** 0.81.0 - React Native framework
- **expo-camera** - Camera access for ID verification
- **expo-av** - Audio/video for interviews
- **expo-notifications** - Push notifications
- **expo-secure-store** - Secure token storage
- **nativewind** - Tailwind CSS for React Native

## Contributing

1. Create a feature branch
2. Make your changes
3. Test on both iOS and Android
4. Submit a pull request

## License

MIT
