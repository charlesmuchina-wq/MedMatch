/**
 * MedMatch Mobile - Messages Screen
 * In-app messaging with recruiters
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../../constants/theme';
import { messagesAPI } from '../../services/api';

interface Conversation {
  id: string;
  participant: {
    name: string;
    company: string;
    avatar?: string;
  };
  lastMessage: string;
  timestamp: string;
  unread: number;
  jobTitle?: string;
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

// Conversation List Item
const ConversationItem = ({
  conversation,
  onPress,
}: {
  conversation: Conversation;
  onPress: () => void;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <TouchableOpacity
      style={[styles.conversationItem, { backgroundColor: themeColors.surface }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={[styles.avatar, { backgroundColor: colors.turquoise + '20' }]}>
        <Text style={styles.avatarText}>
          {conversation.participant.name.charAt(0)}
        </Text>
      </View>
      <View style={styles.conversationContent}>
        <View style={styles.conversationHeader}>
          <Text style={[styles.participantName, { color: themeColors.text }]} numberOfLines={1}>
            {conversation.participant.name}
          </Text>
          <Text style={[styles.timestamp, { color: themeColors.textTertiary }]}>
            {conversation.timestamp}
          </Text>
        </View>
        <Text style={[styles.companyName, { color: themeColors.textSecondary }]} numberOfLines={1}>
          {conversation.participant.company}
          {conversation.jobTitle && ` • ${conversation.jobTitle}`}
        </Text>
        <Text style={[styles.lastMessage, { color: themeColors.textSecondary }]} numberOfLines={1}>
          {conversation.lastMessage}
        </Text>
      </View>
      {conversation.unread > 0 && (
        <View style={styles.unreadBadge}>
          <Text style={styles.unreadText}>{conversation.unread}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

// Message Bubble
const MessageBubble = ({
  message,
  isUser,
}: {
  message: Message;
  isUser: boolean;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <View style={[
      styles.messageBubbleContainer,
      isUser ? styles.userBubbleContainer : styles.otherBubbleContainer
    ]}>
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
        <Text style={[
          styles.messageTime,
          { color: isUser ? colors.white + 'aa' : themeColors.textTertiary }
        ]}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    </View>
  );
};

// Conversations List View
const ConversationsListView = ({
  conversations,
  onSelectConversation,
  isLoading,
}: {
  conversations: Conversation[];
  onSelectConversation: (id: string) => void;
  isLoading: boolean;
}) => {
  const { colors: themeColors } = useTheme();
  
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.turquoise} />
      </View>
    );
  }
  
  if (conversations.length === 0) {
    return (
      <View style={styles.emptyState}>
        <Text style={styles.emptyIcon}>💬</Text>
        <Text style={[styles.emptyTitle, { color: themeColors.text }]}>No messages yet</Text>
        <Text style={[styles.emptyText, { color: themeColors.textSecondary }]}>
          Start applying to jobs to connect with recruiters
        </Text>
        <TouchableOpacity 
          style={styles.emptyButton}
          onPress={() => router.push('/search')}
        >
          <LinearGradient
            colors={[colors.turquoise, colors.turquoiseLight]}
            style={styles.emptyButtonGradient}
          >
            <Text style={styles.emptyButtonText}>Find Jobs</Text>
          </LinearGradient>
        </TouchableOpacity>
      </View>
    );
  }
  
  return (
    <FlatList
      data={conversations}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <ConversationItem
          conversation={item}
          onPress={() => onSelectConversation(item.id)}
        />
      )}
      contentContainerStyle={styles.conversationsList}
    />
  );
};

// Chat View
const ChatView = ({
  conversation,
  messages,
  onSend,
  onBack,
  isLoading,
}: {
  conversation: Conversation;
  messages: Message[];
  onSend: (text: string) => void;
  onBack: () => void;
  isLoading: boolean;
}) => {
  const { colors: themeColors } = useTheme();
  const scrollViewRef = useRef<ScrollView>(null);
  const [inputText, setInputText] = useState('');
  
  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);
  
  const handleSend = () => {
    if (inputText.trim()) {
      onSend(inputText.trim());
      setInputText('');
    }
  };
  
  return (
    <KeyboardAvoidingView
      style={styles.chatContainer}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={100}
    >
      {/* Chat Header */}
      <View style={[styles.chatHeader, { backgroundColor: themeColors.surface }]}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Text style={[styles.backButtonText, { color: themeColors.text }]}>← Back</Text>
        </TouchableOpacity>
        <View style={styles.chatHeaderInfo}>
          <Text style={[styles.chatHeaderName, { color: themeColors.text }]}>
            {conversation.participant.name}
          </Text>
          <Text style={[styles.chatHeaderCompany, { color: themeColors.textSecondary }]}>
            {conversation.participant.company}
          </Text>
        </View>
        <View style={[styles.onlineIndicator, { backgroundColor: colors.success }]} />
      </View>
      
      {/* Messages */}
      <ScrollView
        ref={scrollViewRef}
        style={[styles.messagesContainer, { backgroundColor: themeColors.background }]}
        contentContainerStyle={styles.messagesContent}
      >
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} isUser={msg.isUser} />
        ))}
        {isLoading && (
          <View style={styles.typingIndicator}>
            <Text style={[styles.typingText, { color: themeColors.textSecondary }]}>
              {conversation.participant.name} is typing...
            </Text>
          </View>
        )}
      </ScrollView>
      
      {/* Input */}
      <View style={[styles.inputContainer, { backgroundColor: themeColors.surface }]}>
        <TextInput
          style={[styles.textInput, { backgroundColor: themeColors.background, color: themeColors.text }]}
          placeholder="Type a message..."
          placeholderTextColor={themeColors.textTertiary}
          value={inputText}
          onChangeText={setInputText}
          multiline
          maxLength={1000}
        />
        <TouchableOpacity
          style={[styles.sendButton, { opacity: inputText.trim() ? 1 : 0.5 }]}
          onPress={handleSend}
          disabled={!inputText.trim()}
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
};

