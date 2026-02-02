/**
 * MedMatch Mobile - Calendar/Interview Schedule Screen
 * View and manage interview appointments
 */
import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  Modal,
  TextInput,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useTheme } from '../../contexts/ThemeContext';
import { colors, spacing, borderRadius, fontSize, fontWeight, shadows } from '../../constants/theme';

type InterviewStatus = 'scheduled' | 'completed' | 'cancelled';
type InterviewType = 'video' | 'phone' | 'in_person';

interface Interview {
  id: string;
  company: string;
  position: string;
  date: string;
  time: string;
  type: InterviewType;
  status: InterviewStatus;
  location?: string;
  notes?: string;
}

// Calendar Day Component
const CalendarDay = ({
  day,
  isToday,
  isSelected,
  hasEvent,
  onPress,
}: {
  day: number;
  isToday: boolean;
  isSelected: boolean;
  hasEvent: boolean;
  onPress: () => void;
}) => {
  const { colors: themeColors } = useTheme();
  
  return (
    <TouchableOpacity 
      style={[
        styles.calendarDay,
        isToday && styles.calendarDayToday,
        isSelected && styles.calendarDaySelected,
      ]}
      onPress={onPress}
    >
      <Text style={[
        styles.calendarDayText,
        { color: isSelected ? colors.white : isToday ? colors.turquoise : themeColors.text }
      ]}>
        {day}
      </Text>
      {hasEvent && !isSelected && (
        <View style={[styles.eventDot, { backgroundColor: colors.turquoise }]} />
      )}
    </TouchableOpacity>
  );
};

// Interview Card Component
const InterviewCard = ({
  interview,
  onPress,
  onStatusChange,
}: {
  interview: Interview;
  onPress: () => void;
  onStatusChange: (status: InterviewStatus) => void;
}) => {
  const { colors: themeColors } = useTheme();
  
  const typeIcons: Record<InterviewType, string> = {
    video: '📹',
    phone: '📞',
    in_person: '🏢',
  };
  
  const statusColors: Record<InterviewStatus, string> = {
    scheduled: colors.turquoise,
    completed: colors.success,
    cancelled: colors.error,
  };

  return (
    <TouchableOpacity
      style={[styles.interviewCard, { backgroundColor: themeColors.surface }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.interviewHeader}>
        <View style={[styles.interviewTypeIcon, { backgroundColor: colors.turquoise + '20' }]}>
          <Text style={styles.interviewTypeEmoji}>{typeIcons[interview.type]}</Text>
        </View>
        <View style={styles.interviewHeaderInfo}>
          <Text style={[styles.interviewPosition, { color: themeColors.text }]} numberOfLines={1}>
            {interview.position}
          </Text>
          <Text style={[styles.interviewCompany, { color: themeColors.textSecondary }]}>
            {interview.company}
          </Text>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: statusColors[interview.status] + '20' }]}>
          <Text style={[styles.statusText, { color: statusColors[interview.status] }]}>
            {interview.status.charAt(0).toUpperCase() + interview.status.slice(1)}
          </Text>
        </View>
      </View>
      
      <View style={styles.interviewDetails}>
        <View style={styles.detailRow}>
          <Text style={styles.detailIcon}>📅</Text>
          <Text style={[styles.detailText, { color: themeColors.textSecondary }]}>
            {interview.date} at {interview.time}
          </Text>
        </View>
        {interview.location && (
          <View style={styles.detailRow}>
            <Text style={styles.detailIcon}>📍</Text>
            <Text style={[styles.detailText, { color: themeColors.textSecondary }]}>
              {interview.location}
            </Text>
          </View>
        )}
      </View>
      
      {interview.status === 'scheduled' && (
        <View style={styles.actionButtons}>
          <TouchableOpacity 
            style={[styles.actionButton, { backgroundColor: colors.success + '15' }]}
            onPress={() => onStatusChange('completed')}
          >
            <Text style={[styles.actionButtonText, { color: colors.success }]}>✓ Complete</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.actionButton, { backgroundColor: colors.error + '15' }]}
            onPress={() => onStatusChange('cancelled')}
          >
            <Text style={[styles.actionButtonText, { color: colors.error }]}>✕ Cancel</Text>
          </TouchableOpacity>
        </View>
      )}
    </TouchableOpacity>
  );
};

