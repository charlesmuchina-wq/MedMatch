/**
 * MedMatch Mobile - AI Tools Screen
 * KARAU Dragon AI Assistant, Interview Prep, Voice Coach, Cover Letter
 */
import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  FlatList,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../../constants/theme';
import { aiAPI } from '../../services/api';

// AI Tool Card Component
const AIToolCard = ({
  icon,
  title,
  description,
  gradientColors,
  onPress,
  badge,
}: {
  icon: string;
  title: string;
  description: string;
  gradientColors: [string, string];
  onPress: () => void;
  badge?: string;
}) => (
  <TouchableOpacity style={styles.toolCard} onPress={onPress} activeOpacity={0.8}>
    <LinearGradient
      colors={gradientColors}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.toolCardGradient}
    >
      <View style={styles.batikOverlay}>
        <View style={[styles.batikCircle, { top: -15, right: 10 }]} />
        <View style={[styles.batikCircle, { bottom: -20, left: 20, width: 40, height: 40 }]} />
      </View>
      <Text style={styles.toolIcon}>{icon}</Text>
      <Text style={styles.toolTitle}>{title}</Text>
      <Text style={styles.toolDesc}>{description}</Text>
      {badge && (
        <View style={styles.toolBadge}>
          <Text style={styles.toolBadgeText}>{badge}</Text>
        </View>
      )}
    </LinearGradient>
  </TouchableOpacity>
);

// Chat Message Component
const ChatMessage = ({
  message,
  isUser,
}: {
  message: { text: string; timestamp: Date };
  isUser: boolean;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <View style={[
      styles.messageContainer,
      isUser ? styles.userMessageContainer : styles.aiMessageContainer
    ]}>
      {!isUser && <Text style={styles.aiAvatar}>🐉</Text>}
      <View style={[
        styles.messageBubble,
        isUser 
          ? { backgroundColor: colors.turquoise }
          : { backgroundColor: themeColors.surface }
      ]}>
        <Text style={[
          styles.messageText,
          { color: isUser ? colors.white : themeColors.text }
        ]}>
          {message.text}
        </Text>
      </View>
    </View>
  );
};

// Interview Question Card
const QuestionCard = ({
  question,
  type,
  tip,
  onGenerate,
  isGenerating,
}: {
  question: string;
  type: string;
  tip?: string;
  onGenerate: () => void;
  isGenerating: boolean;
}) => {
  const { colors: themeColors } = useTheme();
  
  const typeColors: Record<string, string> = {
    Behavioral: colors.pink,
    Technical: colors.turquoise,
    Situational: colors.gold,
  };
  
  return (
    <View style={[styles.questionCard, { backgroundColor: themeColors.surface }]}>
      <View style={styles.questionHeader}>
        <View style={[styles.questionTypeBadge, { backgroundColor: (typeColors[type] || colors.turquoise) + '20' }]}>
          <Text style={[styles.questionTypeText, { color: typeColors[type] || colors.turquoise }]}>
            {type}
          </Text>
        </View>
      </View>
      <Text style={[styles.questionText, { color: themeColors.text }]}>{question}</Text>
      {tip && (
        <Text style={[styles.questionTip, { color: themeColors.textSecondary }]}>
          💡 {tip}
        </Text>
      )}
      <TouchableOpacity 
        style={styles.generateButton}
        onPress={onGenerate}
        disabled={isGenerating}
      >
        <LinearGradient
          colors={[colors.turquoise, colors.turquoiseLight]}
          style={styles.generateButtonGradient}
        >
          {isGenerating ? (
            <ActivityIndicator size="small" color={colors.white} />
          ) : (
            <Text style={styles.generateButtonText}>✨ Generate Answer</Text>
          )}
        </LinearGradient>
      </TouchableOpacity>
    </View>
  );
};

type ViewMode = 'tools' | 'chat' | 'interview' | 'voiceCoach';

