/**
 * MedMatch Mobile - Job Search Screen
 * Search and browse jobs with filters
 */
import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../contexts/ThemeContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../../constants/theme';
import { jobsAPI } from '../../services/api';

// Job Card Component
const JobCard = ({
  id,
  title,
  company,
  location,
  salary,
  type,
  matchScore,
  postedDate,
  isSaved,
  onPress,
  onSave,
}: any) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <TouchableOpacity
      style={[styles.jobCard, { backgroundColor: themeColors.surface }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.jobHeader}>
        <View style={[styles.companyLogo, { backgroundColor: colors.turquoise + '20' }]}>
          <Text style={styles.companyInitial}>{company?.charAt(0) || 'C'}</Text>
        </View>
        <View style={styles.jobInfo}>
          <Text style={[styles.jobTitle, { color: themeColors.text }]} numberOfLines={2}>
            {title}
          </Text>
          <Text style={[styles.companyName, { color: themeColors.textSecondary }]}>
            {company}
          </Text>
        </View>
        <TouchableOpacity onPress={onSave} style={styles.saveButton}>
          <Text style={styles.saveIcon}>{isSaved ? '❤️' : '🤍'}</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.jobDetails}>
        <View style={[styles.tag, { backgroundColor: themeColors.background }]}>
          <Text style={[styles.tagText, { color: themeColors.textSecondary }]}>📍 {location || 'Remote'}</Text>
        </View>
        <View style={[styles.tag, { backgroundColor: themeColors.background }]}>
          <Text style={[styles.tagText, { color: themeColors.textSecondary }]}>💼 {type || 'Full-time'}</Text>
        </View>
        {salary && (
          <View style={[styles.tag, { backgroundColor: colors.turquoise + '15' }]}>
            <Text style={[styles.tagText, { color: colors.turquoise }]}>💰 {salary}</Text>
          </View>
        )}
      </View>
      
      <View style={styles.jobFooter}>
        {matchScore && (
          <View style={[styles.matchBadge, { backgroundColor: colors.turquoise + '20' }]}>
            <Text style={[styles.matchText, { color: colors.turquoise }]}>{matchScore}% Match</Text>
          </View>
        )}
        <Text style={[styles.postedDate, { color: themeColors.textTertiary }]}>
          {postedDate || 'Posted today'}
        </Text>
      </View>
    </TouchableOpacity>
  );
};

// Filter Chip
const FilterChip = ({ label, isActive, onPress }: { label: string; isActive: boolean; onPress: () => void }) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <TouchableOpacity
      style={[
        styles.filterChip,
        { 
          backgroundColor: isActive ? colors.turquoise : themeColors.surface,
          borderColor: isActive ? colors.turquoise : themeColors.border,
        }
      ]}
      onPress={onPress}
    >
      <Text style={[styles.filterChipText, { color: isActive ? colors.white : themeColors.text }]}>
        {label}
      </Text>
    </TouchableOpacity>
  );
};

