/**
 * MedMatch Mobile - Credentials Management Screen
 * View and manage verified credentials, Credly badges, PSV certifications
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Image,
  Alert,
  Linking,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../constants/theme';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'https://medmatch-staging.preview.emergentagent.com';

// Trust Score Component
const TrustScoreCard = ({ scoreData }: { scoreData: any }) => {
  const { colors: themeColors } = useTheme();
  
  const getLevelColor = (level: string) => {
    switch (level) {
      case 'Expert': return '#64748B';
      case 'Elite': return '#F59E0B';
      case 'Trusted': return '#8B5CF6';
      case 'Established': return '#10B981';
      case 'Emerging': return '#3B82F6';
      default: return '#6B7280';
    }
  };

  const levelColor = getLevelColor(scoreData?.level?.name);

  return (
    <LinearGradient
      colors={[levelColor, levelColor + 'DD']}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.trustCard}
    >
      <View style={styles.trustHeader}>
        <Text style={styles.trustIcon}>🛡️</Text>
        <View>
          <Text style={styles.trustLabel}>Trust Score</Text>
          <View style={styles.trustScoreRow}>
            <Text style={styles.trustScoreValue}>{scoreData?.total_score || 0}</Text>
            <Text style={styles.trustScoreMax}>/ {scoreData?.max_score || 440}</Text>
          </View>
        </View>
      </View>
      
      <View style={styles.trustLevelBadge}>
        <Text style={styles.trustLevelText}>{scoreData?.level?.name || 'Building'}</Text>
      </View>
      
      <Text style={styles.trustDescription}>{scoreData?.level?.description || 'Keep building your profile'}</Text>
      
      {scoreData?.next_level && (
        <View style={styles.nextLevelContainer}>
          <Text style={styles.nextLevelText}>
            {scoreData.next_level.points_needed} points to {scoreData.next_level.name}
          </Text>
          <View style={styles.progressBar}>
            <View style={[styles.progressFill, { width: `${scoreData?.percentage || 0}%` }]} />
          </View>
        </View>
      )}
    </LinearGradient>
  );
};

// Credential Card Component
const CredentialCard = ({ credential, onPress }: { credential: any; onPress?: () => void }) => {
  const { colors: themeColors } = useTheme();
  const isCredly = credential.source === 'credly';
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified': return colors.success;
      case 'pending': return colors.warning;
      case 'rejected': return colors.error;
      default: return themeColors.textTertiary;
    }
  };

  return (
    <TouchableOpacity 
      style={[styles.credentialCard, { backgroundColor: themeColors.surface }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.credentialHeader}>
        {credential.badge_image_url ? (
          <Image 
            source={{ uri: credential.badge_image_url }}
            style={styles.badgeImage}
            resizeMode="contain"
          />
        ) : (
          <View style={[styles.badgePlaceholder, { backgroundColor: colors.turquoise + '15' }]}>
            <Text style={styles.badgePlaceholderIcon}>🏆</Text>
          </View>
        )}
        
        <View style={styles.credentialInfo}>
          <Text style={[styles.credentialName, { color: themeColors.text }]} numberOfLines={2}>
            {credential.credential_name || credential.credential_code}
          </Text>
          <Text style={[styles.credentialIssuer, { color: themeColors.textSecondary }]} numberOfLines={1}>
            {credential.issuing_authority || credential.provider}
          </Text>
        </View>
        
        <View style={styles.credentialStatus}>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(credential.status) + '20' }]}>
            <View style={[styles.statusDot, { backgroundColor: getStatusColor(credential.status) }]} />
            <Text style={[styles.statusText, { color: getStatusColor(credential.status) }]}>
              {credential.status}
            </Text>
          </View>
          {isCredly && (
            <View style={[styles.sourceBadge, { backgroundColor: '#F97316' + '20' }]}>
              <Text style={styles.sourceText}>Credly</Text>
            </View>
          )}
        </View>
      </View>
      
      {/* Skills Tags */}
      {credential.skills?.length > 0 && (
        <View style={styles.skillsContainer}>
          {credential.skills.slice(0, 3).map((skill: string, idx: number) => (
            <View key={idx} style={[styles.skillTag, { backgroundColor: themeColors.surfaceVariant }]}>
              <Text style={[styles.skillText, { color: themeColors.textSecondary }]}>{skill}</Text>
            </View>
          ))}
          {credential.skills.length > 3 && (
            <Text style={[styles.moreSkills, { color: themeColors.textTertiary }]}>
              +{credential.skills.length - 3}
            </Text>
          )}
        </View>
      )}
      
      {/* Dates */}
      <View style={styles.datesContainer}>
        {credential.issue_date && (
          <Text style={[styles.dateText, { color: themeColors.textTertiary }]}>
            Issued: {new Date(credential.issue_date).toLocaleDateString()}
          </Text>
        )}
        {credential.expiry_date && (
          <Text style={[styles.dateText, { color: themeColors.textTertiary }]}>
            Expires: {new Date(credential.expiry_date).toLocaleDateString()}
          </Text>
        )}
      </View>
    </TouchableOpacity>
  );
};

