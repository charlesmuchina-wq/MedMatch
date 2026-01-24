/**
 * MedMatch Mobile - Theme Constants
 * Batik-inspired theme with turquoise, pink, and red accents
 */

export const colors = {
  // Primary - Turquoise (Batik inspired)
  turquoise: '#20b2aa',
  turquoiseLight: '#40e0d0',
  turquoiseDark: '#008b8b',
  
  // Accent - Pink/Rose
  pink: '#e91e63',
  pinkLight: '#f48fb1',
  pinkDark: '#c2185b',
  rose: '#ec4899',
  
  // Accent - Red/Coral
  red: '#e63946',
  redLight: '#ff6b6b',
  coral: '#ff7f7f',
  
  // Batik Gold
  gold: '#d4af37',
  goldLight: '#ffd700',
  
  // Neutrals
  white: '#ffffff',
  black: '#000000',
  
  // Grays
  gray50: '#f9fafb',
  gray100: '#f3f4f6',
  gray200: '#e5e7eb',
  gray300: '#d1d5db',
  gray400: '#9ca3af',
  gray500: '#6b7280',
  gray600: '#4b5563',
  gray700: '#374151',
  gray800: '#1f2937',
  gray900: '#111827',
  
  // Semantic
  success: '#10b981',
  successLight: '#34d399',
  warning: '#f59e0b',
  warningLight: '#fbbf24',
  error: '#ef4444',
  errorLight: '#f87171',
  info: '#3b82f6',
  infoLight: '#60a5fa',
};

export const lightTheme = {
  background: '#faf9f7',
  surface: '#ffffff',
  surfaceElevated: '#ffffff',
  card: '#ffffff',
  
  primary: colors.turquoise,
  primaryLight: colors.turquoiseLight,
  primaryDark: colors.turquoiseDark,
  
  accent: colors.pink,
  accentLight: colors.pinkLight,
  
  secondary: colors.rose,
  tertiary: colors.coral,
  
  text: '#1a1a2e',
  textSecondary: '#64748b',
  textTertiary: '#94a3b8',
  textInverse: '#ffffff',
  
  border: '#e2e8f0',
  borderLight: '#f1f5f9',
  
  success: colors.success,
  warning: colors.warning,
  error: colors.error,
  info: colors.info,
  
  // Status badge colors
  scheduled: '#3b82f6',
  completed: colors.success,
  cancelled: colors.error,
  pending: colors.warning,
  
  // Gradients (for linear gradient arrays)
  gradientPrimary: [colors.turquoise, colors.turquoiseLight],
  gradientAccent: [colors.pink, colors.rose],
  gradientWarm: [colors.coral, colors.pink],
  gradientDark: ['#1a1a2e', '#2d2d44'],
};

export const darkTheme = {
  background: '#0f0f1a',
  surface: '#1a1a2e',
  surfaceElevated: '#252540',
  card: '#1e1e32',
  
  primary: colors.turquoiseLight,
  primaryLight: colors.turquoise,
  primaryDark: colors.turquoiseDark,
  
  accent: colors.pinkLight,
  accentLight: colors.pink,
  
  secondary: colors.rose,
  tertiary: colors.coral,
  
  text: '#f8fafc',
  textSecondary: '#94a3b8',
  textTertiary: '#64748b',
  textInverse: '#1a1a2e',
  
  border: '#2d2d44',
  borderLight: '#3d3d5c',
  
  success: colors.successLight,
  warning: colors.warningLight,
  error: colors.errorLight,
  info: colors.infoLight,
  
  // Status badge colors
  scheduled: '#60a5fa',
  completed: colors.successLight,
  cancelled: colors.errorLight,
  pending: colors.warningLight,
  
  // Gradients
  gradientPrimary: [colors.turquoise, colors.turquoiseLight],
  gradientAccent: [colors.pink, colors.rose],
  gradientWarm: [colors.coral, colors.pink],
  gradientDark: ['#1a1a2e', '#0f0f1a'],
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64,
};

export const borderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  '2xl': 24,
  full: 9999,
};

export const fontSize = {
  xs: 12,
  sm: 14,
  base: 16,
  lg: 18,
  xl: 20,
  '2xl': 24,
  '3xl': 30,
  '4xl': 36,
};

export const fontWeight = {
  normal: '400' as const,
  medium: '500' as const,
  semibold: '600' as const,
  bold: '700' as const,
};

export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5,
  },
};

export type ThemeColors = typeof lightTheme;
