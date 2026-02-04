/**
 * MedMatch Mobile - Profile Screen
 * User profile, settings, and resume management
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../../constants/theme';

// Menu Item Component
const MenuItem = ({
  icon,
  title,
  subtitle,
  onPress,
  showChevron = true,
  rightElement,
}: {
  icon: string;
  title: string;
  subtitle?: string;
  onPress?: () => void;
  showChevron?: boolean;
  rightElement?: React.ReactNode;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <TouchableOpacity
      style={[styles.menuItem, { backgroundColor: themeColors.surface }]}
      onPress={onPress}
      disabled={!onPress}
      activeOpacity={0.7}
    >
      <View style={[styles.menuIcon, { backgroundColor: colors.turquoise + '15' }]}>
        <Text style={styles.menuIconText}>{icon}</Text>
      </View>
      <View style={styles.menuContent}>
        <Text style={[styles.menuTitle, { color: themeColors.text }]}>{title}</Text>
        {subtitle && <Text style={[styles.menuSubtitle, { color: themeColors.textSecondary }]}>{subtitle}</Text>}
      </View>
      {rightElement || (showChevron && <Text style={[styles.chevron, { color: themeColors.textTertiary }]}>›</Text>)}
    </TouchableOpacity>
  );
};

// Section Header
const SectionHeader = ({ title }: { title: string }) => {
  const { colors: themeColors } = useTheme();
  return <Text style={[styles.sectionHeader, { color: themeColors.textSecondary }]}>{title}</Text>;
};

export default function ProfileScreen() {
  const { colors: themeColors, isDark, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', style: 'destructive', onPress: logout },
      ]
    );
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: themeColors.background }]} contentContainerStyle={styles.content}>
      {/* Profile Header */}
      <LinearGradient
        colors={[colors.turquoise, colors.turquoiseLight]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.profileHeader}
      >
        <View style={styles.batikOverlay}>
          <View style={[styles.batikCircle, { top: -20, right: 20, backgroundColor: colors.pinkLight + '20' }]} />
          <View style={[styles.batikCircle, { bottom: -30, left: 40, backgroundColor: colors.coral + '15' }]} />
        </View>
        
        <View style={styles.avatarContainer}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>{user?.name?.charAt(0) || '?'}</Text>
          </View>
          {user?.id_verified && (
            <View style={styles.verifiedBadge}>
              <Text style={styles.verifiedIcon}>✓</Text>
            </View>
          )}
        </View>
        
        <Text style={styles.userName}>{user?.name || 'Guest User'}</Text>
        <Text style={styles.userEmail}>{user?.email || 'Not signed in'}</Text>
        
        <View style={[styles.membershipBadge, { backgroundColor: colors.white + '20' }]}>
          <Text style={styles.membershipIcon}>👑</Text>
          <Text style={styles.membershipText}>Premium Member</Text>
        </View>
      </LinearGradient>

      {/* Resume Section */}
      <SectionHeader title="Resume & Profile" />
      <View style={styles.menuGroup}>
        <MenuItem icon="📄" title="My Resume" subtitle="View and edit your resume" onPress={() => {}} />
        <MenuItem icon="⬆️" title="Upload Resume" subtitle="PDF, DOC, DOCX" onPress={() => {}} />
        <MenuItem icon="🎯" title="Skills" subtitle="Manage your skills" onPress={() => {}} />
      </View>

      {/* Account Section */}
      <SectionHeader title="Account" />
      <View style={styles.menuGroup}>
        <MenuItem icon="👤" title="Account Settings" subtitle="Profile, name, contact info" onPress={() => router.push('/account' as any)} />
        <MenuItem icon="🏆" title="Credentials & Badges" subtitle="Verify certifications, import badges" onPress={() => router.push('/credentials' as any)} />
        <MenuItem icon="🔒" title="Security" subtitle="Password, biometric login" onPress={() => {}} />
        <MenuItem icon="✓" title="ID Verification" subtitle={user?.id_verified ? 'Verified' : 'Not verified'} onPress={() => router.push('/id-verification' as any)} />
        <MenuItem icon="💳" title="Subscription" subtitle="Premium • Active" onPress={() => {}} />
      </View>

      {/* Preferences Section */}
      <SectionHeader title="Preferences" />
      <View style={styles.menuGroup}>
        <MenuItem
          icon="🌙"
          title="Dark Mode"
          subtitle={isDark ? 'On' : 'Off'}
          showChevron={false}
          rightElement={
            <Switch
              value={isDark}
              onValueChange={toggleTheme}
              trackColor={{ false: themeColors.border, true: colors.turquoise + '60' }}
              thumbColor={isDark ? colors.turquoise : themeColors.textTertiary}
            />
          }
        />
        <MenuItem
          icon="🔔"
          title="Notifications"
          subtitle={notificationsEnabled ? 'On' : 'Off'}
          showChevron={false}
          rightElement={
            <Switch
              value={notificationsEnabled}
              onValueChange={setNotificationsEnabled}
              trackColor={{ false: themeColors.border, true: colors.turquoise + '60' }}
              thumbColor={notificationsEnabled ? colors.turquoise : themeColors.textTertiary}
            />
          }
        />
        <MenuItem icon="🌐" title="Language" subtitle="English" onPress={() => router.push('/settings' as any)} />
        <MenuItem icon="⚙️" title="All Settings" subtitle="View all preferences" onPress={() => router.push('/settings' as any)} />
      </View>

      {/* Support Section */}
      <SectionHeader title="Support" />
      <View style={styles.menuGroup}>
        <MenuItem icon="❓" title="Help Center" subtitle="FAQs and guides" onPress={() => {}} />
        <MenuItem icon="💬" title="Contact Support" subtitle="Chat with us" onPress={() => {}} />
        <MenuItem icon="📋" title="Terms of Service" onPress={() => {}} />
        <MenuItem icon="🔐" title="Privacy Policy" onPress={() => {}} />
      </View>

      {/* Logout */}
      <TouchableOpacity style={[styles.logoutButton, { borderColor: colors.red }]} onPress={handleLogout}>
        <Text style={[styles.logoutText, { color: colors.red }]}>🚪 Logout</Text>
      </TouchableOpacity>

      {/* Version */}
      <Text style={[styles.versionText, { color: themeColors.textTertiary }]}>
        MedMatch v1.0.0 • Made with ❤️
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { paddingBottom: spacing['2xl'] },
  profileHeader: { padding: spacing.lg, alignItems: 'center', marginBottom: spacing.md, overflow: 'hidden' },
  batikOverlay: { ...StyleSheet.absoluteFillObject },
  batikCircle: { position: 'absolute', width: 80, height: 80, borderRadius: 40 },
  avatarContainer: { position: 'relative', marginBottom: spacing.sm },
  avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: colors.white, justifyContent: 'center', alignItems: 'center' },
  avatarText: { fontSize: fontSize['3xl'], fontWeight: fontWeight.bold, color: colors.turquoise },
  verifiedBadge: { position: 'absolute', bottom: 0, right: 0, width: 24, height: 24, borderRadius: 12, backgroundColor: colors.turquoise, justifyContent: 'center', alignItems: 'center', borderWidth: 2, borderColor: colors.white },
  verifiedIcon: { color: colors.white, fontSize: 14, fontWeight: fontWeight.bold },
  userName: { fontSize: fontSize.xl, fontWeight: fontWeight.bold, color: colors.white, marginBottom: 2 },
  userEmail: { fontSize: fontSize.sm, color: colors.white + 'cc', marginBottom: spacing.md },
  membershipBadge: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: spacing.md, paddingVertical: spacing.xs, borderRadius: borderRadius.full },
  membershipIcon: { fontSize: 14, marginRight: spacing.xs },
  membershipText: { fontSize: fontSize.sm, color: colors.white, fontWeight: fontWeight.medium },
  sectionHeader: { fontSize: fontSize.sm, fontWeight: fontWeight.semibold, textTransform: 'uppercase', letterSpacing: 0.5, marginHorizontal: spacing.md, marginTop: spacing.lg, marginBottom: spacing.sm },
  menuGroup: { marginHorizontal: spacing.md, borderRadius: borderRadius.lg, overflow: 'hidden', ...shadows.sm },
  menuItem: { flexDirection: 'row', alignItems: 'center', padding: spacing.md, borderBottomWidth: 0.5, borderBottomColor: 'rgba(0,0,0,0.05)' },
  menuIcon: { width: 40, height: 40, borderRadius: borderRadius.md, justifyContent: 'center', alignItems: 'center', marginRight: spacing.md },
  menuIconText: { fontSize: 18 },
  menuContent: { flex: 1 },
  menuTitle: { fontSize: fontSize.base, fontWeight: fontWeight.medium },
  menuSubtitle: { fontSize: fontSize.sm, marginTop: 2 },
  chevron: { fontSize: 24 },
  logoutButton: { marginHorizontal: spacing.md, marginTop: spacing.xl, padding: spacing.md, borderRadius: borderRadius.lg, borderWidth: 1, alignItems: 'center' },
  logoutText: { fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  versionText: { textAlign: 'center', fontSize: fontSize.sm, marginTop: spacing.lg },
});