export default function MessagesScreen() {
  const { colors: themeColors } = useTheme();
  const { user } = useAuth();
  
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: '1',
      participant: { name: 'Sarah Chen', company: 'Google' },
      lastMessage: 'Thank you for your application! We would like to schedule...',
      timestamp: '2h ago',
      unread: 2,
      jobTitle: 'Senior Software Engineer',
    },
    {
      id: '2',
      participant: { name: 'Michael Brown', company: 'Microsoft' },
      lastMessage: 'Your profile looks great. Are you available for a call?',
      timestamp: '1d ago',
      unread: 0,
      jobTitle: 'Product Manager',
    },
    {
      id: '3',
      participant: { name: 'Emily Johnson', company: 'Apple' },
      lastMessage: 'We have reviewed your application and...',
      timestamp: '3d ago',
      unread: 1,
      jobTitle: 'UX Designer',
    },
  ]);
  
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const loadConversations = async () => {
    setIsLoading(true);
    try {
      const response = await messagesAPI.getConversations();
      // setConversations(response.data || []);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const loadMessages = async (conversationId: string) => {
    setIsLoading(true);
    try {
      const response = await messagesAPI.getMessages(conversationId);
      // setMessages(response.data || []);
      // Demo messages
      setMessages([
        { id: '1', text: 'Hi! Thank you for applying to the Senior Software Engineer position.', isUser: false, timestamp: new Date(Date.now() - 3600000 * 2) },
        { id: '2', text: 'Thank you for reaching out! I\'m very excited about this opportunity.', isUser: true, timestamp: new Date(Date.now() - 3600000) },
        { id: '3', text: 'Great! We would like to schedule a phone screen with you. Are you available next week?', isUser: false, timestamp: new Date(Date.now() - 1800000) },
        { id: '4', text: 'Yes, I\'m available Tuesday or Wednesday afternoon.', isUser: true, timestamp: new Date(Date.now() - 900000) },
        { id: '5', text: 'Perfect! Let\'s do Tuesday at 2 PM PST. I\'ll send you a calendar invite.', isUser: false, timestamp: new Date() },
      ]);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSelectConversation = (id: string) => {
    setSelectedConversation(id);
    loadMessages(id);
    // Mark as read
    setConversations(prev =>
      prev.map(c => c.id === id ? { ...c, unread: 0 } : c)
    );
  };
  
  const handleSendMessage = async (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
    
    try {
      await messagesAPI.sendMessage(selectedConversation!, text);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };
  
  const selectedConv = conversations.find(c => c.id === selectedConversation);
  
  if (selectedConversation && selectedConv) {
    return (
      <ChatView
        conversation={selectedConv}
        messages={messages}
        onSend={handleSendMessage}
        onBack={() => setSelectedConversation(null)}
        isLoading={isLoading}
      />
    );
  }
  
  return (
    <View style={[styles.container, { backgroundColor: themeColors.background }]}>
      {/* Header */}
      <View style={[styles.header, { backgroundColor: themeColors.surface }]}>
        <Text style={[styles.headerTitle, { color: themeColors.text }]}>Messages</Text>
        <View style={styles.unreadCount}>
          <Text style={styles.unreadCountText}>
            {conversations.reduce((sum, c) => sum + c.unread, 0)} unread
          </Text>
        </View>
      </View>
      
      <ConversationsListView
        conversations={conversations}
        onSelectConversation={handleSelectConversation}
        isLoading={isLoading}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center',
    padding: spacing.md,
    ...shadows.sm,
  },
  headerTitle: { fontSize: fontSize.xl, fontWeight: fontWeight.bold },
  unreadCount: { 
    backgroundColor: colors.turquoise + '20', 
    paddingHorizontal: spacing.sm, 
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.full,
  },
  unreadCountText: { color: colors.turquoise, fontSize: fontSize.sm, fontWeight: fontWeight.medium },
  
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  
  emptyState: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: spacing.xl },
  emptyIcon: { fontSize: 64, marginBottom: spacing.md },
  emptyTitle: { fontSize: fontSize.xl, fontWeight: fontWeight.semibold, marginBottom: spacing.sm },
  emptyText: { fontSize: fontSize.base, textAlign: 'center', marginBottom: spacing.lg },
  emptyButton: { borderRadius: borderRadius.lg, overflow: 'hidden' },
  emptyButtonGradient: { paddingHorizontal: spacing.xl, paddingVertical: spacing.md },
  emptyButtonText: { color: colors.white, fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  
  conversationsList: { padding: spacing.md },
  conversationItem: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderRadius: borderRadius.lg,
    ...shadows.sm,
  },
  avatar: { 
    width: 48, 
    height: 48, 
    borderRadius: 24, 
    justifyContent: 'center', 
    alignItems: 'center',
    marginRight: spacing.md,
  },
  avatarText: { fontSize: fontSize.lg, fontWeight: fontWeight.bold, color: colors.turquoise },
  conversationContent: { flex: 1 },
  conversationHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  participantName: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, flex: 1 },
  timestamp: { fontSize: fontSize.xs },
  companyName: { fontSize: fontSize.sm, marginTop: 2 },
  lastMessage: { fontSize: fontSize.sm, marginTop: spacing.xs },
  unreadBadge: { 
    backgroundColor: colors.turquoise, 
    width: 20, 
    height: 20, 
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: spacing.sm,
  },
  unreadText: { color: colors.white, fontSize: fontSize.xs, fontWeight: fontWeight.bold },
  
  // Chat View
  chatContainer: { flex: 1 },
  chatHeader: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    padding: spacing.md,
    ...shadows.sm,
  },
  backButton: { padding: spacing.xs, marginRight: spacing.sm },
  backButtonText: { fontSize: fontSize.base, fontWeight: fontWeight.medium },
  chatHeaderInfo: { flex: 1 },
  chatHeaderName: { fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  chatHeaderCompany: { fontSize: fontSize.sm },
  onlineIndicator: { width: 10, height: 10, borderRadius: 5 },
  
  messagesContainer: { flex: 1 },
  messagesContent: { padding: spacing.md },
  messageBubbleContainer: { marginBottom: spacing.sm },
  userBubbleContainer: { alignItems: 'flex-end' },
  otherBubbleContainer: { alignItems: 'flex-start' },
  messageBubble: { 
    maxWidth: '80%', 
    padding: spacing.md, 
    borderRadius: borderRadius.lg,
    ...shadows.sm,
  },
  messageText: { fontSize: fontSize.base, lineHeight: 22 },
  messageTime: { fontSize: fontSize.xs, marginTop: spacing.xs, textAlign: 'right' },
  typingIndicator: { padding: spacing.md },
  typingText: { fontSize: fontSize.sm, fontStyle: 'italic' },
  
  inputContainer: { 
    flexDirection: 'row', 
    alignItems: 'flex-end', 
    padding: spacing.md,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.05)',
  },
  textInput: { 
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
});
