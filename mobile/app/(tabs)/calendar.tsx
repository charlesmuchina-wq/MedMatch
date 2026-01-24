/**
 * MedMatch Mobile - Interview Calendar Screen
 */
import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../contexts/ThemeContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../../constants/theme';

// Interview Card
const InterviewCard = ({ interview, onPress }: { interview: any; onPress: () => void }) => {
  const { colors: themeColors } = useTheme();
  const typeIcons: { [key: string]: string } = { video: '📹', phone: '📞', in_person: '🏢' };
  const typeColors: { [key: string]: string } = { video: colors.turquoise, phone: colors.coral, in_person: colors.pink };
  
  const startDate = new Date(interview.start_time);
  const isToday = new Date().toDateString() === startDate.toDateString();
  const isPast = startDate < new Date();
  
  return (
    <TouchableOpacity
      style={[styles.interviewCard, { backgroundColor: themeColors.surface, opacity: isPast ? 0.6 : 1 }]}
      onPress={onPress}
    >
      <View style={[styles.dateColumn, { backgroundColor: typeColors[interview.interview_type] + '15' }]}>
        <Text style={[styles.dateDay, { color: typeColors[interview.interview_type] }]}>
          {isToday ? 'TODAY' : startDate.getDate()}
        </Text>
        {!isToday && (
          <Text style={[styles.dateMonth, { color: typeColors[interview.interview_type] }]}>
            {startDate.toLocaleString('default', { month: 'short' }).toUpperCase()}
          </Text>
        )}
      </View>
      
      <View style={styles.interviewDetails}>
        <View style={styles.interviewHeader}>
          <Text style={[styles.interviewPosition, { color: themeColors.text }]} numberOfLines={1}>
            {interview.position}
          </Text>
          <Text style={styles.typeIcon}>{typeIcons[interview.interview_type] || '📅'}</Text>
        </View>
        <Text style={[styles.interviewCompany, { color: themeColors.textSecondary }]} numberOfLines={1}>
          {interview.company}
        </Text>
        <Text style={[styles.interviewTime, { color: themeColors.textTertiary }]}>
          {startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
        
        {interview.preparation && (
          <View style={[styles.prepBadge, { backgroundColor: colors.turquoise + '15' }]}>
            <Text style={[styles.prepText, { color: colors.turquoise }]}>✨ AI Prep Ready</Text>
          </View>
        )}
      </View>
      
      <Text style={[styles.chevron, { color: colors.turquoise }]}>›</Text>
    </TouchableOpacity>
  );
};

// Day Section
const DaySection = ({ title, interviews, onInterviewPress }: { title: string; interviews: any[]; onInterviewPress: (id: string) => void }) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <View style={styles.daySection}>
      <Text style={[styles.daySectionTitle, { color: themeColors.text }]}>{title}</Text>
      {interviews.map(interview => (
        <InterviewCard key={interview.id} interview={interview} onPress={() => onInterviewPress(interview.id)} />
      ))}
    </View>
  );
};

