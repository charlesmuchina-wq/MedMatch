/**
 * MedMatch Mobile - Home/Dashboard Screen
 * Batik-inspired design with stats, quick actions, and upcoming interviews
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
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../../constants/theme';
import { applicationsAPI } from '../../services/api';

// Stat Card Component
const StatCard = ({ 
  title, 
  value, 
  icon, 
  color, 
  onPress 
}: { 
  title: string; 
  value: string | number; 
  icon: string; 
  color: string;
  onPress?: () => void;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <TouchableOpacity
      style={[styles.statCard, { backgroundColor: themeColors.surface }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={[styles.statIconContainer, { backgroundColor: color + '20' }]}>
        <Text style={styles.statIcon}>{icon}</Text>
      </View>
      <Text style={[styles.statValue, { color: themeColors.text }]}>{value}</Text>
      <Text style={[styles.statTitle, { color: themeColors.textSecondary }]}>{title}</Text>
    </TouchableOpacity>
  );
};

// Quick Action Card
const QuickActionCard = ({
  title,
  description,
  icon,
  gradientColors,
  onPress,
}: {
  title: string;
  description: string;
  icon: string;
  gradientColors: [string, string];
  onPress: () => void;
}) => (
  <TouchableOpacity style={styles.quickActionCard} onPress={onPress} activeOpacity={0.8}>
    <LinearGradient
      colors={gradientColors}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.quickActionGradient}
    >
      <Text style={styles.quickActionIcon}>{icon}</Text>
      <Text style={styles.quickActionTitle}>{title}</Text>
      <Text style={styles.quickActionDesc}>{description}</Text>
    </LinearGradient>
  </TouchableOpacity>
);

// Interview Card
const InterviewCard = ({
  company,
  position,
  date,
  time,
  type,
  onPress,
}: {
  company: string;
  position: string;
  date: string;
  time: string;
  type: 'video' | 'phone' | 'in_person';
  onPress: () => void;
}) => {
  const { colors: themeColors } = useTheme();
  const typeIcons = { video: '📹', phone: '📞', in_person: '🏢' };
  
  return (
    <TouchableOpacity
      style={[styles.interviewCard, { backgroundColor: themeColors.surface }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={[styles.interviewTypeIcon, { backgroundColor: colors.turquoise + '20' }]}>
        <Text style={styles.interviewTypeEmoji}>{typeIcons[type] || '📅'}</Text>
      </View>
      <View style={styles.interviewInfo}>
        <Text style={[styles.interviewPosition, { color: themeColors.text }]} numberOfLines={1}>
          {position}
        </Text>
        <Text style={[styles.interviewCompany, { color: themeColors.textSecondary }]} numberOfLines={1}>
          {company}
        </Text>
        <View style={styles.interviewDateTime}>
          <Text style={[styles.interviewDate, { color: colors.turquoise }]}>{date}</Text>
          <Text style={[styles.interviewTime, { color: themeColors.textTertiary }]}> • {time}</Text>
        </View>
      </View>
      <Text style={styles.chevron}>›</Text>
    </TouchableOpacity>
  );
};

export default function HomeScreen() {
  const { colors: themeColors } = useTheme();
  const { user } = useAuth();
  
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    savedJobs: 0,
    applications: 0,
    interviews: 0,
    messages: 0,
  });
  const [upcomingInterviews, setUpcomingInterviews] = useState<any[]>([]);

  const loadData = useCallback(async () => {
    try {
      const [applicationsRes] = await Promise.all([
        applicationsAPI.getStats().catch(() => ({ data: {} })),
      ]);
      
      setStats({
        savedJobs: applicationsRes.data?.saved_jobs || 12,
        applications: applicationsRes.data?.total_applications || 8,
        interviews: applicationsRes.data?.interviews_scheduled || 3,
        messages: applicationsRes.data?.unread_messages || 2,
      });

      setUpcomingInterviews([
        {
          id: '1',
          company: 'Google',
          position: 'Senior Software Engineer',
          date: 'Tomorrow',
          time: '2:00 PM',
          type: 'video',
        },
        {
          id: '2',
          company: 'Microsoft',
          position: 'Product Manager',
          date: 'Jan 28',
          time: '10:00 AM',
          type: 'phone',
        },
      ]);
    } catch (error) {
      console.error('Failed to load home data:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  }, [loadData]);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: themeColors.background }]}>
        <ActivityIndicator size="large" color={colors.turquoise} />
      </View>
    );
  }

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: themeColors.background }]}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.turquoise} />
      }
    >
      {/* Greeting Header */}
      <LinearGradient
        colors={[colors.turquoise, colors.turquoiseLight]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.greetingCard}
      >
        <View style={styles.batikOverlay}>
          <View style={[styles.batikCircle, { top: -20, right: 20, backgroundColor: colors.pinkLight + '20' }]} />
          <View style={[styles.batikCircle, { bottom: -30, left: 40, backgroundColor: colors.coral + '15' }]} />
        </View>
        <Text style={styles.greetingText}>{getGreeting()},</Text>
        <Text style={styles.userName}>{user?.name || 'User'} 👋</Text>
        <Text style={styles.greetingSubtext}>Ready to find your next opportunity?</Text>
      </LinearGradient>

      {/* Stats Grid */}
      <Text style={[styles.sectionTitle, { color: themeColors.text }]}>Your Activity</Text>
      <View style={styles.statsGrid}>
        <StatCard title="Saved Jobs" value={stats.savedJobs} icon="💾" color={colors.turquoise} onPress={() => router.push('/search')} />
        <StatCard title="Applications" value={stats.applications} icon="📝" color={colors.pink} onPress={() => {}} />
        <StatCard title="Interviews" value={stats.interviews} icon="📅" color={colors.coral} onPress={() => router.push('/calendar')} />
        <StatCard title="Messages" value={stats.messages} icon="💬" color={colors.gold} onPress={() => {}} />
      </View>

      {/* Quick Actions */}
      <Text style={[styles.sectionTitle, { color: themeColors.text }]}>Quick Actions</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.quickActionsContainer}>
        <QuickActionCard title="Interview Prep" description="AI-powered practice" icon="🎯" gradientColors={[colors.turquoise, colors.turquoiseDark]} onPress={() => router.push('/ai-tools')} />
        <QuickActionCard title="Voice Coach" description="Improve your delivery" icon="🎤" gradientColors={[colors.pink, colors.pinkDark]} onPress={() => router.push('/ai-tools')} />
        <QuickActionCard title="Cover Letter" description="AI-generated letters" icon="✉️" gradientColors={[colors.coral, colors.red]} onPress={() => router.push('/ai-tools')} />
        <QuickActionCard title="Upload Resume" description="Update your profile" icon="📄" gradientColors={[colors.gold, '#b8860b']} onPress={() => router.push('/profile')} />
      </ScrollView>

      {/* Upcoming Interviews */}
      <View style={styles.sectionHeader}>
        <Text style={[styles.sectionTitle, { color: themeColors.text }]}>Upcoming Interviews</Text>
        <TouchableOpacity onPress={() => router.push('/calendar')}>
          <Text style={[styles.seeAll, { color: colors.turquoise }]}>See All</Text>
        </TouchableOpacity>
      </View>
      
      {upcomingInterviews.length > 0 ? (
        <View style={styles.interviewsList}>
          {upcomingInterviews.map((interview) => (
            <InterviewCard key={interview.id} {...interview} onPress={() => router.push('/calendar')} />
          ))}
        </View>
      ) : (
        <View style={[styles.emptyState, { backgroundColor: themeColors.surface }]}>
          <Text style={styles.emptyIcon}>📅</Text>
          <Text style={[styles.emptyText, { color: themeColors.textSecondary }]}>No upcoming interviews</Text>
          <TouchableOpacity onPress={() => router.push('/search')}>
            <Text style={[styles.emptyAction, { color: colors.turquoise }]}>Start applying to jobs</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* AI Assistant Prompt */}
      <TouchableOpacity style={[styles.aiPrompt, { backgroundColor: themeColors.surface }]} onPress={() => router.push('/ai-tools')}>
        <LinearGradient colors={[colors.turquoise + '20', colors.pink + '10']} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={styles.aiPromptGradient}>
          <Text style={styles.aiPromptIcon}>✨</Text>
          <View style={styles.aiPromptContent}>
            <Text style={[styles.aiPromptTitle, { color: themeColors.text }]}>KARAU Dragon AI</Text>
            <Text style={[styles.aiPromptDesc, { color: themeColors.textSecondary }]}>Ask me anything about your job search</Text>
          </View>
          <Text style={styles.chevron}>›</Text>
        </LinearGradient>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { paddingBottom: spacing.xl },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  greetingCard: { margin: spacing.md, padding: spacing.lg, borderRadius: borderRadius.xl, overflow: 'hidden' },
  batikOverlay: { ...StyleSheet.absoluteFillObject },
  batikCircle: { position: 'absolute', width: 100, height: 100, borderRadius: 50 },
  greetingText: { fontSize: fontSize.lg, color: colors.white + 'cc' },
  userName: { fontSize: fontSize['2xl'], fontWeight: fontWeight.bold, color: colors.white, marginBottom: spacing.xs },
  greetingSubtext: { fontSize: fontSize.sm, color: colors.white + 'aa' },
  sectionTitle: { fontSize: fontSize.lg, fontWeight: fontWeight.semibold, marginHorizontal: spacing.md, marginTop: spacing.lg, marginBottom: spacing.md },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: spacing.lg, paddingRight: spacing.md },
  seeAll: { fontSize: fontSize.sm, fontWeight: fontWeight.medium },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: spacing.sm, gap: spacing.sm },
  statCard: { width: '47%', padding: spacing.md, borderRadius: borderRadius.lg, ...shadows.sm },
  statIconContainer: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center', marginBottom: spacing.sm },
  statIcon: { fontSize: 20 },
  statValue: { fontSize: fontSize['2xl'], fontWeight: fontWeight.bold },
  statTitle: { fontSize: fontSize.sm, marginTop: spacing.xs },
  quickActionsContainer: { paddingHorizontal: spacing.md, gap: spacing.md },
  quickActionCard: { width: 140, height: 130, borderRadius: borderRadius.lg, overflow: 'hidden' },
  quickActionGradient: { flex: 1, padding: spacing.md, justifyContent: 'space-between' },
  quickActionIcon: { fontSize: 28 },
  quickActionTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, color: colors.white },
  quickActionDesc: { fontSize: fontSize.xs, color: colors.white + 'cc' },
  interviewsList: { paddingHorizontal: spacing.md, gap: spacing.sm },
  interviewCard: { flexDirection: 'row', alignItems: 'center', padding: spacing.md, borderRadius: borderRadius.lg, ...shadows.sm },
  interviewTypeIcon: { width: 48, height: 48, borderRadius: 24, justifyContent: 'center', alignItems: 'center', marginRight: spacing.md },
  interviewTypeEmoji: { fontSize: 22 },
  interviewInfo: { flex: 1 },
  interviewPosition: { fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  interviewCompany: { fontSize: fontSize.sm, marginTop: 2 },
  interviewDateTime: { flexDirection: 'row', marginTop: spacing.xs },
  interviewDate: { fontSize: fontSize.sm, fontWeight: fontWeight.medium },
  interviewTime: { fontSize: fontSize.sm },
  chevron: { fontSize: 24, color: colors.turquoise, marginLeft: spacing.sm },
  emptyState: { margin: spacing.md, padding: spacing.xl, borderRadius: borderRadius.lg, alignItems: 'center', ...shadows.sm },
  emptyIcon: { fontSize: 40, marginBottom: spacing.sm },
  emptyText: { fontSize: fontSize.base, textAlign: 'center' },
  emptyAction: { fontSize: fontSize.base, fontWeight: fontWeight.medium, marginTop: spacing.sm },
  aiPrompt: { margin: spacing.md, borderRadius: borderRadius.lg, overflow: 'hidden', ...shadows.sm },
  aiPromptGradient: { flexDirection: 'row', alignItems: 'center', padding: spacing.md },
  aiPromptIcon: { fontSize: 32, marginRight: spacing.md },
  aiPromptContent: { flex: 1 },
  aiPromptTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  aiPromptDesc: { fontSize: fontSize.sm, marginTop: 2 },
});