export default function AIToolsScreen() {
  const { colors: themeColors } = useTheme();
  const { user } = useAuth();
  const scrollViewRef = useRef<ScrollView>(null);
  
  const [viewMode, setViewMode] = useState<ViewMode>('tools');
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean; timestamp: Date }>>([
    { text: "Hello! I'm KARAU Dragon, your AI career assistant. How can I help you today?", isUser: false, timestamp: new Date() }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Interview Prep State
  const [jobTitle, setJobTitle] = useState('');
  const [questions, setQuestions] = useState<any[]>([]);
  const [generatingQuestions, setGeneratingQuestions] = useState(false);
  const [generatingAnswer, setGeneratingAnswer] = useState<string | null>(null);
  const [generatedAnswers, setGeneratedAnswers] = useState<Record<string, string>>({});

  const sendMessage = async () => {
    if (!chatInput.trim() || isLoading) return;
    
    const userMessage = { text: chatInput.trim(), isUser: true, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setIsLoading(true);
    
    try {
      const response = await aiAPI.sendMessage(chatInput, 'general');
      const aiResponse = { 
        text: response.data.response || "I'm sorry, I couldn't process that request.", 
        isUser: false, 
        timestamp: new Date() 
      };
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        text: "Sorry, I'm having trouble connecting. Please try again.", 
        isUser: false, 
        timestamp: new Date() 
      }]);
    } finally {
      setIsLoading(false);
    }
    
    setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);
  };

  const generateInterviewQuestions = async () => {
    if (!jobTitle.trim()) return;
    
    setGeneratingQuestions(true);
    try {
      const response = await aiAPI.generateQuestions(jobTitle, 5);
      setQuestions(response.data.questions || []);
    } catch (error) {
      console.error('Generate questions error:', error);
      // Demo fallback
      setQuestions([
        { question: 'Tell me about yourself and your experience.', type: 'Behavioral', tip: 'Focus on relevant experience' },
        { question: 'Why are you interested in this role?', type: 'Behavioral', tip: 'Connect your goals to the company' },
        { question: 'Describe a challenging project you worked on.', type: 'Situational', tip: 'Use the STAR method' },
        { question: 'What are your technical strengths?', type: 'Technical', tip: 'Be specific with examples' },
        { question: 'Where do you see yourself in 5 years?', type: 'Behavioral', tip: 'Show growth mindset' },
      ]);
    } finally {
      setGeneratingQuestions(false);
    }
  };

  const generateAnswer = async (question: string) => {
    setGeneratingAnswer(question);
    try {
      const response = await aiAPI.sendMessage(
        `Generate a strong interview answer for: "${question}" for a ${jobTitle} position. Use the STAR method if applicable.`,
        'interview'
      );
      setGeneratedAnswers(prev => ({
        ...prev,
        [question]: response.data.response || 'Answer not available'
      }));
    } catch (error) {
      console.error('Generate answer error:', error);
      setGeneratedAnswers(prev => ({
        ...prev,
        [question]: 'Failed to generate answer. Please try again.'
      }));
    } finally {
      setGeneratingAnswer(null);
    }
  };

  const renderToolsView = () => (
    <ScrollView 
      style={styles.content}
      contentContainerStyle={styles.toolsGrid}
      showsVerticalScrollIndicator={false}
    >
      {/* Hero Section */}
      <LinearGradient
        colors={[colors.turquoise, colors.turquoiseLight]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.heroCard}
      >
        <View style={styles.batikOverlay}>
          <View style={[styles.batikCircle, { top: -30, right: 30, width: 80, height: 80, backgroundColor: colors.pinkLight + '15' }]} />
          <View style={[styles.batikCircle, { bottom: -20, left: 50, backgroundColor: colors.coral + '10' }]} />
        </View>
        <Text style={styles.heroIcon}>🐉</Text>
        <Text style={styles.heroTitle}>KARAU Dragon AI</Text>
        <Text style={styles.heroSubtitle}>Your intelligent career companion</Text>
        <TouchableOpacity 
          style={styles.heroButton}
          onPress={() => setViewMode('chat')}
        >
          <Text style={styles.heroButtonText}>Start Chatting →</Text>
        </TouchableOpacity>
      </LinearGradient>

      {/* AI Tools Grid */}
      <Text style={[styles.sectionTitle, { color: themeColors.text }]}>AI-Powered Tools</Text>
      
      <View style={styles.toolsRow}>
        <AIToolCard
          icon="🎯"
          title="Interview Prep"
          description="AI-generated questions & answers"
          gradientColors={[colors.turquoise, colors.turquoiseDark]}
          onPress={() => setViewMode('interview')}
          badge="Popular"
        />
        <AIToolCard
          icon="🎤"
          title="Voice Coach"
          description="Improve your delivery"
          gradientColors={[colors.pink, colors.pinkDark]}
          onPress={() => setViewMode('voiceCoach')}
        />
      </View>
      
      <View style={styles.toolsRow}>
        <AIToolCard
          icon="✉️"
          title="Cover Letter"
          description="AI-written letters"
          gradientColors={[colors.coral, colors.red]}
          onPress={() => {}}
        />
        <AIToolCard
          icon="📊"
          title="Success Predictor"
          description="Callback probability"
          gradientColors={[colors.gold, '#b8860b']}
          onPress={() => {}}
        />
      </View>

      {/* Quick Tips */}
      <View style={[styles.tipsCard, { backgroundColor: themeColors.surface }]}>
        <Text style={styles.tipsIcon}>💡</Text>
        <Text style={[styles.tipsTitle, { color: themeColors.text }]}>Pro Tip</Text>
        <Text style={[styles.tipsText, { color: themeColors.textSecondary }]}>
          Use KARAU Dragon AI to practice mock interviews. The more you practice, the more confident you'll feel!
        </Text>
      </View>
    </ScrollView>
  );

  const renderChatView = () => (
    <KeyboardAvoidingView 
      style={styles.chatContainer}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={100}
    >
      {/* Back Button */}
      <TouchableOpacity 
        style={[styles.backButton, { backgroundColor: themeColors.surface }]}
        onPress={() => setViewMode('tools')}
      >
        <Text style={[styles.backButtonText, { color: themeColors.text }]}>← Back to Tools</Text>
      </TouchableOpacity>
      
      {/* Chat Messages */}
      <ScrollView 
        ref={scrollViewRef}
        style={styles.chatMessages}
        contentContainerStyle={styles.chatMessagesContent}
        showsVerticalScrollIndicator={false}
      >
        {messages.map((msg, index) => (
          <ChatMessage key={index} message={msg} isUser={msg.isUser} />
        ))}
        {isLoading && (
          <View style={styles.loadingIndicator}>
            <ActivityIndicator size="small" color={colors.turquoise} />
            <Text style={[styles.loadingText, { color: themeColors.textSecondary }]}>
              KARAU is thinking...
            </Text>
          </View>
        )}
      </ScrollView>
      
      {/* Chat Input */}
      <View style={[styles.chatInputContainer, { backgroundColor: themeColors.surface }]}>
        <TextInput
          style={[styles.chatInput, { backgroundColor: themeColors.background, color: themeColors.text }]}
          placeholder="Ask KARAU anything..."
          placeholderTextColor={themeColors.textTertiary}
          value={chatInput}
          onChangeText={setChatInput}
          multiline
          maxLength={500}
        />
        <TouchableOpacity 
          style={[styles.sendButton, { opacity: chatInput.trim() ? 1 : 0.5 }]}
          onPress={sendMessage}
          disabled={!chatInput.trim() || isLoading}
        >
          <LinearGradient
            colors={[colors.turquoise, colors.turquoiseLight]}
            style={styles.sendButtonGradient}
          >
            <Text style={styles.sendButtonText}>↑</Text>
          </LinearGradient>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );

  const renderInterviewView = () => (
    <ScrollView 
      style={styles.content}
      contentContainerStyle={styles.interviewContent}
      showsVerticalScrollIndicator={false}
    >
      {/* Back Button */}
      <TouchableOpacity 
        style={[styles.backButton, { backgroundColor: themeColors.surface }]}
        onPress={() => setViewMode('tools')}
      >
        <Text style={[styles.backButtonText, { color: themeColors.text }]}>← Back to Tools</Text>
      </TouchableOpacity>
      
      {/* Job Title Input */}
      <View style={[styles.inputCard, { backgroundColor: themeColors.surface }]}>
        <Text style={[styles.inputLabel, { color: themeColors.text }]}>Target Position</Text>
        <TextInput
          style={[styles.textInput, { backgroundColor: themeColors.background, color: themeColors.text }]}
          placeholder="e.g., Software Engineer"
          placeholderTextColor={themeColors.textTertiary}
          value={jobTitle}
          onChangeText={setJobTitle}
        />
        <TouchableOpacity 
          style={styles.generateQuestionsButton}
          onPress={generateInterviewQuestions}
          disabled={generatingQuestions || !jobTitle.trim()}
        >
          <LinearGradient
            colors={[colors.turquoise, colors.turquoiseLight]}
            style={styles.generateQuestionsGradient}
          >
            {generatingQuestions ? (
              <ActivityIndicator size="small" color={colors.white} />
            ) : (
              <Text style={styles.generateQuestionsText}>✨ Generate Questions</Text>
            )}
          </LinearGradient>
        </TouchableOpacity>
      </View>

      {/* Questions List */}
      {questions.length > 0 && (
        <>
          <Text style={[styles.sectionTitle, { color: themeColors.text }]}>
            Interview Questions ({questions.length})
          </Text>
          {questions.map((q, index) => (
            <View key={index}>
              <QuestionCard
                question={q.question}
                type={q.type}
                tip={q.tip}
                onGenerate={() => generateAnswer(q.question)}
                isGenerating={generatingAnswer === q.question}
              />
              {generatedAnswers[q.question] && (
                <View style={[styles.answerCard, { backgroundColor: colors.turquoise + '10' }]}>
                  <Text style={[styles.answerLabel, { color: colors.turquoise }]}>✨ AI-Generated Answer</Text>
                  <Text style={[styles.answerText, { color: themeColors.text }]}>
                    {generatedAnswers[q.question]}
                  </Text>
                </View>
              )}
            </View>
          ))}
        </>
      )}
    </ScrollView>
  );

  const renderVoiceCoachView = () => (
    <ScrollView 
      style={styles.content}
      contentContainerStyle={styles.voiceCoachContent}
      showsVerticalScrollIndicator={false}
    >
      {/* Back Button */}
      <TouchableOpacity 
        style={[styles.backButton, { backgroundColor: themeColors.surface }]}
        onPress={() => setViewMode('tools')}
      >
        <Text style={[styles.backButtonText, { color: themeColors.text }]}>← Back to Tools</Text>
      </TouchableOpacity>
      
      {/* Voice Coach Hero */}
      <LinearGradient
        colors={[colors.pink, colors.pinkDark]}
        style={styles.voiceHero}
      >
        <Text style={styles.voiceHeroIcon}>🎤</Text>
        <Text style={styles.voiceHeroTitle}>Voice Coach</Text>
        <Text style={styles.voiceHeroSubtitle}>Practice your interview delivery</Text>
      </LinearGradient>
      
      {/* Features */}
      <View style={[styles.featureCard, { backgroundColor: themeColors.surface }]}>
        <Text style={styles.featureIcon}>🎯</Text>
        <Text style={[styles.featureTitle, { color: themeColors.text }]}>Real-time Feedback</Text>
        <Text style={[styles.featureDesc, { color: themeColors.textSecondary }]}>
          Get instant feedback on pace, clarity, and filler words
        </Text>
      </View>
      
      <View style={[styles.featureCard, { backgroundColor: themeColors.surface }]}>
        <Text style={styles.featureIcon}>📊</Text>
        <Text style={[styles.featureTitle, { color: themeColors.text }]}>Speech Analysis</Text>
        <Text style={[styles.featureDesc, { color: themeColors.textSecondary }]}>
          Track your progress over multiple practice sessions
        </Text>
      </View>
      
      <View style={[styles.featureCard, { backgroundColor: themeColors.surface }]}>
        <Text style={styles.featureIcon}>💡</Text>
        <Text style={[styles.featureTitle, { color: themeColors.text }]}>Pro Tips</Text>
        <Text style={[styles.featureDesc, { color: themeColors.textSecondary }]}>
          Learn techniques from professional speakers
        </Text>
      </View>
      
      <TouchableOpacity style={styles.startPracticeButton}>
        <LinearGradient
          colors={[colors.pink, colors.pinkDark]}
          style={styles.startPracticeGradient}
        >
          <Text style={styles.startPracticeText}>🎤 Start Practice Session</Text>
        </LinearGradient>
      </TouchableOpacity>
    </ScrollView>
  );

  return (
    <View style={[styles.container, { backgroundColor: themeColors.background }]}>
      {viewMode === 'tools' && renderToolsView()}
      {viewMode === 'chat' && renderChatView()}
      {viewMode === 'interview' && renderInterviewView()}
      {viewMode === 'voiceCoach' && renderVoiceCoachView()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { flex: 1 },
  toolsGrid: { padding: spacing.md, paddingBottom: spacing['2xl'] },
  heroCard: { 
    padding: spacing.xl, 
    borderRadius: borderRadius.xl, 
    alignItems: 'center',
    marginBottom: spacing.lg,
    overflow: 'hidden',
  },
  batikOverlay: { ...StyleSheet.absoluteFillObject },
  batikCircle: { 
    position: 'absolute', 
    width: 60, 
    height: 60, 
    borderRadius: 30,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  heroIcon: { fontSize: 48, marginBottom: spacing.sm },
  heroTitle: { fontSize: fontSize['2xl'], fontWeight: fontWeight.bold, color: colors.white },
  heroSubtitle: { fontSize: fontSize.base, color: colors.white + 'cc', marginBottom: spacing.md },
  heroButton: { 
    backgroundColor: colors.white + '20', 
    paddingHorizontal: spacing.lg, 
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.full,
  },
  heroButtonText: { color: colors.white, fontWeight: fontWeight.semibold },
  sectionTitle: { 
    fontSize: fontSize.lg, 
    fontWeight: fontWeight.semibold, 
    marginTop: spacing.lg, 
    marginBottom: spacing.md,
  },
  toolsRow: { flexDirection: 'row', gap: spacing.md, marginBottom: spacing.md },
  toolCard: { flex: 1, height: 140, borderRadius: borderRadius.lg, overflow: 'hidden' },
  toolCardGradient: { flex: 1, padding: spacing.md, justifyContent: 'space-between', overflow: 'hidden' },
  toolIcon: { fontSize: 32 },
  toolTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, color: colors.white },
  toolDesc: { fontSize: fontSize.xs, color: colors.white + 'cc' },
  toolBadge: { 
    position: 'absolute', 
    top: spacing.sm, 
    right: spacing.sm,
    backgroundColor: colors.white + '30',
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: borderRadius.sm,
  },
  toolBadgeText: { fontSize: fontSize.xs, color: colors.white, fontWeight: fontWeight.medium },
  tipsCard: { 
    padding: spacing.md, 
    borderRadius: borderRadius.lg, 
    marginTop: spacing.md,
    ...shadows.sm,
  },
  tipsIcon: { fontSize: 24, marginBottom: spacing.xs },
  tipsTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, marginBottom: spacing.xs },
  tipsText: { fontSize: fontSize.sm, lineHeight: 20 },
  
  // Chat styles
  chatContainer: { flex: 1 },
  backButton: { 
    padding: spacing.md, 
    marginHorizontal: spacing.md, 
    marginTop: spacing.sm,
    borderRadius: borderRadius.lg,
    ...shadows.sm,
  },
  backButtonText: { fontSize: fontSize.base, fontWeight: fontWeight.medium },
  chatMessages: { flex: 1, paddingHorizontal: spacing.md },
  chatMessagesContent: { paddingVertical: spacing.md },
  messageContainer: { marginBottom: spacing.md, flexDirection: 'row', alignItems: 'flex-end' },
  userMessageContainer: { justifyContent: 'flex-end' },
  aiMessageContainer: { justifyContent: 'flex-start' },
  aiAvatar: { fontSize: 24, marginRight: spacing.sm },
  messageBubble: { 
    maxWidth: '75%', 
    padding: spacing.md, 
    borderRadius: borderRadius.lg,
    ...shadows.sm,
  },
  messageText: { fontSize: fontSize.base, lineHeight: 22 },
  loadingIndicator: { flexDirection: 'row', alignItems: 'center', paddingVertical: spacing.md },
  loadingText: { marginLeft: spacing.sm, fontSize: fontSize.sm },
  chatInputContainer: { 
    flexDirection: 'row', 
    alignItems: 'flex-end', 
    padding: spacing.md,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.05)',
  },
  chatInput: { 
    flex: 1, 
    padding: spacing.md, 
    borderRadius: borderRadius.lg, 
    maxHeight: 100,
    fontSize: fontSize.base,
  },
  sendButton: { marginLeft: spacing.sm },
  sendButtonGradient: { 
    width: 44, 
    height: 44, 
    borderRadius: 22, 
    justifyContent: 'center', 
    alignItems: 'center',
  },
  sendButtonText: { fontSize: 20, color: colors.white, fontWeight: fontWeight.bold },
  
  // Interview styles
  interviewContent: { padding: spacing.md, paddingBottom: spacing['2xl'] },
  inputCard: { padding: spacing.md, borderRadius: borderRadius.lg, marginTop: spacing.md, ...shadows.sm },
  inputLabel: { fontSize: fontSize.sm, fontWeight: fontWeight.semibold, marginBottom: spacing.sm },
  textInput: { 
    padding: spacing.md, 
    borderRadius: borderRadius.md, 
    fontSize: fontSize.base,
    marginBottom: spacing.md,
  },
  generateQuestionsButton: { borderRadius: borderRadius.lg, overflow: 'hidden' },
  generateQuestionsGradient: { paddingVertical: spacing.md, alignItems: 'center' },
  generateQuestionsText: { color: colors.white, fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  questionCard: { padding: spacing.md, borderRadius: borderRadius.lg, marginBottom: spacing.md, ...shadows.sm },
  questionHeader: { flexDirection: 'row', marginBottom: spacing.sm },
  questionTypeBadge: { paddingHorizontal: spacing.sm, paddingVertical: spacing.xs, borderRadius: borderRadius.sm },
  questionTypeText: { fontSize: fontSize.xs, fontWeight: fontWeight.semibold },
  questionText: { fontSize: fontSize.base, lineHeight: 24, marginBottom: spacing.sm },
  questionTip: { fontSize: fontSize.sm, fontStyle: 'italic', marginBottom: spacing.md },
  generateButton: { borderRadius: borderRadius.md, overflow: 'hidden' },
  generateButtonGradient: { paddingVertical: spacing.sm, alignItems: 'center' },
  generateButtonText: { color: colors.white, fontSize: fontSize.sm, fontWeight: fontWeight.semibold },
  answerCard: { padding: spacing.md, borderRadius: borderRadius.lg, marginBottom: spacing.md, marginTop: -spacing.sm },
  answerLabel: { fontSize: fontSize.sm, fontWeight: fontWeight.semibold, marginBottom: spacing.sm },
  answerText: { fontSize: fontSize.base, lineHeight: 24 },
  
  // Voice Coach styles
  voiceCoachContent: { padding: spacing.md, paddingBottom: spacing['2xl'] },
  voiceHero: { 
    padding: spacing.xl, 
    borderRadius: borderRadius.xl, 
    alignItems: 'center',
    marginTop: spacing.md,
    marginBottom: spacing.lg,
  },
  voiceHeroIcon: { fontSize: 48, marginBottom: spacing.sm },
  voiceHeroTitle: { fontSize: fontSize['2xl'], fontWeight: fontWeight.bold, color: colors.white },
  voiceHeroSubtitle: { fontSize: fontSize.base, color: colors.white + 'cc' },
  featureCard: { 
    padding: spacing.md, 
    borderRadius: borderRadius.lg, 
    marginBottom: spacing.md,
    ...shadows.sm,
  },
  featureIcon: { fontSize: 28, marginBottom: spacing.sm },
  featureTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, marginBottom: spacing.xs },
  featureDesc: { fontSize: fontSize.sm, lineHeight: 20 },
  startPracticeButton: { borderRadius: borderRadius.lg, overflow: 'hidden', marginTop: spacing.md },
  startPracticeGradient: { paddingVertical: spacing.md, alignItems: 'center' },
  startPracticeText: { color: colors.white, fontSize: fontSize.base, fontWeight: fontWeight.semibold },
});