export default function CalendarScreen() {
  const { colors: themeColors } = useTheme();
  
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [interviews, setInterviews] = useState<any[]>([]);
  const [stats, setStats] = useState({ upcoming: 0, completed: 0, thisWeek: 0 });

  // Mock data
  const mockInterviews = [
    { id: '1', position: 'Senior Software Engineer', company: 'Google', interview_type: 'video', start_time: new Date(Date.now() + 86400000).toISOString(), preparation: true },
    { id: '2', position: 'Product Manager', company: 'Microsoft', interview_type: 'phone', start_time: new Date(Date.now() + 172800000).toISOString(), preparation: false },
    { id: '3', position: 'UX Designer', company: 'Apple', interview_type: 'in_person', start_time: new Date(Date.now() + 432000000).toISOString(), preparation: true },
  ];

  const loadData = useCallback(async () => {
    try {
      // In real app, fetch from API
      setInterviews(mockInterviews);
      setStats({ upcoming: 3, completed: 5, thisWeek: 2 });
    } catch (error) {
      console.error('Failed to load interviews:', error);
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

  const groupInterviewsByDate = () => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const nextWeek = new Date(today);
    nextWeek.setDate(nextWeek.getDate() + 7);

    const groups: { [key: string]: any[] } = {
      today: [],
      tomorrow: [],
      thisWeek: [],
      later: [],
    };

    interviews.forEach(interview => {
      const date = new Date(interview.start_time);
      if (date.toDateString() === today.toDateString()) {
        groups.today.push(interview);
      } else if (date.toDateString() === tomorrow.toDateString()) {
        groups.tomorrow.push(interview);
      } else if (date < nextWeek) {
        groups.thisWeek.push(interview);
      } else {
        groups.later.push(interview);
      }
    });

    return groups;
  };

  const grouped = groupInterviewsByDate();

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
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.turquoise} />}
    >
      {/* Stats Header */}
      <LinearGradient
        colors={[colors.turquoise, colors.turquoiseLight]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.statsHeader}
      >
        <View style={styles.batikOverlay}>
          <View style={[styles.batikCircle, { top: -20, right: 30, backgroundColor: colors.pinkLight + '20' }]} />
        </View>
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{stats.upcoming}</Text>
            <Text style={styles.statLabel}>Upcoming</Text>
          </View>
          <View style={[styles.statDivider, { backgroundColor: colors.white + '30' }]} />
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{stats.thisWeek}</Text>
            <Text style={styles.statLabel}>This Week</Text>
          </View>
          <View style={[styles.statDivider, { backgroundColor: colors.white + '30' }]} />
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{stats.completed}</Text>
            <Text style={styles.statLabel}>Completed</Text>
          </View>
        </View>
      </LinearGradient>

      {/* Interview Sections */}
      <View style={styles.sectionsContainer}>
        {grouped.today.length > 0 && (
          <DaySection title="Today" interviews={grouped.today} onInterviewPress={(id) => {}} />
        )}
        {grouped.tomorrow.length > 0 && (
          <DaySection title="Tomorrow" interviews={grouped.tomorrow} onInterviewPress={(id) => {}} />
        )}
        {grouped.thisWeek.length > 0 && (
          <DaySection title="This Week" interviews={grouped.thisWeek} onInterviewPress={(id) => {}} />
        )}
        {grouped.later.length > 0 && (
          <DaySection title="Later" interviews={grouped.later} onInterviewPress={(id) => {}} />
        )}

        {interviews.length === 0 && (
          <View style={[styles.emptyState, { backgroundColor: themeColors.surface }]}>
            <Text style={styles.emptyIcon}>📅</Text>
            <Text style={[styles.emptyTitle, { color: themeColors.text }]}>No Interviews Scheduled</Text>
            <Text style={[styles.emptySubtext, { color: themeColors.textSecondary }]}>
              Start applying to jobs and schedule your interviews here
            </Text>
            <TouchableOpacity style={styles.emptyButton} onPress={() => router.push('/search')}>
              <LinearGradient colors={[colors.turquoise, colors.turquoiseDark]} style={styles.emptyButtonGradient}>
                <Text style={styles.emptyButtonText}>Find Jobs</Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  statsHeader: { margin: spacing.md, padding: spacing.lg, borderRadius: borderRadius.xl, overflow: 'hidden' },
  batikOverlay: { ...StyleSheet.absoluteFillObject },
  batikCircle: { position: 'absolute', width: 80, height: 80, borderRadius: 40 },
  statsRow: { flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center' },
  statItem: { alignItems: 'center' },
  statNumber: { fontSize: fontSize['2xl'], fontWeight: fontWeight.bold, color: colors.white },
  statLabel: { fontSize: fontSize.sm, color: colors.white + 'cc', marginTop: 2 },
  statDivider: { width: 1, height: 40 },
  sectionsContainer: { paddingHorizontal: spacing.md, paddingBottom: spacing.xl },
  daySection: { marginBottom: spacing.lg },
  daySectionTitle: { fontSize: fontSize.lg, fontWeight: fontWeight.semibold, marginBottom: spacing.sm },
  interviewCard: { flexDirection: 'row', alignItems: 'center', padding: spacing.md, borderRadius: borderRadius.lg, marginBottom: spacing.sm, ...shadows.sm },
  dateColumn: { width: 50, height: 50, borderRadius: borderRadius.md, justifyContent: 'center', alignItems: 'center', marginRight: spacing.md },
  dateDay: { fontSize: fontSize.lg, fontWeight: fontWeight.bold },
  dateMonth: { fontSize: fontSize.xs },
  interviewDetails: { flex: 1 },
  interviewHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  interviewPosition: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, flex: 1 },
  typeIcon: { fontSize: 16, marginLeft: spacing.xs },
  interviewCompany: { fontSize: fontSize.sm, marginTop: 2 },
  interviewTime: { fontSize: fontSize.sm, marginTop: 2 },
  prepBadge: { marginTop: spacing.xs, alignSelf: 'flex-start', paddingHorizontal: spacing.sm, paddingVertical: 2, borderRadius: borderRadius.sm },
  prepText: { fontSize: fontSize.xs, fontWeight: fontWeight.medium },
  chevron: { fontSize: 24, marginLeft: spacing.sm },
  emptyState: { padding: spacing.xl, borderRadius: borderRadius.xl, alignItems: 'center', marginTop: spacing.xl },
  emptyIcon: { fontSize: 48, marginBottom: spacing.md },
  emptyTitle: { fontSize: fontSize.lg, fontWeight: fontWeight.semibold, marginBottom: spacing.xs },
  emptySubtext: { fontSize: fontSize.sm, textAlign: 'center', marginBottom: spacing.lg },
  emptyButton: { borderRadius: borderRadius.lg, overflow: 'hidden' },
  emptyButtonGradient: { paddingHorizontal: spacing.xl, paddingVertical: spacing.md },
  emptyButtonText: { color: colors.white, fontSize: fontSize.base, fontWeight: fontWeight.semibold },
});
