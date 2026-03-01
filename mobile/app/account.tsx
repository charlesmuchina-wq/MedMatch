/**
 * MedMatch Mobile - Account Management Screen
 * Edit profile information, verify identity, manage credentials
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../constants/theme';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'https://karau-webex-pro.preview.emergentagent.com';

// Input Field Component
const InputField = ({
  label,
  value,
  onChangeText,
  placeholder,
  keyboardType = 'default',
  multiline = false,
  editable = true,
  icon,
}: {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  keyboardType?: 'default' | 'email-address' | 'phone-pad' | 'numeric';
  multiline?: boolean;
  editable?: boolean;
  icon?: string;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <View style={styles.inputContainer}>
      <Text style={[styles.inputLabel, { color: themeColors.textSecondary }]}>{label}</Text>
      <View style={[
        styles.inputWrapper, 
        { 
          backgroundColor: editable ? themeColors.surface : themeColors.surfaceVariant,
          borderColor: themeColors.border,
        }
      ]}>
        {icon && <Text style={styles.inputIcon}>{icon}</Text>}
        <TextInput
          style={[
            styles.input, 
            { color: themeColors.text },
            multiline && { height: 100, textAlignVertical: 'top' }
          ]}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor={themeColors.textTertiary}
          keyboardType={keyboardType}
          multiline={multiline}
          editable={editable}
          autoCapitalize="none"
        />
      </View>
    </View>
  );
};

// Section Header
const SectionHeader = ({ title, icon }: { title: string; icon?: string }) => {
  const { colors: themeColors } = useTheme();
  return (
    <View style={styles.sectionHeader}>
      {icon && <Text style={styles.sectionIcon}>{icon}</Text>}
      <Text style={[styles.sectionTitle, { color: themeColors.text }]}>{title}</Text>
    </View>
  );
};

// Trust Score Badge
const TrustScoreBadge = ({ score, level }: { score: number; level: string }) => {
  const getLevelColor = () => {
    switch (level) {
      case 'Expert': return '#64748B';
      case 'Elite': return '#F59E0B';
      case 'Trusted': return '#8B5CF6';
      case 'Established': return '#10B981';
      case 'Emerging': return '#3B82F6';
      default: return '#6B7280';
    }
  };

  return (
    <View style={[styles.trustBadge, { backgroundColor: getLevelColor() + '15' }]}>
      <Text style={styles.trustIcon}>🛡️</Text>
      <View>
        <Text style={[styles.trustScore, { color: getLevelColor() }]}>{score}</Text>
        <Text style={[styles.trustLevel, { color: getLevelColor() }]}>{level}</Text>
      </View>
    </View>
  );
};

export default function AccountScreen() {
  const { colors: themeColors, isDark } = useTheme();
  const { user, token, updateUser } = useAuth();
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [trustScore, setTrustScore] = useState<{ score: number; level: string } | null>(null);
  
  // Form state
  const [name, setName] = useState(user?.name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [location, setLocation] = useState(user?.location || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [linkedinUrl, setLinkedinUrl] = useState(user?.linkedin_url || '');
  const [jobTitle, setJobTitle] = useState(user?.job_title || '');

  useEffect(() => {
    fetchTrustScore();
  }, []);

  const fetchTrustScore = async () => {
    try {
      const response = await fetch(`${API_URL}/api/credentials/trust-score`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setTrustScore({
          score: data.total_score,
          level: data.level?.name || 'Building'
        });
      }
    } catch (error) {
      console.error('Failed to fetch trust score:', error);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${API_URL}/api/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name,
          phone,
          location,
          bio,
          linkedin_url: linkedinUrl,
          job_title: jobTitle,
        })
      });

      if (response.ok) {
        const updatedUser = await response.json();
        updateUser?.(updatedUser);
        Alert.alert('Success', 'Profile updated successfully');
      } else {
        const error = await response.json();
        Alert.alert('Error', error.detail || 'Failed to update profile');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      'Delete Account',
      'Are you sure you want to permanently delete your account? This action cannot be undone and all your data will be erased.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive', 
          onPress: async () => {
            try {
              const response = await fetch(`${API_URL}/api/privacy/data/delete`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
              });
              if (response.ok) {
                Alert.alert('Account Deleted', 'Your account has been deleted.');
                router.replace('/');
              }
            } catch (error) {
              Alert.alert('Error', 'Failed to delete account');
            }
          }
        },
      ]
    );
  };

  return (
    <KeyboardAvoidingView 
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView 
        style={[styles.container, { backgroundColor: themeColors.background }]}
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        {/* Header */}
        <LinearGradient
          colors={[colors.turquoise, colors.turquoiseLight]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.header}
        >
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Text style={styles.backIcon}>←</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Account Settings</Text>
          <View style={styles.headerPlaceholder} />
        </LinearGradient>

        {/* Trust Score */}
        {trustScore && (
          <View style={styles.trustContainer}>
            <TrustScoreBadge score={trustScore.score} level={trustScore.level} />
            <TouchableOpacity 
              style={styles.credentialsLink}
              onPress={() => router.push('/credentials')}
            >
              <Text style={[styles.credentialsText, { color: colors.turquoise }]}>
                Manage Credentials →
              </Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Personal Information */}
        <View style={[styles.section, { backgroundColor: themeColors.surface }]}>
          <SectionHeader title="Personal Information" icon="👤" />
          
          <InputField
            label="Full Name"
            value={name}
            onChangeText={setName}
            placeholder="Enter your full name"
            icon="📝"
          />
          
          <InputField
            label="Email"
            value={user?.email || ''}
            onChangeText={() => {}}
            editable={false}
            icon="✉️"
          />
          
          <InputField
            label="Phone Number"
            value={phone}
            onChangeText={setPhone}
            placeholder="+1 (555) 123-4567"
            keyboardType="phone-pad"
            icon="📱"
          />
          
          <InputField
            label="Location"
            value={location}
            onChangeText={setLocation}
            placeholder="City, Country"
            icon="📍"
          />
        </View>

        {/* Professional Information */}
        <View style={[styles.section, { backgroundColor: themeColors.surface }]}>
          <SectionHeader title="Professional Information" icon="💼" />
          
          <InputField
            label="Job Title"
            value={jobTitle}
            onChangeText={setJobTitle}
            placeholder="e.g., Senior Software Engineer"
            icon="🏷️"
          />
          
          <InputField
            label="LinkedIn URL"
            value={linkedinUrl}
            onChangeText={setLinkedinUrl}
            placeholder="https://linkedin.com/in/yourprofile"
            keyboardType="default"
            icon="🔗"
          />
          
          <InputField
            label="Bio"
            value={bio}
            onChangeText={setBio}
            placeholder="Tell us about yourself..."
            multiline
            icon="📄"
          />
        </View>

        {/* Quick Actions */}
        <View style={[styles.section, { backgroundColor: themeColors.surface }]}>
          <SectionHeader title="Quick Actions" icon="⚡" />
          
          <TouchableOpacity 
            style={[styles.actionButton, { borderColor: themeColors.border }]}
            onPress={() => router.push('/credentials')}
          >
            <Text style={styles.actionIcon}>🏆</Text>
            <View style={styles.actionContent}>
              <Text style={[styles.actionTitle, { color: themeColors.text }]}>Manage Credentials</Text>
              <Text style={[styles.actionSubtitle, { color: themeColors.textSecondary }]}>
                Import badges, verify certifications
              </Text>
            </View>
            <Text style={[styles.chevron, { color: themeColors.textTertiary }]}>›</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.actionButton, { borderColor: themeColors.border }]}
            onPress={() => Alert.alert('Coming Soon', 'Resume upload will be available soon')}
          >
            <Text style={styles.actionIcon}>📄</Text>
            <View style={styles.actionContent}>
              <Text style={[styles.actionTitle, { color: themeColors.text }]}>Upload Resume</Text>
              <Text style={[styles.actionSubtitle, { color: themeColors.textSecondary }]}>
                Get AI-powered job matches
              </Text>
            </View>
            <Text style={[styles.chevron, { color: themeColors.textTertiary }]}>›</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.actionButton, { borderColor: themeColors.border }]}
            onPress={() => router.push('/settings')}
          >
            <Text style={styles.actionIcon}>⚙️</Text>
            <View style={styles.actionContent}>
              <Text style={[styles.actionTitle, { color: themeColors.text }]}>App Settings</Text>
              <Text style={[styles.actionSubtitle, { color: themeColors.textSecondary }]}>
                Notifications, language, privacy
              </Text>
            </View>
            <Text style={[styles.chevron, { color: themeColors.textTertiary }]}>›</Text>
          </TouchableOpacity>
        </View>

        {/* Save Button */}
        <TouchableOpacity
          style={[styles.saveButton, saving && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={saving}
        >
          <LinearGradient
            colors={[colors.turquoise, colors.turquoiseLight]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.saveButtonGradient}
          >
            {saving ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.saveButtonText}>Save Changes</Text>
            )}
          </LinearGradient>
        </TouchableOpacity>

        {/* Danger Zone */}
        <View style={[styles.dangerSection, { backgroundColor: colors.error + '10' }]}>
          <SectionHeader title="Danger Zone" icon="⚠️" />
          <TouchableOpacity 
            style={[styles.dangerButton, { borderColor: colors.error }]}
            onPress={handleDeleteAccount}
          >
            <Text style={styles.dangerIcon}>🗑️</Text>
            <Text style={[styles.dangerText, { color: colors.error }]}>Delete Account</Text>
          </TouchableOpacity>
          <Text style={[styles.dangerNote, { color: themeColors.textTertiary }]}>
            This will permanently delete all your data including resume, applications, and credentials.
          </Text>
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { paddingBottom: spacing.xl },
  
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 60,
    paddingBottom: spacing.lg,
    paddingHorizontal: spacing.md,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  backIcon: { fontSize: 20, color: '#fff' },
  headerTitle: { fontSize: fontSize.lg, fontWeight: fontWeight.bold, color: '#fff' },
  headerPlaceholder: { width: 40 },

  trustContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
  },
  trustBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    gap: spacing.sm,
  },
  trustIcon: { fontSize: 24 },
  trustScore: { fontSize: fontSize.xl, fontWeight: fontWeight.bold },
  trustLevel: { fontSize: fontSize.xs, fontWeight: fontWeight.medium },
  credentialsLink: { paddingHorizontal: spacing.md },
  credentialsText: { fontSize: fontSize.sm, fontWeight: fontWeight.semibold },

  section: {
    marginHorizontal: spacing.md,
    marginTop: spacing.md,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    ...shadows.sm,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
    gap: spacing.sm,
  },
  sectionIcon: { fontSize: 20 },
  sectionTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold },

  inputContainer: { marginBottom: spacing.md },
  inputLabel: { fontSize: fontSize.sm, marginBottom: spacing.xs, fontWeight: fontWeight.medium },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.sm,
  },
  inputIcon: { fontSize: 16, marginRight: spacing.sm },
  input: { flex: 1, paddingVertical: spacing.sm, fontSize: fontSize.base },

  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
  },
  actionIcon: { fontSize: 24, marginRight: spacing.md },
  actionContent: { flex: 1 },
  actionTitle: { fontSize: fontSize.base, fontWeight: fontWeight.medium },
  actionSubtitle: { fontSize: fontSize.sm, marginTop: 2 },
  chevron: { fontSize: 20, fontWeight: fontWeight.bold },

  saveButton: { marginHorizontal: spacing.md, marginTop: spacing.lg },
  saveButtonDisabled: { opacity: 0.7 },
  saveButtonGradient: {
    paddingVertical: spacing.md,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
  },
  saveButtonText: { color: '#fff', fontSize: fontSize.base, fontWeight: fontWeight.semibold },

  dangerSection: {
    marginHorizontal: spacing.md,
    marginTop: spacing.xl,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
  },
  dangerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.md,
    borderWidth: 1,
    borderRadius: borderRadius.md,
    gap: spacing.sm,
  },
  dangerIcon: { fontSize: 18 },
  dangerText: { fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  dangerNote: { fontSize: fontSize.xs, textAlign: 'center', marginTop: spacing.sm },
});
