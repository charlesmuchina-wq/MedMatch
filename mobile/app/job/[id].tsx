/**
 * MedMatch Mobile - Job Details Screen
 * Full job details with apply functionality
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Share,
  Linking,
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../contexts/ThemeContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../../constants/theme';
import { jobsAPI, aiAPI } from '../../services/api';

// Skill Badge Component
const SkillBadge = ({ skill, matched }: { skill: string; matched?: boolean }) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <View style={[
      styles.skillBadge,
      { 
        backgroundColor: matched ? colors.turquoise + '20' : themeColors.background,
        borderColor: matched ? colors.turquoise : themeColors.border,
      }
    ]}>
      {matched && <Text style={styles.matchIcon}>✓ </Text>}
      <Text style={[
        styles.skillText,
        { color: matched ? colors.turquoise : themeColors.textSecondary }
      ]}>
        {skill}
      </Text>
    </View>
  );
};

// Section Component
const Section = ({ 
  title, 
  children 
}: { 
  title: string; 
  children: React.ReactNode;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <View style={styles.section}>
      <Text style={[styles.sectionTitle, { color: themeColors.text }]}>{title}</Text>
      {children}
    </View>
  );
};

export default function JobDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { colors: themeColors } = useTheme();
  
  const [isLoading, setIsLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [generatingCover, setGeneratingCover] = useState(false);
  const [job, setJob] = useState<any>(null);
  const [coverLetter, setCoverLetter] = useState<string | null>(null);

  useEffect(() => {
    loadJob();
  }, [id]);

  const loadJob = async () => {
    setIsLoading(true);
    try {
      const response = await jobsAPI.getJob(id || '');
      setJob(response.data);
    } catch (error) {
      console.error('Failed to load job:', error);
      // Demo fallback
      setJob({
        id: id,
        title: 'Senior Software Engineer',
        company: 'Google',
        company_logo: null,
        location: 'Mountain View, CA (Remote)',
        salary: '$150,000 - $200,000',
        job_type: 'Full-time',
        posted_at: '2 days ago',
        match_score: 92,
        description: `We are looking for a Senior Software Engineer to join our team and help build the next generation of products. You will work on challenging problems at scale and collaborate with talented engineers.

**Responsibilities:**
• Design, develop, and maintain scalable systems
• Collaborate with cross-functional teams
• Mentor junior engineers
• Participate in code reviews and architectural discussions
• Drive best practices in software development

**Requirements:**
• 5+ years of software engineering experience
• Strong proficiency in Python, Java, or Go
• Experience with distributed systems
• Excellent problem-solving skills
• Strong communication skills`,
        required_skills: ['Python', 'Java', 'Distributed Systems', 'Cloud Computing', 'System Design'],
        nice_to_have: ['Kubernetes', 'Machine Learning', 'React'],
        benefits: [
          '💰 Competitive salary + equity',
          '🏥 Health, dental, vision insurance',
          '🏖️ Unlimited PTO',
          '🍼 Parental leave',
          '📚 Learning & development budget',
          '🏠 Remote work options',
        ],
        apply_url: 'https://careers.google.com/jobs',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      if (isSaved) {
        await jobsAPI.unsaveJob(id || '');
      } else {
        await jobsAPI.saveJob(id || '');
      }
      setIsSaved(!isSaved);
    } catch (error) {
      console.error('Save error:', error);
    }
  };

  const handleShare = async () => {
    try {
      await Share.share({
        message: `Check out this job: ${job?.title} at ${job?.company}\n\n${job?.apply_url || ''}`,
        title: `${job?.title} at ${job?.company}`,
      });
    } catch (error) {
      console.error('Share error:', error);
    }
  };

  const handleApply = async () => {
    if (job?.apply_url) {
      Linking.openURL(job.apply_url);
    }
  };

  const generateCoverLetter = async () => {
    setGeneratingCover(true);
    try {
      const response = await aiAPI.sendMessage(
        `Write a professional cover letter for this position: ${job?.title} at ${job?.company}. The job requires: ${job?.required_skills?.join(', ')}. Make it concise and impactful.`,
        'career'
      );
      setCoverLetter(response.data.response);
    } catch (error) {
      console.error('Cover letter error:', error);
      setCoverLetter('Failed to generate cover letter. Please try again.');
    } finally {
      setGeneratingCover(false);
    }
  };

  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: themeColors.background }]}>
        <ActivityIndicator size="large" color={colors.turquoise} />
      </View>
    );
  }

  if (!job) {
    return (
      <View style={[styles.errorContainer, { backgroundColor: themeColors.background }]}>
        <Text style={styles.errorIcon}>😕</Text>
        <Text style={[styles.errorText, { color: themeColors.text }]}>Job not found</Text>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={[styles.backLink, { color: colors.turquoise }]}>Go back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: themeColors.background }]}>
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={[styles.header, { backgroundColor: themeColors.surface }]}>
          <View style={styles.headerTop}>
            <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
              <Text style={[styles.backButtonText, { color: themeColors.text }]}>← Back</Text>
            </TouchableOpacity>
            <View style={styles.headerActions}>
              <TouchableOpacity onPress={handleSave} style={styles.iconButton}>
                <Text style={styles.actionIcon}>{isSaved ? '❤️' : '🤍'}</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={handleShare} style={styles.iconButton}>
                <Text style={styles.actionIcon}>📤</Text>
              </TouchableOpacity>
            </View>
          </View>
          
          <View style={styles.companyRow}>
            <View style={[styles.companyLogo, { backgroundColor: colors.turquoise + '20' }]}>
              <Text style={styles.companyLogoText}>{job.company?.charAt(0)}</Text>
            </View>
            <View style={styles.companyInfo}>
              <Text style={[styles.jobTitle, { color: themeColors.text }]}>{job.title}</Text>
              <Text style={[styles.companyName, { color: themeColors.textSecondary }]}>{job.company}</Text>
            </View>
          </View>
          
          {/* Meta Info */}
          <View style={styles.metaRow}>
            <View style={[styles.metaBadge, { backgroundColor: themeColors.background }]}>
              <Text style={styles.metaIcon}>📍</Text>
              <Text style={[styles.metaText, { color: themeColors.textSecondary }]}>{job.location}</Text>
            </View>
            <View style={[styles.metaBadge, { backgroundColor: themeColors.background }]}>
              <Text style={styles.metaIcon}>💰</Text>
              <Text style={[styles.metaText, { color: themeColors.textSecondary }]}>{job.salary}</Text>
            </View>
          </View>
          <View style={styles.metaRow}>
            <View style={[styles.metaBadge, { backgroundColor: colors.turquoise + '15' }]}>
              <Text style={[styles.metaText, { color: colors.turquoise }]}>{job.job_type}</Text>
            </View>
            <View style={[styles.metaBadge, { backgroundColor: themeColors.background }]}>
              <Text style={styles.metaIcon}>🕐</Text>
              <Text style={[styles.metaText, { color: themeColors.textSecondary }]}>{job.posted_at}</Text>
            </View>
          </View>
          
          {/* Match Score */}
          {job.match_score && (
            <View style={[styles.matchCard, { backgroundColor: colors.turquoise + '10' }]}>
              <View style={styles.matchHeader}>
                <Text style={[styles.matchLabel, { color: colors.turquoise }]}>Your Match Score</Text>
                <Text style={[styles.matchScore, { color: colors.turquoise }]}>{job.match_score}%</Text>
              </View>
              <View style={[styles.matchBarBg, { backgroundColor: colors.turquoise + '20' }]}>
                <View style={[styles.matchBarFill, { width: `${job.match_score}%` }]} />
              </View>
            </View>
          )}
        </View>

        {/* Description */}
        <Section title="About This Role">
          <Text style={[styles.description, { color: themeColors.textSecondary }]}>
            {job.description}
          </Text>
        </Section>

        {/* Required Skills */}
        {job.required_skills && (
          <Section title="Required Skills">
            <View style={styles.skillsGrid}>
              {job.required_skills.map((skill: string, index: number) => (
                <SkillBadge key={index} skill={skill} matched={index < 3} />
              ))}
            </View>
          </Section>
        )}

        {/* Nice to Have */}
        {job.nice_to_have && (
          <Section title="Nice to Have">
            <View style={styles.skillsGrid}>
              {job.nice_to_have.map((skill: string, index: number) => (
                <SkillBadge key={index} skill={skill} />
              ))}
            </View>
          </Section>
        )}

        {/* Benefits */}
        {job.benefits && (
          <Section title="Benefits">
            <View style={[styles.benefitsList, { backgroundColor: themeColors.surface }]}>
              {job.benefits.map((benefit: string, index: number) => (
                <Text key={index} style={[styles.benefitItem, { color: themeColors.text }]}>
                  {benefit}
                </Text>
              ))}
            </View>
          </Section>
        )}

        {/* AI Cover Letter */}
        <Section title="AI Assistant">
          <TouchableOpacity 
            style={[styles.aiCard, { backgroundColor: themeColors.surface }]}
            onPress={generateCoverLetter}
            disabled={generatingCover}
          >
            <LinearGradient
              colors={[colors.turquoise + '10', colors.pink + '05']}
              style={styles.aiCardGradient}
            >
              <Text style={styles.aiIcon}>✨</Text>
              <View style={styles.aiContent}>
                <Text style={[styles.aiTitle, { color: themeColors.text }]}>Generate Cover Letter</Text>
                <Text style={[styles.aiDesc, { color: themeColors.textSecondary }]}>
                  AI-powered cover letter tailored for this job
                </Text>
              </View>
              {generatingCover ? (
                <ActivityIndicator size="small" color={colors.turquoise} />
              ) : (
                <Text style={styles.aiArrow}>→</Text>
              )}
            </LinearGradient>
          </TouchableOpacity>
          
          {coverLetter && (
            <View style={[styles.coverLetterCard, { backgroundColor: themeColors.surface }]}>
              <Text style={[styles.coverLetterTitle, { color: colors.turquoise }]}>
                ✨ Generated Cover Letter
              </Text>
              <Text style={[styles.coverLetterText, { color: themeColors.text }]}>
                {coverLetter}
              </Text>
            </View>
          )}
        </Section>

        {/* Spacer for bottom button */}
        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Apply Button */}
      <View style={[styles.applyContainer, { backgroundColor: themeColors.background }]}>
        <TouchableOpacity 
          style={styles.applyButton}
          onPress={handleApply}
          disabled={isApplying}
        >
          <LinearGradient
            colors={[colors.turquoise, colors.turquoiseLight]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.applyGradient}
          >
            <Text style={styles.applyText}>
              {isApplying ? 'Opening...' : 'Apply Now →'}
            </Text>
          </LinearGradient>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scrollView: { flex: 1 },
  content: { paddingBottom: spacing.xl },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  errorContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  errorIcon: { fontSize: 48, marginBottom: spacing.md },
  errorText: { fontSize: fontSize.lg, marginBottom: spacing.md },
  backLink: { fontSize: fontSize.base, fontWeight: fontWeight.medium },
  
  header: { padding: spacing.md, ...shadows.sm },
  headerTop: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  backButton: { padding: spacing.xs },
  backButtonText: { fontSize: fontSize.base, fontWeight: fontWeight.medium },
  headerActions: { flexDirection: 'row', gap: spacing.sm },
  iconButton: { padding: spacing.xs },
  actionIcon: { fontSize: 24 },
  
  companyRow: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.md },
  companyLogo: { 
    width: 56, 
    height: 56, 
    borderRadius: borderRadius.lg, 
    justifyContent: 'center', 
    alignItems: 'center',
    marginRight: spacing.md,
  },
  companyLogoText: { fontSize: fontSize['2xl'], fontWeight: fontWeight.bold, color: colors.turquoise },
  companyInfo: { flex: 1 },
  jobTitle: { fontSize: fontSize.xl, fontWeight: fontWeight.bold, marginBottom: 2 },
  companyName: { fontSize: fontSize.base },
  
  metaRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginBottom: spacing.sm },
  metaBadge: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    paddingHorizontal: spacing.sm, 
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.sm,
  },
  metaIcon: { fontSize: 12, marginRight: 4 },
  metaText: { fontSize: fontSize.sm },
  
  matchCard: { 
    padding: spacing.md, 
    borderRadius: borderRadius.lg, 
    marginTop: spacing.md,
  },
  matchHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  matchLabel: { fontSize: fontSize.sm, fontWeight: fontWeight.medium },
  matchScore: { fontSize: fontSize.xl, fontWeight: fontWeight.bold },
  matchBarBg: { height: 8, borderRadius: 4 },
  matchBarFill: { 
    height: 8, 
    borderRadius: 4, 
    backgroundColor: colors.turquoise,
  },
  
  section: { padding: spacing.md },
  sectionTitle: { 
    fontSize: fontSize.lg, 
    fontWeight: fontWeight.semibold, 
    marginBottom: spacing.md,
  },
  description: { fontSize: fontSize.base, lineHeight: 24 },
  
  skillsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  skillBadge: { 
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md, 
    paddingVertical: spacing.sm, 
    borderRadius: borderRadius.full,
    borderWidth: 1,
  },
  matchIcon: { fontSize: 12, color: colors.turquoise },
  skillText: { fontSize: fontSize.sm },
  
  benefitsList: { 
    padding: spacing.md, 
    borderRadius: borderRadius.lg,
    ...shadows.sm,
  },
  benefitItem: { 
    fontSize: fontSize.base, 
    marginBottom: spacing.sm,
    lineHeight: 24,
  },
  
  aiCard: { borderRadius: borderRadius.lg, overflow: 'hidden', ...shadows.sm },
  aiCardGradient: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    padding: spacing.md,
  },
  aiIcon: { fontSize: 32, marginRight: spacing.md },
  aiContent: { flex: 1 },
  aiTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  aiDesc: { fontSize: fontSize.sm, marginTop: 2 },
  aiArrow: { fontSize: 20, color: colors.turquoise },
  
  coverLetterCard: { 
    marginTop: spacing.md, 
    padding: spacing.md, 
    borderRadius: borderRadius.lg,
    ...shadows.sm,
  },
  coverLetterTitle: { 
    fontSize: fontSize.sm, 
    fontWeight: fontWeight.semibold, 
    marginBottom: spacing.sm,
  },
  coverLetterText: { fontSize: fontSize.base, lineHeight: 24 },
  
  applyContainer: { 
    position: 'absolute', 
    bottom: 0, 
    left: 0, 
    right: 0, 
    padding: spacing.md,
    paddingBottom: spacing.xl,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.05)',
  },
  applyButton: { borderRadius: borderRadius.lg, overflow: 'hidden' },
  applyGradient: { paddingVertical: spacing.md, alignItems: 'center' },
  applyText: { 
    color: colors.white, 
    fontSize: fontSize.lg, 
    fontWeight: fontWeight.semibold,
  },
});