// Credly Connect Button
const CredlyConnectButton = ({ 
  connected, 
  onConnect, 
  onSync, 
  loading 
}: { 
  connected: boolean; 
  onConnect: () => void; 
  onSync: () => void;
  loading: boolean;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <View style={[styles.credlySection, { backgroundColor: '#FFF7ED' }]}>
      <View style={styles.credlyHeader}>
        <View style={styles.credlyLogo}>
          <Text style={styles.credlyLogoText}>🏅</Text>
        </View>
        <View style={styles.credlyInfo}>
          <Text style={styles.credlyTitle}>Credly Digital Badges</Text>
          <Text style={styles.credlySubtitle}>
            {connected ? 'Connected • Import your verified badges' : 'Import badges from AWS, Microsoft, Google & more'}
          </Text>
        </View>
      </View>
      
      {connected ? (
        <TouchableOpacity 
          style={[styles.syncButton, loading && styles.buttonDisabled]}
          onPress={onSync}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator size="small" color="#F97316" />
          ) : (
            <>
              <Text style={styles.syncIcon}>🔄</Text>
              <Text style={styles.syncText}>Sync Badges</Text>
            </>
          )}
        </TouchableOpacity>
      ) : (
        <TouchableOpacity 
          style={[styles.connectButton, loading && styles.buttonDisabled]}
          onPress={onConnect}
          disabled={loading}
        >
          <LinearGradient
            colors={['#F97316', '#FB923C']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.connectGradient}
          >
            {loading ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <Text style={styles.connectText}>Connect Credly</Text>
            )}
          </LinearGradient>
        </TouchableOpacity>
      )}
      
      {!connected && (
        <View style={styles.issuersContainer}>
          <Text style={styles.issuersLabel}>Supported: </Text>
          {['AWS', 'Microsoft', 'Google', 'Cisco', 'PMI'].map((issuer, idx) => (
            <View key={idx} style={styles.issuerBadge}>
              <Text style={styles.issuerText}>{issuer}</Text>
            </View>
          ))}
          <Text style={styles.issuersMore}>+50</Text>
        </View>
      )}
    </View>
  );
};

