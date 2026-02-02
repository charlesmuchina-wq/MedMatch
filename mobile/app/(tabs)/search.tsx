/**
 * MedMatch Mobile - Job Search Screen
 * Search and filter jobs with batik-inspired design
 */
import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  FlatList,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../contexts/ThemeContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../../constants/theme';
import { jobsAPI } from '../../services/api';

// Filter Chip Component
const FilterChip = ({ 
  label, 
  active, 
  onPress 
}: { 
  label: string; 
  active: boolean; 
  onPress: () => void;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <TouchableOpacity
      style={[
        styles.filterChip,
        { 
          backgroundColor: active ? colors.turquoise : themeColors.surface,
          borderColor: active ? colors.turquoise : themeColors.border,
        }
      ]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <Text style={[
        styles.filterChipText,
        { color: active ? colors.white : themeColors.text }
      ]}>
        {label}
      </Text>
    </TouchableOpacity>
  );
};

// Job Card Component
const JobCard = ({
  job,
  onPress,
  onSave,
  isSaved,
}: {
  job: any;
  onPress: () => void;
  onSave: () => void;
  isSaved: boolean;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <TouchableOpacity
      style={[styles.jobCard, { backgroundColor: themeColors.surface }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.jobHeader}>
        <View style={[styles.companyLogo, { backgroundColor: colors.turquoise + '20' }]}>
          <Text style={styles.companyLogoText}>
            {job.company?.charAt(0) || '?'}
          </Text>
        </View>
        <View style={styles.jobHeaderInfo}>
          <Text style={[styles.jobTitle, { color: themeColors.text }]} numberOfLines={2}>
            {job.title}
          </Text>
          <Text style={[styles.companyName, { color: themeColors.textSecondary }]} numberOfLines={1}>
            {job.company}
          </Text>
        </View>
        <TouchableOpacity style={styles.saveButton} onPress={onSave}>
          <Text style={styles.saveIcon}>{isSaved ? '❤️' : '🤍'}</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.jobMeta}>
        <View style={[styles.metaBadge, { backgroundColor: themeColors.background }]}>
          <Text style={styles.metaIcon}>📍</Text>
          <Text style={[styles.metaText, { color: themeColors.textSecondary }]} numberOfLines={1}>
            {job.location || 'Remote'}
          </Text>
        </View>
        <View style={[styles.metaBadge, { backgroundColor: themeColors.background }]}>
          <Text style={styles.metaIcon}>💰</Text>
          <Text style={[styles.metaText, { color: themeColors.textSecondary }]}>
            {job.salary || 'Competitive'}
          </Text>
        </View>
        {job.job_type && (
          <View style={[styles.metaBadge, { backgroundColor: colors.turquoise + '15' }]}>
            <Text style={[styles.metaText, { color: colors.turquoise }]}>
              {job.job_type}
            </Text>
          </View>
        )}
      </View>
      
      {job.match_score && (
        <View style={styles.matchScore}>
          <LinearGradient
            colors={[colors.turquoise, colors.turquoiseLight]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={[styles.matchBar, { width: `${job.match_score}%` }]}
          />
          <Text style={[styles.matchText, { color: colors.turquoise }]}>
            {job.match_score}% Match
          </Text>
        </View>
      )}
      
      <Text style={[styles.postedDate, { color: themeColors.textTertiary }]}>
        Posted {job.posted_at || 'recently'}
      </Text>
    </TouchableOpacity>
  );
};

export default function SearchScreen() {
  const { colors: themeColors } = useTheme();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [location, setLocation] = useState('');
  const [jobs, setJobs] = useState<any[]>([]);
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [activeFilter, setActiveFilter] = useState('all');
  
  const filters = [
    { id: 'all', label: 'All Jobs' },
    { id: 'remote', label: '🌍 Remote' },
    { id: 'hybrid', label: '🏢 Hybrid' },
    { id: 'fulltime', label: '⏰ Full-time' },
    { id: 'contract', label: '📝 Contract' },
  ];

  const loadJobs = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await jobsAPI.search({ 
        query: searchQuery, 
        location: location 
      });
      setJobs(response.data?.jobs || []);
    } catch (error) {
      console.error('Failed to load jobs:', error);
      // Demo data fallback
      setJobs([
        {
          id: '1',
          title: 'Senior Software Engineer',
          company: 'Google',
          location: 'Remote',
          salary: '$150k - $200k',
          job_type: 'Full-time',
          match_score: 92,
          posted_at: '2 days ago',
        },
        {
          id: '2',
          title: 'Product Manager',
          company: 'Microsoft',
          location: 'Seattle, WA',
          salary: '$130k - $170k',
          job_type: 'Full-time',
          match_score: 87,
          posted_at: '1 week ago',
        },
        {
          id: '3',
          title: 'UX Designer',
          company: 'Apple',
          location: 'Cupertino, CA',
          salary: '$120k - $160k',
          job_type: 'Full-time',
          match_score: 78,
          posted_at: '3 days ago',
        },
        {
          id: '4',
          title: 'Data Scientist',
          company: 'Meta',
          location: 'Remote',
          salary: '$140k - $180k',
          job_type: 'Full-time',
          match_score: 85,
          posted_at: '5 days ago',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, location]);

  useEffect(() => {
    loadJobs();
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadJobs();
    setRefreshing(false);
  }, [loadJobs]);

  const handleSaveJob = (jobId: string) => {
    setSavedJobs(prev => {
      const newSet = new Set(prev);
      if (newSet.has(jobId)) {
        newSet.delete(jobId);
      } else {
        newSet.add(jobId);
      }
      return newSet;
    });
  };

  const handleSearch = () => {
    loadJobs();
  };

  const filteredJobs = jobs.filter(job => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'remote') return job.location?.toLowerCase().includes('remote');
    if (activeFilter === 'hybrid') return job.job_type?.toLowerCase().includes('hybrid');
    if (activeFilter === 'fulltime') return job.job_type?.toLowerCase().includes('full');
    if (activeFilter === 'contract') return job.job_type?.toLowerCase().includes('contract');
    return true;
  });

  return (
    <View style={[styles.container, { backgroundColor: themeColors.background }]}>
      {/* Search Header */}
      <View style={[styles.searchHeader, { backgroundColor: themeColors.surface }]}>
        <View style={[styles.searchInputContainer, { backgroundColor: themeColors.background, borderColor: themeColors.border }]}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            style={[styles.searchInput, { color: themeColors.text }]}
            placeholder="Job title, company, or keywords"
            placeholderTextColor={themeColors.textTertiary}
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={handleSearch}
            returnKeyType="search"
          />
        </View>
        <View style={[styles.searchInputContainer, styles.locationInput, { backgroundColor: themeColors.background, borderColor: themeColors.border }]}>
          <Text style={styles.searchIcon}>📍</Text>
          <TextInput
            style={[styles.searchInput, { color: themeColors.text }]}
            placeholder="Location"
            placeholderTextColor={themeColors.textTertiary}
            value={location}
            onChangeText={setLocation}
            onSubmitEditing={handleSearch}
            returnKeyType="search"
          />
        </View>
        <TouchableOpacity 
          style={styles.searchButton} 
          onPress={handleSearch}
        >
          <LinearGradient
            colors={[colors.turquoise, colors.turquoiseLight]}
            style={styles.searchButtonGradient}
          >
            <Text style={styles.searchButtonText}>Search</Text>
          </LinearGradient>
        </TouchableOpacity>
      </View>

      {/* Filters */}
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.filtersContainer}
      >
        {filters.map((filter) => (
          <FilterChip
            key={filter.id}
            label={filter.label}
            active={activeFilter === filter.id}
            onPress={() => setActiveFilter(filter.id)}
          />
        ))}
      </ScrollView>

      {/* Results Count */}
      <View style={styles.resultsHeader}>
        <Text style={[styles.resultsCount, { color: themeColors.textSecondary }]}>
          {filteredJobs.length} jobs found
        </Text>
        <TouchableOpacity>
          <Text style={[styles.sortButton, { color: colors.turquoise }]}>
            Sort by: Match ↓
          </Text>
        </TouchableOpacity>
      </View>

      {/* Jobs List */}
      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.turquoise} />
          <Text style={[styles.loadingText, { color: themeColors.textSecondary }]}>
            Finding the best jobs for you...
          </Text>
        </View>
      ) : (
        <FlatList
          data={filteredJobs}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <JobCard
              job={item}
              onPress={() => router.push({ pathname: '/job/[id]', params: { id: item.id } } as any)}
              onSave={() => handleSaveJob(item.id)}
              isSaved={savedJobs.has(item.id)}
            />
          )}
          contentContainerStyle={styles.jobsList}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={colors.turquoise}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <Text style={styles.emptyIcon}>🔍</Text>
              <Text style={[styles.emptyTitle, { color: themeColors.text }]}>
                No jobs found
              </Text>
              <Text style={[styles.emptyText, { color: themeColors.textSecondary }]}>
                Try adjusting your search criteria
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  searchHeader: { padding: spacing.md, gap: spacing.sm },
  searchInputContainer: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    borderRadius: borderRadius.lg, 
    borderWidth: 1,
    paddingHorizontal: spacing.md,
    height: 48,
  },
  locationInput: { marginTop: spacing.xs },
  searchIcon: { fontSize: 18, marginRight: spacing.sm },
  searchInput: { flex: 1, fontSize: fontSize.base },
  searchButton: { borderRadius: borderRadius.lg, overflow: 'hidden', marginTop: spacing.xs },
  searchButtonGradient: { paddingVertical: spacing.md, alignItems: 'center' },
  searchButtonText: { color: colors.white, fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  filtersContainer: { paddingHorizontal: spacing.md, paddingVertical: spacing.sm, gap: spacing.sm },
  filterChip: { 
    paddingHorizontal: spacing.md, 
    paddingVertical: spacing.sm, 
    borderRadius: borderRadius.full,
    borderWidth: 1,
  },
  filterChipText: { fontSize: fontSize.sm, fontWeight: fontWeight.medium },
  resultsHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  resultsCount: { fontSize: fontSize.sm },
  sortButton: { fontSize: fontSize.sm, fontWeight: fontWeight.medium },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingVertical: spacing['3xl'] },
  loadingText: { marginTop: spacing.md, fontSize: fontSize.base },
  jobsList: { paddingHorizontal: spacing.md, paddingBottom: spacing.xl },
  jobCard: { 
    padding: spacing.md, 
    borderRadius: borderRadius.lg, 
    marginBottom: spacing.md,
    ...shadows.sm,
  },
  jobHeader: { flexDirection: 'row', alignItems: 'flex-start' },
  companyLogo: { 
    width: 48, 
    height: 48, 
    borderRadius: borderRadius.md, 
    justifyContent: 'center', 
    alignItems: 'center',
    marginRight: spacing.md,
  },
  companyLogoText: { fontSize: fontSize.xl, fontWeight: fontWeight.bold, color: colors.turquoise },
  jobHeaderInfo: { flex: 1 },
  jobTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, marginBottom: 2 },
  companyName: { fontSize: fontSize.sm },
  saveButton: { padding: spacing.xs },
  saveIcon: { fontSize: 20 },
  jobMeta: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.xs, marginTop: spacing.md },
  metaBadge: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    paddingHorizontal: spacing.sm, 
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm,
  },
  metaIcon: { fontSize: 12, marginRight: 4 },
  metaText: { fontSize: fontSize.xs },
  matchScore: { marginTop: spacing.md, position: 'relative' },
  matchBar: { 
    height: 4, 
    borderRadius: 2,
    position: 'absolute',
    top: 0,
    left: 0,
  },
  matchText: { 
    fontSize: fontSize.xs, 
    fontWeight: fontWeight.medium,
    marginTop: spacing.xs,
  },
  postedDate: { fontSize: fontSize.xs, marginTop: spacing.sm },
  emptyState: { alignItems: 'center', paddingVertical: spacing['3xl'] },
  emptyIcon: { fontSize: 48, marginBottom: spacing.md },
  emptyTitle: { fontSize: fontSize.lg, fontWeight: fontWeight.semibold },
  emptyText: { fontSize: fontSize.base, marginTop: spacing.xs },
});
