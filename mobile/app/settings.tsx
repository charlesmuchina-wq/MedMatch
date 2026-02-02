/**
 * MedMatch Mobile - Settings Screen
 * App settings, preferences, and account management
 */
import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Switch,
  Alert,
  Linking,
  Platform,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../../constants/theme';

// Settings Section Component
const SettingsSection = ({ 
  title, 
  children 
}: { 
  title: string; 
  children: React.ReactNode;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <View style={styles.section}>
      <Text style={[styles.sectionTitle, { color: themeColors.textSecondary }]}>{title}</Text>
      <View style={[styles.sectionContent, { backgroundColor: themeColors.surface }]}>
        {children}
      </View>
    </View>
  );
};

// Settings Row Component
const SettingsRow = ({
  icon,
  title,
  subtitle,
  onPress,
  rightElement,
  destructive = false,
}: {
  icon: string;
  title: string;
  subtitle?: string;
  onPress?: () => void;
  rightElement?: React.ReactNode;
  destructive?: boolean;
}) => {
  const { colors: themeColors } = useTheme();
  
  const content = (
    <View style={styles.row}>
      <View style={[styles.iconContainer, { backgroundColor: destructive ? colors.error + '15' : colors.turquoise + '15' }]}>
        <Text style={styles.icon}>{icon}</Text>
      </View>
      <View style={styles.rowContent}>
        <Text style={[styles.rowTitle, { color: destructive ? colors.error : themeColors.text }]}>{title}</Text>
        {subtitle && <Text style={[styles.rowSubtitle, { color: themeColors.textSecondary }]}>{subtitle}</Text>}
      </View>
      {rightElement || (onPress && <Text style={[styles.chevron, { color: themeColors.textTertiary }]}>›</Text>)}
    </View>
  );
  
  if (onPress) {
    return (
      <TouchableOpacity onPress={onPress} activeOpacity={0.7}>
        {content}
      </TouchableOpacity>
    );
  }
  
  return content;
};

// Language Selector
const LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'en-GB', name: 'English (UK)', flag: '🇬🇧' },
  { code: 'sw', name: 'Swahili', flag: '🇰🇪' },
  { code: 'ha', name: 'Hausa', flag: '🇳🇬' },
  { code: 'yo', name: 'Yoruba', flag: '🇳🇬' },
  { code: 'zu', name: 'Zulu', flag: '🇿🇦' },
  { code: 'am', name: 'Amharic', flag: '🇪🇹' },
  { code: 'ar', name: 'Arabic', flag: '🇸🇦' },
  { code: 'fr', name: 'French', flag: '🇫🇷' },
  { code: 'es', name: 'Spanish', flag: '🇪🇸' },
  { code: 'pt-BR', name: 'Portuguese', flag: '🇧🇷' },
  { code: 'zh', name: 'Chinese', flag: '🇨🇳' },
];