// Add Interview Modal
const AddInterviewModal = ({
  visible,
  onClose,
  onAdd,
}: {
  visible: boolean;
  onClose: () => void;
  onAdd: (interview: Partial<Interview>) => void;
}) => {
  const { colors: themeColors, isDark } = useTheme();
  const [company, setCompany] = useState('');
  const [position, setPosition] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [type, setType] = useState<InterviewType>('video');
  
  const handleAdd = () => {
    if (!company || !position || !date || !time) {
      Alert.alert('Missing Fields', 'Please fill in all required fields');
      return;
    }
    onAdd({ company, position, date, time, type, status: 'scheduled' });
    setCompany('');
    setPosition('');
    setDate('');
    setTime('');
    setType('video');
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" transparent>
      <View style={styles.modalOverlay}>
        <View style={[styles.modalContent, { backgroundColor: themeColors.surface }]}>
          <Text style={[styles.modalTitle, { color: themeColors.text }]}>Schedule Interview</Text>
          
          <Text style={[styles.inputLabel, { color: themeColors.textSecondary }]}>Company *</Text>
          <TextInput
            style={[styles.input, { backgroundColor: themeColors.background, color: themeColors.text }]}
            placeholder="Company name"
            placeholderTextColor={themeColors.textTertiary}
            value={company}
            onChangeText={setCompany}
          />
          
          <Text style={[styles.inputLabel, { color: themeColors.textSecondary }]}>Position *</Text>
          <TextInput
            style={[styles.input, { backgroundColor: themeColors.background, color: themeColors.text }]}
            placeholder="Job title"
            placeholderTextColor={themeColors.textTertiary}
            value={position}
            onChangeText={setPosition}
          />
          
          <View style={styles.inputRow}>
            <View style={styles.inputHalf}>
              <Text style={[styles.inputLabel, { color: themeColors.textSecondary }]}>Date *</Text>
              <TextInput
                style={[styles.input, { backgroundColor: themeColors.background, color: themeColors.text }]}
                placeholder="Feb 15, 2026"
                placeholderTextColor={themeColors.textTertiary}
                value={date}
                onChangeText={setDate}
              />
            </View>
            <View style={styles.inputHalf}>
              <Text style={[styles.inputLabel, { color: themeColors.textSecondary }]}>Time *</Text>
              <TextInput
                style={[styles.input, { backgroundColor: themeColors.background, color: themeColors.text }]}
                placeholder="2:00 PM"
                placeholderTextColor={themeColors.textTertiary}
                value={time}
                onChangeText={setTime}
              />
            </View>
          </View>
          
          <Text style={[styles.inputLabel, { color: themeColors.textSecondary }]}>Type</Text>
          <View style={styles.typeSelector}>
            {(['video', 'phone', 'in_person'] as InterviewType[]).map((t) => (
              <TouchableOpacity
                key={t}
                style={[
                  styles.typeButton,
                  { 
                    backgroundColor: type === t ? colors.turquoise : themeColors.background,
                    borderColor: type === t ? colors.turquoise : themeColors.border,
                  }
                ]}
                onPress={() => setType(t)}
              >
                <Text style={{ color: type === t ? colors.white : themeColors.text }}>
                  {t === 'video' ? '📹' : t === 'phone' ? '📞' : '🏢'} {t.replace('_', '-')}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          
          <View style={styles.modalActions}>
            <TouchableOpacity style={styles.cancelButton} onPress={onClose}>
              <Text style={[styles.cancelButtonText, { color: themeColors.textSecondary }]}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.addButton} onPress={handleAdd}>
              <LinearGradient
                colors={[colors.turquoise, colors.turquoiseLight]}
                style={styles.addButtonGradient}
              >
                <Text style={styles.addButtonText}>Schedule</Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

export default function CalendarScreen() {
  const { colors: themeColors } = useTheme();
  
  const [selectedDate, setSelectedDate] = useState(new Date().getDate());
  const [refreshing, setRefreshing] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [interviews, setInterviews] = useState<Interview[]>([
    {
      id: '1',
      company: 'Google',
      position: 'Senior Software Engineer',
      date: 'Feb 3, 2026',
      time: '2:00 PM',
      type: 'video',
      status: 'scheduled',
      location: 'Google Meet',
    },
    {
      id: '2',
      company: 'Microsoft',
      position: 'Product Manager',
      date: 'Feb 5, 2026',
      time: '10:00 AM',
      type: 'phone',
      status: 'scheduled',
    },
    {
      id: '3',
      company: 'Apple',
      position: 'UX Designer',
      date: 'Jan 30, 2026',
      time: '3:00 PM',
      type: 'in_person',
      status: 'completed',
      location: 'Apple Park, Cupertino',
    },
  ]);

  const currentDate = new Date();
  const currentMonth = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
  
  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  
  // Days with events (for demo)
  const eventDays = new Set([3, 5, 10, 15, 22]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  }, []);

  const handleStatusChange = (interviewId: string, newStatus: InterviewStatus) => {
    Alert.alert(
      'Update Status',
      `Mark this interview as ${newStatus}?`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Confirm', 
          onPress: () => {
            setInterviews(prev => 
              prev.map(i => i.id === interviewId ? { ...i, status: newStatus } : i)
            );
          }
        },
      ]
    );
  };

  const handleAddInterview = (interview: Partial<Interview>) => {
    const newInterview: Interview = {
      id: Date.now().toString(),
      company: interview.company || '',
      position: interview.position || '',
      date: interview.date || '',
      time: interview.time || '',
      type: interview.type || 'video',
      status: 'scheduled',
    };
    setInterviews(prev => [...prev, newInterview]);
  };

  const scheduledInterviews = interviews.filter(i => i.status === 'scheduled');
  const completedInterviews = interviews.filter(i => i.status === 'completed');

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: themeColors.background }]}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.turquoise} />
      }
    >
      {/* Calendar Header */}
      <View style={[styles.calendarHeader, { backgroundColor: themeColors.surface }]}>
        <Text style={[styles.monthTitle, { color: themeColors.text }]}>{currentMonth}</Text>
        
        {/* Week Days */}
        <View style={styles.weekDaysRow}>
          {weekDays.map(day => (
            <Text key={day} style={[styles.weekDayText, { color: themeColors.textSecondary }]}>
              {day}
            </Text>
          ))}
        </View>
        
        {/* Calendar Grid */}
        <View style={styles.calendarGrid}>
          {/* Empty cells for days before the 1st */}
          {Array.from({ length: firstDayOfMonth }).map((_, i) => (
            <View key={`empty-${i}`} style={styles.calendarDay} />
          ))}
          
          {/* Days of the month */}
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = i + 1;
            return (
              <CalendarDay
                key={day}
                day={day}
                isToday={day === currentDate.getDate()}
                isSelected={day === selectedDate}
                hasEvent={eventDays.has(day)}
                onPress={() => setSelectedDate(day)}
              />
            );
          })}
        </View>
      </View>

      {/* Stats */}
      <View style={styles.statsRow}>
        <View style={[styles.statCard, { backgroundColor: themeColors.surface }]}>
          <Text style={styles.statIcon}>📅</Text>
          <Text style={[styles.statValue, { color: themeColors.text }]}>{scheduledInterviews.length}</Text>
          <Text style={[styles.statLabel, { color: themeColors.textSecondary }]}>Upcoming</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: themeColors.surface }]}>
          <Text style={styles.statIcon}>✅</Text>
          <Text style={[styles.statValue, { color: themeColors.text }]}>{completedInterviews.length}</Text>
          <Text style={[styles.statLabel, { color: themeColors.textSecondary }]}>Completed</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: themeColors.surface }]}>
          <Text style={styles.statIcon}>🎯</Text>
          <Text style={[styles.statValue, { color: themeColors.text }]}>
            {completedInterviews.length > 0 ? Math.round((completedInterviews.length / interviews.length) * 100) : 0}%
          </Text>
          <Text style={[styles.statLabel, { color: themeColors.textSecondary }]}>Success</Text>
        </View>
      </View>

      {/* Add Interview Button */}
      <TouchableOpacity 
        style={styles.addInterviewButton}
        onPress={() => setShowAddModal(true)}
      >
        <LinearGradient
          colors={[colors.turquoise, colors.turquoiseLight]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={styles.addInterviewGradient}
        >
          <Text style={styles.addInterviewText}>+ Schedule New Interview</Text>
        </LinearGradient>
      </TouchableOpacity>

      {/* Upcoming Interviews */}
      {scheduledInterviews.length > 0 && (
        <>
          <Text style={[styles.sectionTitle, { color: themeColors.text }]}>
            Upcoming Interviews ({scheduledInterviews.length})
          </Text>
          {scheduledInterviews.map(interview => (
            <InterviewCard
              key={interview.id}
              interview={interview}
              onPress={() => {}}
              onStatusChange={(status) => handleStatusChange(interview.id, status)}
            />
          ))}
        </>
      )}

      {/* Completed Interviews */}
      {completedInterviews.length > 0 && (
        <>
          <Text style={[styles.sectionTitle, { color: themeColors.text }]}>
            Completed ({completedInterviews.length})
          </Text>
          {completedInterviews.map(interview => (
            <InterviewCard
              key={interview.id}
              interview={interview}
              onPress={() => {}}
              onStatusChange={(status) => handleStatusChange(interview.id, status)}
            />
          ))}
        </>
      )}

      {/* Add Interview Modal */}
      <AddInterviewModal
        visible={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={handleAddInterview}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { paddingBottom: spacing['2xl'] },
  calendarHeader: { 
    margin: spacing.md, 
    padding: spacing.md, 
    borderRadius: borderRadius.xl,
    ...shadows.sm,
  },
  monthTitle: { 
    fontSize: fontSize.xl, 
    fontWeight: fontWeight.bold, 
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  weekDaysRow: { 
    flexDirection: 'row', 
    justifyContent: 'space-around',
    marginBottom: spacing.sm,
  },
  weekDayText: { 
    fontSize: fontSize.sm, 
    fontWeight: fontWeight.medium,
    width: 40,
    textAlign: 'center',
  },
  calendarGrid: { 
    flexDirection: 'row', 
    flexWrap: 'wrap',
  },
  calendarDay: { 
    width: '14.28%', 
    aspectRatio: 1,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  calendarDayToday: { },
  calendarDaySelected: { 
    backgroundColor: colors.turquoise,
    borderRadius: 20,
  },
  calendarDayText: { 
    fontSize: fontSize.base, 
    fontWeight: fontWeight.medium,
  },
  eventDot: { 
    position: 'absolute', 
    bottom: 4, 
    width: 6, 
    height: 6, 
    borderRadius: 3,
  },
  statsRow: { 
    flexDirection: 'row', 
    paddingHorizontal: spacing.md, 
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  statCard: { 
    flex: 1, 
    padding: spacing.md, 
    borderRadius: borderRadius.lg, 
    alignItems: 'center',
    ...shadows.sm,
  },
  statIcon: { fontSize: 24, marginBottom: spacing.xs },
  statValue: { fontSize: fontSize.xl, fontWeight: fontWeight.bold },
  statLabel: { fontSize: fontSize.xs, marginTop: 2 },
  addInterviewButton: { 
    marginHorizontal: spacing.md, 
    borderRadius: borderRadius.lg, 
    overflow: 'hidden',
    marginBottom: spacing.md,
  },
  addInterviewGradient: { 
    paddingVertical: spacing.md, 
    alignItems: 'center',
  },
  addInterviewText: { 
    color: colors.white, 
    fontSize: fontSize.base, 
    fontWeight: fontWeight.semibold,
  },
  sectionTitle: { 
    fontSize: fontSize.lg, 
    fontWeight: fontWeight.semibold, 
    marginHorizontal: spacing.md,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  interviewCard: { 
    marginHorizontal: spacing.md, 
    marginBottom: spacing.sm, 
    padding: spacing.md, 
    borderRadius: borderRadius.lg,
    ...shadows.sm,
  },
  interviewHeader: { flexDirection: 'row', alignItems: 'center' },
  interviewTypeIcon: { 
    width: 44, 
    height: 44, 
    borderRadius: 22, 
    justifyContent: 'center', 
    alignItems: 'center',
    marginRight: spacing.md,
  },
  interviewTypeEmoji: { fontSize: 20 },
  interviewHeaderInfo: { flex: 1 },
  interviewPosition: { fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  interviewCompany: { fontSize: fontSize.sm, marginTop: 2 },
  statusBadge: { 
    paddingHorizontal: spacing.sm, 
    paddingVertical: spacing.xs, 
    borderRadius: borderRadius.sm,
  },
  statusText: { fontSize: fontSize.xs, fontWeight: fontWeight.semibold },
  interviewDetails: { marginTop: spacing.md },
  detailRow: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.xs },
  detailIcon: { fontSize: 14, marginRight: spacing.sm },
  detailText: { fontSize: fontSize.sm },
  actionButtons: { 
    flexDirection: 'row', 
    gap: spacing.sm, 
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.05)',
  },
  actionButton: { 
    flex: 1, 
    paddingVertical: spacing.sm, 
    borderRadius: borderRadius.md, 
    alignItems: 'center',
  },
  actionButtonText: { fontSize: fontSize.sm, fontWeight: fontWeight.semibold },
  
  // Modal styles
  modalOverlay: { 
    flex: 1, 
    backgroundColor: 'rgba(0,0,0,0.5)', 
    justifyContent: 'flex-end',
  },
  modalContent: { 
    padding: spacing.lg, 
    borderTopLeftRadius: borderRadius.xl, 
    borderTopRightRadius: borderRadius.xl,
  },
  modalTitle: { 
    fontSize: fontSize.xl, 
    fontWeight: fontWeight.bold, 
    marginBottom: spacing.lg,
    textAlign: 'center',
  },
  inputLabel: { 
    fontSize: fontSize.sm, 
    fontWeight: fontWeight.medium, 
    marginBottom: spacing.xs,
    marginTop: spacing.md,
  },
  input: { 
    padding: spacing.md, 
    borderRadius: borderRadius.md, 
    fontSize: fontSize.base,
  },
  inputRow: { flexDirection: 'row', gap: spacing.md },
  inputHalf: { flex: 1 },
  typeSelector: { flexDirection: 'row', gap: spacing.sm, marginTop: spacing.xs },
  typeButton: { 
    flex: 1, 
    padding: spacing.sm, 
    borderRadius: borderRadius.md, 
    alignItems: 'center',
    borderWidth: 1,
  },
  modalActions: { 
    flexDirection: 'row', 
    gap: spacing.md, 
    marginTop: spacing.xl,
  },
  cancelButton: { 
    flex: 1, 
    padding: spacing.md, 
    alignItems: 'center',
  },
  cancelButtonText: { fontSize: fontSize.base, fontWeight: fontWeight.medium },
  addButton: { flex: 1, borderRadius: borderRadius.lg, overflow: 'hidden' },
  addButtonGradient: { padding: spacing.md, alignItems: 'center' },
  addButtonText: { color: colors.white, fontSize: fontSize.base, fontWeight: fontWeight.semibold },
});
