/**
 * MedMatch Mobile - Home/Jobs Screen
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { router } from 'expo-router';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';
import { jobsAPI } from '../../services/api';
import { Ionicons } from '@expo/vector-icons';

interface Job {
  job_id: string;
  title: string;
  company: string;
  location: string;
  salary_range?: string;
  job_type?: string;
  posted_date?: string;
  match_score?: number;
}

export default function JobsScreen() {
  const { colors } = useTheme();
  const { user } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const response = await jobsAPI.getRecommendations();
      setJobs(response.data.jobs || []);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const onRefresh = () => {
    setIsRefreshing(true);
    loadJobs();
  };

  const renderJobCard = ({ item }: { item: Job }) => (
    <TouchableOpacity
      style={[styles.jobCard, { backgroundColor: colors.surface }]}
      onPress={() => router.push(`/job/${item.job_id}`)}
      activeOpacity={0.7}
    >
      <View style={styles.jobHeader}>
        <View style={styles.jobInfo}>
          <Text style={[styles.jobTitle, { color: colors.text }]} numberOfLines={2}>
            {item.title}
          </Text>
          <Text style={[styles.companyName, { color: colors.primary }]}>
            {item.company}
          </Text>
        </View>
        {item.match_score && (
          <View style={[styles.matchBadge, { backgroundColor: colors.primary }]}>
            <Text style={styles.matchText}>{item.match_score}%</Text>
          </View>
        )}
      </View>
      
      <View style={styles.jobMeta}>
        <View style={styles.metaItem}>
          <Ionicons name="location-outline" size={14} color={colors.textSecondary} />
          <Text style={[styles.metaText, { color: colors.textSecondary }]}>
            {item.location}
          </Text>
        </View>
        {item.salary_range && (
          <View style={styles.metaItem}>
            <Ionicons name="cash-outline" size={14} color={colors.textSecondary} />
            <Text style={[styles.metaText, { color: colors.textSecondary }]}>
              {item.salary_range}
            </Text>
          </View>
        )}
      </View>
      
      {item.job_type && (
        <View style={[styles.typeBadge, { backgroundColor: colors.border }]}>
          <Text style={[styles.typeText, { color: colors.text }]}>{item.job_type}</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={[styles.loadingText, { color: colors.textSecondary }]}>
          Finding your perfect jobs...
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <View style={[styles.header, { backgroundColor: colors.surface }]}>
        <Text style={[styles.greeting, { color: colors.text }]}>
          Welcome back, {user?.name?.split(' ')[0] || 'there'}! 👋
        </Text>
        <Text style={[styles.subtitle, { color: colors.textSecondary }]}>
          {jobs.length} jobs match your profile
        </Text>
      </View>

      <FlatList
        data={jobs}
        renderItem={renderJobCard}
        keyExtractor={(item) => item.job_id}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={onRefresh}
            tintColor={colors.primary}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="briefcase-outline" size={64} color={colors.textSecondary} />
            <Text style={[styles.emptyText, { color: colors.textSecondary }]}>
              No job recommendations yet
            </Text>
            <Text style={[styles.emptySubtext, { color: colors.textSecondary }]}>
              Upload your resume to get personalized matches
            </Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 20,
    paddingTop: 10,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  subtitle: {
    fontSize: 14,
    marginTop: 4,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
  },
  listContent: {
    padding: 16,
    paddingTop: 8,
  },
  jobCard: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  jobHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  jobInfo: {
    flex: 1,
    marginRight: 12,
  },
  jobTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  companyName: {
    fontSize: 14,
    fontWeight: '500',
  },
  matchBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  matchText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  jobMeta: {
    flexDirection: 'row',
    marginTop: 12,
    flexWrap: 'wrap',
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
    marginBottom: 4,
  },
  metaText: {
    fontSize: 12,
    marginLeft: 4,
  },
  typeBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    marginTop: 12,
  },
  typeText: {
    fontSize: 11,
    fontWeight: '500',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    marginTop: 8,
    textAlign: 'center',
  },
});
