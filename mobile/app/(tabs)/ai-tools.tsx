/**
 * MedMatch Mobile - AI Tools Screen
 * Access to all AI-powered features
 */
import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { router } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../contexts/ThemeContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../../constants/theme';

// AI Tool Card
const AIToolCard = ({
  title,
  description,
  icon,
  gradientColors,
  features,
  onPress,
}: {
  title: string;
  description: string;
  icon: string;
  gradientColors: [string, string];
  features: string[];
  onPress: () => void;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <TouchableOpacity style={[styles.toolCard, { backgroundColor: themeColors.surface }]} onPress={onPress} activeOpacity={0.8}>
      <LinearGradient
        colors={gradientColors}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.toolIconContainer}
      >
        <Text style={styles.toolIcon}>{icon}</Text>
      </LinearGradient>
      
      <View style={styles.toolContent}>
        <Text style={[styles.toolTitle, { color: themeColors.text }]}>{title}</Text>
        <Text style={[styles.toolDescription, { color: themeColors.textSecondary }]}>{description}</Text>
        
        <View style={styles.featuresList}>
          {features.map((feature, index) => (
            <View key={index} style={styles.featureItem}>
              <Text style={[styles.featureDot, { color: gradientColors[0] }]}>•</Text>
              <Text style={[styles.featureText, { color: themeColors.textTertiary }]}>{feature}</Text>
            </View>
          ))}
        </View>
      </View>
      
      <Text style={[styles.chevron, { color: gradientColors[0] }]}>›</Text>
    </TouchableOpacity>
  );
};

export default function AIToolsScreen() {
  const { colors: themeColors } = useTheme();

  const tools = [
    {
      title: 'KARAU Dragon AI',
      description: 'Your personal AI career assistant',
      icon: '🐉',
      gradientColors: [colors.turquoise, colors.turquoiseDark] as [string, string],
      features: ['Job search advice', 'Resume tips', 'Career guidance'],
      route: '/ai-assistant',
    },
    {
      title: 'Interview Prep',
      description: 'Practice with AI-generated questions',
      icon: '🎯',
      gradientColors: [colors.pink, colors.pinkDark] as [string, string],
      features: ['Role-specific questions', 'Answer coaching', 'Feedback analysis'],
      route: '/interview/practice',
    },
    {
      title: 'Voice Coach',
      description: 'Improve your speaking skills',
      icon: '🎤',
      gradientColors: [colors.coral, colors.red] as [string, string],
      features: ['Pace analysis', 'Filler word detection', 'Confidence scoring'],
      route: '/voice-coach',
    },
    {
      title: 'Video Interview',
      description: 'Practice with facial analysis',
      icon: '📹',
      gradientColors: [colors.gold, '#b8860b'] as [string, string],
      features: ['Eye contact tracking', 'Expression analysis', 'Body language tips'],
      route: '/video-interview',
    },
    {
      title: 'Cover Letter',
      description: 'AI-generated cover letters',
      icon: '✉️',
      gradientColors: ['#8b5cf6', '#6d28d9'] as [string, string],
      features: ['Job-specific content', 'Multiple styles', 'Easy editing'],
      route: '/cover-letter',
    },
    {
      title: 'Meeting Notes',
      description: 'Transcribe and summarize interviews',
      icon: '📝',
      gradientColors: ['#3b82f6', '#1d4ed8'] as [string, string],
      features: ['Real-time transcription', 'AI summaries', 'Action items'],
      route: '/meeting-notes',
    },
  ];

  return (
    <ScrollView style={[styles.container, { backgroundColor: themeColors.background }]} contentContainerStyle={styles.content}>
      {/* Header */}
      <LinearGradient
        colors={[colors.turquoise, colors.turquoiseLight]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.header}
      >
        <View style={styles.batikOverlay}>
          <View style={[styles.batikCircle, { top: -10, right: 20, backgroundColor: colors.pinkLight + '20' }]} />
          <View style={[styles.batikCircle, { bottom: -20, left: 30, backgroundColor: colors.coral + '15' }]} />
        </View>
        <Text style={styles.headerIcon}>✨</Text>
        <Text style={styles.headerTitle}>AI-Powered Tools</Text>
        <Text style={styles.headerSubtitle}>
          Supercharge your job search with intelligent assistance
        </Text>
      </LinearGradient>

      {/* Tools List */}
      <View style={styles.toolsList}>
        {tools.map((tool, index) => (
          <AIToolCard
            key={index}
            title={tool.title}
            description={tool.description}
            icon={tool.icon}
            gradientColors={tool.gradientColors}
            features={tool.features}
            onPress={() => {
              // For now, just show alert. In real app, navigate to route
              // router.push(tool.route);
            }}
          />
        ))}
      </View>

      {/* Premium Banner */}
      <TouchableOpacity style={styles.premiumBanner}>
        <LinearGradient
          colors={[colors.pink, colors.rose]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.premiumGradient}
        >
          <Text style={styles.premiumIcon}>👑</Text>
          <View style={styles.premiumContent}>
            <Text style={styles.premiumTitle}>Upgrade to Premium</Text>
            <Text style={styles.premiumSubtitle}>Unlock all AI features with unlimited usage</Text>
          </View>
          <Text style={styles.premiumArrow}>→</Text>
        </LinearGradient>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { paddingBottom: spacing.xl },
  header: { margin: spacing.md, padding: spacing.lg, borderRadius: borderRadius.xl, alignItems: 'center', overflow: 'hidden' },
  batikOverlay: { ...StyleSheet.absoluteFillObject },
  batikCircle: { position: 'absolute', width: 60, height: 60, borderRadius: 30 },
  headerIcon: { fontSize: 40, marginBottom: spacing.sm },
  headerTitle: { fontSize: fontSize.xl, fontWeight: fontWeight.bold, color: colors.white, marginBottom: spacing.xs },
  headerSubtitle: { fontSize: fontSize.sm, color: colors.white + 'cc', textAlign: 'center' },
  toolsList: { paddingHorizontal: spacing.md, gap: spacing.md },
  toolCard: { flexDirection: 'row', alignItems: 'center', padding: spacing.md, borderRadius: borderRadius.xl, ...shadows.sm },
  toolIconContainer: { width: 56, height: 56, borderRadius: borderRadius.lg, justifyContent: 'center', alignItems: 'center', marginRight: spacing.md },
  toolIcon: { fontSize: 28 },
  toolContent: { flex: 1 },
  toolTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, marginBottom: 2 },
  toolDescription: { fontSize: fontSize.sm, marginBottom: spacing.sm },
  featuresList: { gap: 2 },
  featureItem: { flexDirection: 'row', alignItems: 'center' },
  featureDot: { fontSize: fontSize.sm, marginRight: spacing.xs },
  featureText: { fontSize: fontSize.xs },
  chevron: { fontSize: 28, marginLeft: spacing.sm },
  premiumBanner: { margin: spacing.md, borderRadius: borderRadius.xl, overflow: 'hidden' },
  premiumGradient: { flexDirection: 'row', alignItems: 'center', padding: spacing.md },
  premiumIcon: { fontSize: 32, marginRight: spacing.md },
  premiumContent: { flex: 1 },
  premiumTitle: { fontSize: fontSize.base, fontWeight: fontWeight.bold, color: colors.white },
  premiumSubtitle: { fontSize: fontSize.sm, color: colors.white + 'cc' },
  premiumArrow: { fontSize: 24, color: colors.white },
});