export default function CredentialsScreen() {
  const { colors: themeColors } = useTheme();
  const { token } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [credentials, setCredentials] = useState<any[]>([]);
  const [trustScore, setTrustScore] = useState<any>(null);
  const [credlyStatus, setCredlyStatus] = useState<{ connected: boolean } | null>(null);
  const [connecting, setConnecting] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      
      const [credsRes, scoreRes, credlyRes] = await Promise.all([
        fetch(`${API_URL}/api/credentials/my-credentials`, { headers }),
        fetch(`${API_URL}/api/credentials/trust-score`, { headers }),
        fetch(`${API_URL}/api/credentials/credly/status`, { headers }),
      ]);
      
      if (credsRes.ok) {
        const data = await credsRes.json();
        setCredentials(data.credentials || []);
      }
      
      if (scoreRes.ok) {
        const data = await scoreRes.json();
        setTrustScore(data);
      }
      
      if (credlyRes.ok) {
        const data = await credlyRes.json();
        setCredlyStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch credentials:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleConnectCredly = async () => {
    setConnecting(true);
    try {
      const response = await fetch(`${API_URL}/api/credentials/credly/auth`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      
      if (data.auth_url) {
        // Demo mode
        if (data.auth_url.includes('DEMO_CLIENT')) {
          const callbackRes = await fetch(
            `${API_URL}/api/credentials/credly/callback?code=demo_code&state=${data.state}`,
            { headers: { 'Authorization': `Bearer ${token}` } }
          );
          const callbackData = await callbackRes.json();
          
          if (callbackData.success) {
            Alert.alert('Success', `Imported ${callbackData.imported_count} badges!`);
            fetchData();
          }
        } else {
          // Production: open browser
          Linking.openURL(data.auth_url);
        }
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to connect to Credly');
    } finally {
      setConnecting(false);
    }
  };

  const handleSyncCredly = async () => {
    setConnecting(true);
    try {
      const response = await fetch(`${API_URL}/api/credentials/credly/sync`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      
      if (data.success) {
        Alert.alert('Success', data.message);
        fetchData();
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to sync badges');
    } finally {
      setConnecting(false);
    }
  };

  const handleCredentialPress = (credential: any) => {
    if (credential.badge_url) {
      Alert.alert(
        credential.credential_name,
        `Issuer: ${credential.issuing_authority}\nStatus: ${credential.status}`,
        [
          { text: 'Close', style: 'cancel' },
          { text: 'View Badge', onPress: () => Linking.openURL(credential.badge_url) },
        ]
      );
    } else {
      Alert.alert(
        credential.credential_name,
        `Issuer: ${credential.issuing_authority}\nStatus: ${credential.status}`
      );
    }
  };

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: themeColors.background }]}>
        <ActivityIndicator size="large" color={colors.turquoise} />
        <Text style={[styles.loadingText, { color: themeColors.textSecondary }]}>Loading credentials...</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: themeColors.background }]}>
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
        <Text style={styles.headerTitle}>My Credentials</Text>
        <View style={styles.headerPlaceholder} />
      </LinearGradient>

      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.turquoise} />
        }
      >
        {/* Trust Score */}
        {trustScore && <TrustScoreCard scoreData={trustScore} />}

        {/* Credly Section */}
        <CredlyConnectButton
          connected={credlyStatus?.connected || false}
          onConnect={handleConnectCredly}
          onSync={handleSyncCredly}
          loading={connecting}
        />

        {/* Credentials List */}
        <View style={styles.credentialsSection}>
          <View style={styles.sectionHeader}>
            <Text style={[styles.sectionTitle, { color: themeColors.text }]}>
              Your Credentials ({credentials.length})
            </Text>
          </View>
          
          {credentials.length > 0 ? (
            credentials.map((cred, idx) => (
              <CredentialCard 
                key={cred.id || idx} 
                credential={cred}
                onPress={() => handleCredentialPress(cred)}
              />
            ))
          ) : (
            <View style={[styles.emptyState, { backgroundColor: themeColors.surface }]}>
              <Text style={styles.emptyIcon}>🏆</Text>
              <Text style={[styles.emptyTitle, { color: themeColors.text }]}>No credentials yet</Text>
              <Text style={[styles.emptySubtitle, { color: themeColors.textSecondary }]}>
                Connect Credly or add credentials manually to build your profile
              </Text>
            </View>
          )}
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: spacing.md, fontSize: fontSize.sm },
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

  // Trust Score Card
  trustCard: {
    margin: spacing.md,
    padding: spacing.lg,
    borderRadius: borderRadius.xl,
    ...shadows.md,
  },
  trustHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.md },
  trustIcon: { fontSize: 40 },
  trustLabel: { fontSize: fontSize.sm, color: 'rgba(255,255,255,0.8)' },
  trustScoreRow: { flexDirection: 'row', alignItems: 'baseline' },
  trustScoreValue: { fontSize: 36, fontWeight: fontWeight.bold, color: '#fff' },
  trustScoreMax: { fontSize: fontSize.base, color: 'rgba(255,255,255,0.7)', marginLeft: 4 },
  trustLevelBadge: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.full,
    marginTop: spacing.sm,
  },
  trustLevelText: { color: '#fff', fontWeight: fontWeight.semibold, fontSize: fontSize.sm },
  trustDescription: { color: 'rgba(255,255,255,0.8)', fontSize: fontSize.sm, marginTop: spacing.sm },
  nextLevelContainer: { marginTop: spacing.md },
  nextLevelText: { color: 'rgba(255,255,255,0.8)', fontSize: fontSize.xs, marginBottom: spacing.xs },
  progressBar: { height: 6, backgroundColor: 'rgba(255,255,255,0.3)', borderRadius: 3 },
  progressFill: { height: '100%', backgroundColor: '#fff', borderRadius: 3 },

  // Credly Section
  credlySection: {
    marginHorizontal: spacing.md,
    marginTop: spacing.sm,
    padding: spacing.md,
    borderRadius: borderRadius.lg,
  },
  credlyHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.md },
  credlyLogo: {
    width: 48,
    height: 48,
    borderRadius: 12,
    backgroundColor: '#F97316',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.md,
  },
  credlyLogoText: { fontSize: 24 },
  credlyInfo: { flex: 1 },
  credlyTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, color: '#1F2937' },
  credlySubtitle: { fontSize: fontSize.sm, color: '#6B7280', marginTop: 2 },
  connectButton: { borderRadius: borderRadius.md, overflow: 'hidden' },
  connectGradient: { paddingVertical: spacing.sm, alignItems: 'center' },
  connectText: { color: '#fff', fontWeight: fontWeight.semibold, fontSize: fontSize.sm },
  syncButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.sm,
    backgroundColor: '#F97316' + '15',
    borderRadius: borderRadius.md,
    gap: spacing.xs,
  },
  syncIcon: { fontSize: 16 },
  syncText: { color: '#F97316', fontWeight: fontWeight.semibold, fontSize: fontSize.sm },
  buttonDisabled: { opacity: 0.6 },
  issuersContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    marginTop: spacing.md,
    gap: spacing.xs,
  },
  issuersLabel: { fontSize: fontSize.xs, color: '#6B7280' },
  issuerBadge: {
    backgroundColor: '#fff',
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
  },
  issuerText: { fontSize: fontSize.xs, color: '#374151' },
  issuersMore: { fontSize: fontSize.xs, color: '#6B7280' },

  // Credentials Section
  credentialsSection: { marginTop: spacing.md },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
  },
  sectionTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold },

  // Credential Card
  credentialCard: {
    marginHorizontal: spacing.md,
    marginBottom: spacing.sm,
    padding: spacing.md,
    borderRadius: borderRadius.lg,
    ...shadows.sm,
  },
  credentialHeader: { flexDirection: 'row', alignItems: 'flex-start' },
  badgeImage: { width: 50, height: 50, borderRadius: 8 },
  badgePlaceholder: {
    width: 50,
    height: 50,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgePlaceholderIcon: { fontSize: 24 },
  credentialInfo: { flex: 1, marginLeft: spacing.md },
  credentialName: { fontSize: fontSize.base, fontWeight: fontWeight.medium },
  credentialIssuer: { fontSize: fontSize.sm, marginTop: 2 },
  credentialStatus: { alignItems: 'flex-end' },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: borderRadius.full,
    gap: 4,
  },
  statusDot: { width: 6, height: 6, borderRadius: 3 },
  statusText: { fontSize: fontSize.xs, fontWeight: fontWeight.medium, textTransform: 'capitalize' },
  sourceBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: borderRadius.full,
    marginTop: 4,
  },
  sourceText: { fontSize: fontSize.xs, color: '#F97316', fontWeight: fontWeight.medium },
  skillsContainer: { flexDirection: 'row', flexWrap: 'wrap', marginTop: spacing.sm, gap: 4 },
  skillTag: { paddingHorizontal: spacing.sm, paddingVertical: 2, borderRadius: borderRadius.sm },
  skillText: { fontSize: fontSize.xs },
  moreSkills: { fontSize: fontSize.xs, alignSelf: 'center' },
  datesContainer: { flexDirection: 'row', gap: spacing.md, marginTop: spacing.sm },
  dateText: { fontSize: fontSize.xs },

  // Empty State
  emptyState: {
    marginHorizontal: spacing.md,
    padding: spacing.xl,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
  },
  emptyIcon: { fontSize: 48, marginBottom: spacing.md },
  emptyTitle: { fontSize: fontSize.lg, fontWeight: fontWeight.semibold, marginBottom: spacing.xs },
  emptySubtitle: { fontSize: fontSize.sm, textAlign: 'center' },
});