export default function SettingsScreen() {
  const { colors: themeColors, isDark, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  
  const [notifications, setNotifications] = useState(true);
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [jobAlerts, setJobAlerts] = useState(true);
  const [biometricLogin, setBiometricLogin] = useState(false);
  const [language, setLanguage] = useState('en');
  const [showLanguages, setShowLanguages] = useState(false);

  const handleLogout = useCallback(() => {
    Alert.alert(
      'Log Out',
      'Are you sure you want to log out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Log Out', 
          style: 'destructive',
          onPress: async () => {
            await logout();
            router.replace('/login');
          }
        },
      ]
    );
  }, [logout]);

  const handleDeleteAccount = useCallback(() => {
    Alert.alert(
      'Delete Account',
      'This action cannot be undone. All your data will be permanently deleted.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: () => {
            Alert.alert('Account Deletion', 'Please contact support@medmatch.com to delete your account.');
          }
        },
      ]
    );
  }, []);

  const handleExportData = useCallback(() => {
    Alert.alert(
      'Export Data',
      'Your data export will be sent to your registered email address within 24 hours.',
      [{ text: 'OK' }]
    );
  }, []);

  const openURL = useCallback((url: string) => {
    Linking.openURL(url).catch(err => console.error('Failed to open URL:', err));
  }, []);

  const currentLang = LANGUAGES.find(l => l.code === language) || LANGUAGES[0];

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: themeColors.background }]}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      {/* User Header */}
      <View style={[styles.userHeader, { backgroundColor: themeColors.surface }]}>
        <View style={[styles.avatar, { backgroundColor: colors.turquoise + '20' }]}>
          <Text style={styles.avatarText}>{user?.name?.charAt(0) || user?.email?.charAt(0) || '?'}</Text>
        </View>
        <View style={styles.userInfo}>
          <Text style={[styles.userName, { color: themeColors.text }]}>{user?.name || 'User'}</Text>
          <Text style={[styles.userEmail, { color: themeColors.textSecondary }]}>{user?.email}</Text>
          <TouchableOpacity 
            style={[styles.editProfileBtn, { backgroundColor: colors.turquoise + '15' }]}
            onPress={() => router.push('/profile')}
          >
            <Text style={[styles.editProfileText, { color: colors.turquoise }]}>Edit Profile</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Appearance */}
      <SettingsSection title="APPEARANCE">
        <SettingsRow
          icon="🌙"
          title="Dark Mode"
          subtitle={isDark ? "On" : "Off"}
          rightElement={
            <Switch
              value={isDark}
              onValueChange={toggleTheme}
              trackColor={{ false: themeColors.border, true: colors.turquoise + '50' }}
              thumbColor={isDark ? colors.turquoise : '#f4f3f4'}
            />
          }
        />
        <View style={[styles.separator, { backgroundColor: themeColors.border }]} />
        <SettingsRow
          icon="🌍"
          title="Language"
          subtitle={`${currentLang.flag} ${currentLang.name}`}
          onPress={() => setShowLanguages(!showLanguages)}
        />
        {showLanguages && (
          <View style={styles.languageList}>
            {LANGUAGES.map((lang) => (
              <TouchableOpacity
                key={lang.code}
                style={[
                  styles.languageItem,
                  language === lang.code && { backgroundColor: colors.turquoise + '15' }
                ]}
                onPress={() => {
                  setLanguage(lang.code);
                  setShowLanguages(false);
                }}
              >
                <Text style={styles.languageFlag}>{lang.flag}</Text>
                <Text style={[styles.languageName, { color: themeColors.text }]}>{lang.name}</Text>
                {language === lang.code && <Text style={styles.checkmark}>✓</Text>}
              </TouchableOpacity>
            ))}
          </View>
        )}
      </SettingsSection>

      {/* Notifications */}
      <SettingsSection title="NOTIFICATIONS">
        <SettingsRow
          icon="🔔"
          title="Push Notifications"
          subtitle="Get notified about new matches"
          rightElement={
            <Switch
              value={notifications}
              onValueChange={setNotifications}
              trackColor={{ false: themeColors.border, true: colors.turquoise + '50' }}
              thumbColor={notifications ? colors.turquoise : '#f4f3f4'}
            />
          }
        />
        <View style={[styles.separator, { backgroundColor: themeColors.border }]} />
        <SettingsRow
          icon="📧"
          title="Email Alerts"
          subtitle="Weekly digest and updates"
          rightElement={
            <Switch
              value={emailAlerts}
              onValueChange={setEmailAlerts}
              trackColor={{ false: themeColors.border, true: colors.turquoise + '50' }}
              thumbColor={emailAlerts ? colors.turquoise : '#f4f3f4'}
            />
          }
        />
        <View style={[styles.separator, { backgroundColor: themeColors.border }]} />
        <SettingsRow
          icon="💼"
          title="Job Alerts"
          subtitle="New matching jobs"
          rightElement={
            <Switch
              value={jobAlerts}
              onValueChange={setJobAlerts}
              trackColor={{ false: themeColors.border, true: colors.turquoise + '50' }}
              thumbColor={jobAlerts ? colors.turquoise : '#f4f3f4'}
            />
          }
        />
      </SettingsSection>

      {/* Security */}
      <SettingsSection title="SECURITY">
        <SettingsRow
          icon="🔐"
          title="Change Password"
          onPress={() => Alert.alert('Change Password', 'Password change feature coming soon')}
        />
        <View style={[styles.separator, { backgroundColor: themeColors.border }]} />
        <SettingsRow
          icon="👆"
          title="Biometric Login"
          subtitle={Platform.OS === 'ios' ? "Face ID / Touch ID" : "Fingerprint"}
          rightElement={
            <Switch
              value={biometricLogin}
              onValueChange={setBiometricLogin}
              trackColor={{ false: themeColors.border, true: colors.turquoise + '50' }}
              thumbColor={biometricLogin ? colors.turquoise : '#f4f3f4'}
            />
          }
        />
        <View style={[styles.separator, { backgroundColor: themeColors.border }]} />
        <SettingsRow
          icon="🔑"
          title="Two-Factor Authentication"
          subtitle="Add extra security"
          onPress={() => Alert.alert('2FA', 'Two-factor authentication coming soon')}
        />
      </SettingsSection>

      {/* Data & Privacy */}
      <SettingsSection title="DATA & PRIVACY">
        <SettingsRow
          icon="📦"
          title="Export My Data"
          subtitle="Download all your information"
          onPress={handleExportData}
        />
        <View style={[styles.separator, { backgroundColor: themeColors.border }]} />
        <SettingsRow
          icon="📜"
          title="Privacy Policy"
          onPress={() => openURL('https://medmatch.com/privacy')}
        />
        <View style={[styles.separator, { backgroundColor: themeColors.border }]} />
        <SettingsRow
          icon="📋"
          title="Terms of Service"
          onPress={() => openURL('https://medmatch.com/terms')}
        />
      </SettingsSection>

      {/* Support */}
      <SettingsSection title="SUPPORT">
        <SettingsRow
          icon="❓"
          title="Help Center"
          onPress={() => openURL('https://medmatch.com/help')}
        />
        <View style={[styles.separator, { backgroundColor: themeColors.border }]} />
        <SettingsRow
          icon="💬"
          title="Contact Support"
          subtitle="support@medmatch.com"
          onPress={() => openURL('mailto:support@medmatch.com')}
        />
        <View style={[styles.separator, { backgroundColor: themeColors.border }]} />
        <SettingsRow
          icon="⭐"
          title="Rate the App"
          onPress={() => Alert.alert('Rate Us', 'Thank you for your support!')}
        />
      </SettingsSection>

      {/* About */}
      <SettingsSection title="ABOUT">
        <SettingsRow
          icon="ℹ️"
          title="App Version"
          subtitle="1.0.0 (Build 1)"
        />
        <View style={[styles.separator, { backgroundColor: themeColors.border }]} />
        <SettingsRow
          icon="📝"
          title="Changelog"
          onPress={() => Alert.alert('What\'s New', 'Version 1.0.0\n\n• Initial release\n• AI-powered job matching\n• Interview preparation\n• Multi-language support')}
        />
      </SettingsSection>

      {/* Danger Zone */}
      <SettingsSection title="ACCOUNT">
        <SettingsRow
          icon="🚪"
          title="Log Out"
          onPress={handleLogout}
        />
        <View style={[styles.separator, { backgroundColor: themeColors.border }]} />
        <SettingsRow
          icon="🗑️"
          title="Delete Account"
          subtitle="Permanently delete your account"
          onPress={handleDeleteAccount}
          destructive
        />
      </SettingsSection>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={[styles.footerText, { color: themeColors.textTertiary }]}>
          MedMatch © 2026
        </Text>
        <Text style={[styles.footerText, { color: themeColors.textTertiary }]}>
          Made with ❤️ for job seekers
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { paddingBottom: spacing['3xl'] },
  
  userHeader: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    padding: spacing.lg,
    marginBottom: spacing.md,
    ...shadows.sm,
  },
  avatar: { 
    width: 70, 
    height: 70, 
    borderRadius: 35, 
    justifyContent: 'center', 
    alignItems: 'center',
    marginRight: spacing.md,
  },
  avatarText: { fontSize: 28, fontWeight: fontWeight.bold, color: colors.turquoise },
  userInfo: { flex: 1 },
  userName: { fontSize: fontSize.xl, fontWeight: fontWeight.bold },
  userEmail: { fontSize: fontSize.sm, marginTop: 2 },
  editProfileBtn: { 
    alignSelf: 'flex-start', 
    paddingHorizontal: spacing.md, 
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.full,
    marginTop: spacing.sm,
  },
  editProfileText: { fontSize: fontSize.sm, fontWeight: fontWeight.semibold },
  
  section: { marginBottom: spacing.md },
  sectionTitle: { 
    fontSize: fontSize.xs, 
    fontWeight: fontWeight.semibold, 
    marginLeft: spacing.md,
    marginBottom: spacing.xs,
    letterSpacing: 1,
  },
  sectionContent: { 
    borderRadius: borderRadius.lg, 
    marginHorizontal: spacing.md,
    overflow: 'hidden',
    ...shadows.sm,
  },
  
  row: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    padding: spacing.md,
  },
  iconContainer: { 
    width: 36, 
    height: 36, 
    borderRadius: 10, 
    justifyContent: 'center', 
    alignItems: 'center',
    marginRight: spacing.md,
  },
  icon: { fontSize: 18 },
  rowContent: { flex: 1 },
  rowTitle: { fontSize: fontSize.base, fontWeight: fontWeight.medium },
  rowSubtitle: { fontSize: fontSize.sm, marginTop: 2 },
  chevron: { fontSize: 20, fontWeight: fontWeight.bold },
  separator: { height: 1, marginLeft: 60 },
  
  languageList: { paddingHorizontal: spacing.md, paddingBottom: spacing.md },
  languageItem: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.xs,
  },
  languageFlag: { fontSize: 20, marginRight: spacing.sm },
  languageName: { flex: 1, fontSize: fontSize.base },
  checkmark: { fontSize: 16, color: colors.turquoise, fontWeight: fontWeight.bold },
  
  footer: { 
    alignItems: 'center', 
    paddingVertical: spacing.xl,
    paddingHorizontal: spacing.md,
  },
  footerText: { fontSize: fontSize.sm, marginBottom: spacing.xs },
});