export default function SearchScreen() {
  const { colors: themeColors } = useTheme();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [location, setLocation] = useState('');
  const [jobs, setJobs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [activeFilter, setActiveFilter] = useState('all');
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());

  const filters = [
    { key: 'all', label: 'All Jobs' },
    { key: 'remote', label: '🏠 Remote' },
    { key: 'fulltime', label: '⏰ Full-time' },
    { key: 'parttime', label: '⏱️ Part-time' },
    { key: 'contract', label: '📋 Contract' },
  ];

  const loadJobs = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await jobsAPI.search({ query: searchQuery, location });
      setJobs(response.data?.jobs || mockJobs);
    } catch (error) {
      console.error('Failed to load jobs:', error);
      setJobs(mockJobs);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, location]);

  // Mock data for demo
  const mockJobs = [
    { id: '1', title: 'Senior Software Engineer', company: 'Google', location: 'Remote', salary: '$150k-200k', type: 'Full-time', matchScore: 95, postedDate: '2 days ago' },
    { id: '2', title: 'Product Manager', company: 'Microsoft', location: 'Seattle, WA', salary: '$130k-180k', type: 'Full-time', matchScore: 88, postedDate: '1 day ago' },
    { id: '3', title: 'UX Designer', company: 'Apple', location: 'Cupertino, CA', salary: '$120k-160k', type: 'Full-time', matchScore: 82, postedDate: '3 days ago' },
    { id: '4', title: 'Data Scientist', company: 'Meta', location: 'Remote', salary: '$140k-190k', type: 'Full-time', matchScore: 79, postedDate: 'Today' },
    { id: '5', title: 'DevOps Engineer', company: 'Amazon', location: 'Remote', salary: '$135k-175k', type: 'Contract', matchScore: 75, postedDate: '5 days ago' },
  ];

  useEffect(() => {
    setJobs(mockJobs);
    setIsLoading(false);
  }, []);

  const handleSearch = () => {
    loadJobs();
  };

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadJobs();
    setRefreshing(false);
  }, [loadJobs]);

  const toggleSave = (jobId: string) => {
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

  return (
    <View style={[styles.container, { backgroundColor: themeColors.background }]}>
      {/* Search Header */}
      <View style={[styles.searchHeader, { backgroundColor: themeColors.surface }]}>
        <View style={[styles.searchInputContainer, { backgroundColor: themeColors.background, borderColor: themeColors.border }]}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            style={[styles.searchInput, { color: themeColors.text }]}
            placeholder="Job title, skills, or company"
            placeholderTextColor={themeColors.textTertiary}
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={handleSearch}
            returnKeyType="search"
          />
        </View>
        <View style={[styles.locationInputContainer, { backgroundColor: themeColors.background, borderColor: themeColors.border }]}>
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
        <TouchableOpacity onPress={handleSearch}>
          <LinearGradient
            colors={[colors.turquoise, colors.turquoiseDark]}
            style={styles.searchButton}
          >
            <Text style={styles.searchButtonText}>Search</Text>
          </LinearGradient>
        </TouchableOpacity>
      </View>

      {/* Filters */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filtersContainer} contentContainerStyle={styles.filtersContent}>
        {filters.map(filter => (
          <FilterChip
            key={filter.key}
            label={filter.label}
            isActive={activeFilter === filter.key}
            onPress={() => setActiveFilter(filter.key)}
          />
        ))}
      </ScrollView>

      {/* Results Count */}
      <View style={styles.resultsHeader}>
        <Text style={[styles.resultsCount, { color: themeColors.textSecondary }]}>
          {jobs.length} jobs found
        </Text>
      </View>

      {/* Job List */}
      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.turquoise} />
        </View>
      ) : (
        <FlatList
          data={jobs}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <JobCard
              {...item}
              isSaved={savedJobs.has(item.id)}
              onPress={() => router.push(`/job/${item.id}`)}
              onSave={() => toggleSave(item.id)}
            />
          )}
          contentContainerStyle={styles.jobList}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.turquoise} />
          }
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <Text style={styles.emptyIcon}>🔍</Text>
              <Text style={[styles.emptyText, { color: themeColors.textSecondary }]}>
                No jobs found. Try different keywords.
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
  searchHeader: { padding: spacing.md, gap: spacing.sm, ...shadows.sm },
  searchInputContainer: { flexDirection: 'row', alignItems: 'center', height: 48, borderRadius: borderRadius.lg, borderWidth: 1, paddingHorizontal: spacing.md },
  locationInputContainer: { flexDirection: 'row', alignItems: 'center', height: 48, borderRadius: borderRadius.lg, borderWidth: 1, paddingHorizontal: spacing.md },
  searchIcon: { fontSize: 16, marginRight: spacing.sm },
  searchInput: { flex: 1, fontSize: fontSize.base },
  searchButton: { height: 48, borderRadius: borderRadius.lg, justifyContent: 'center', alignItems: 'center', paddingHorizontal: spacing.lg },
  searchButtonText: { color: colors.white, fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  filtersContainer: { maxHeight: 50 },
  filtersContent: { paddingHorizontal: spacing.md, gap: spacing.sm, paddingVertical: spacing.sm },
  filterChip: { paddingHorizontal: spacing.md, paddingVertical: spacing.sm, borderRadius: borderRadius.full, borderWidth: 1 },
  filterChipText: { fontSize: fontSize.sm, fontWeight: fontWeight.medium },
  resultsHeader: { paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  resultsCount: { fontSize: fontSize.sm },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  jobList: { paddingHorizontal: spacing.md, paddingBottom: spacing.xl, gap: spacing.md },
  jobCard: { padding: spacing.md, borderRadius: borderRadius.lg, ...shadows.sm },
  jobHeader: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: spacing.sm },
  companyLogo: { width: 48, height: 48, borderRadius: borderRadius.md, justifyContent: 'center', alignItems: 'center', marginRight: spacing.md },
  companyInitial: { fontSize: fontSize.xl, fontWeight: fontWeight.bold, color: colors.turquoise },
  jobInfo: { flex: 1 },
  jobTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, marginBottom: 2 },
  companyName: { fontSize: fontSize.sm },
  saveButton: { padding: spacing.xs },
  saveIcon: { fontSize: 20 },
  jobDetails: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.xs, marginBottom: spacing.sm },
  tag: { paddingHorizontal: spacing.sm, paddingVertical: 4, borderRadius: borderRadius.sm },
  tagText: { fontSize: fontSize.xs },
  jobFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  matchBadge: { paddingHorizontal: spacing.sm, paddingVertical: 4, borderRadius: borderRadius.sm },
  matchText: { fontSize: fontSize.xs, fontWeight: fontWeight.semibold },
  postedDate: { fontSize: fontSize.xs },
  emptyState: { alignItems: 'center', paddingVertical: spacing['3xl'] },
  emptyIcon: { fontSize: 48, marginBottom: spacing.md },
  emptyText: { fontSize: fontSize.base, textAlign: 'center' },
});
