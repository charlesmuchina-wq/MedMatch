/**
 * MedMatch Mobile - Tab Layout
 * Bottom navigation with batik-inspired styling
 */
import { Tabs } from 'expo-router';
import { View, Text, StyleSheet, Platform } from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';
import { colors } from '../../constants/theme';

// Custom Tab Bar Icon
const TabBarIcon = ({ icon, focused }: { icon: string; focused: boolean }) => (
  <View style={[styles.iconContainer, focused && styles.iconContainerFocused]}>
    <Text style={[styles.iconEmoji, { opacity: focused ? 1 : 0.6 }]}>{icon}</Text>
  </View>
);

export default function TabLayout() {
  const { colors: themeColors, isDark } = useTheme();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.turquoise,
        tabBarInactiveTintColor: themeColors.textSecondary,
        tabBarStyle: {
          backgroundColor: themeColors.surface,
          borderTopColor: themeColors.border,
          borderTopWidth: 1,
          height: Platform.OS === 'ios' ? 88 : 65,
          paddingBottom: Platform.OS === 'ios' ? 25 : 10,
          paddingTop: 10,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
        },
        headerStyle: {
          backgroundColor: themeColors.surface,
          shadowColor: 'transparent',
          elevation: 0,
        },
        headerTintColor: themeColors.text,
        headerTitleStyle: {
          fontWeight: 'bold',
          fontSize: 20,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ focused }) => <TabBarIcon icon="🏠" focused={focused} />,
          tabBarLabel: 'Home',
          headerTitle: 'MedMatch',
          headerTitleStyle: {
            color: colors.turquoise,
            fontWeight: 'bold',
            fontSize: 24,
          },
        }}
      />
      <Tabs.Screen
        name="search"
        options={{
          title: 'Jobs',
          tabBarIcon: ({ focused }) => <TabBarIcon icon="🔍" focused={focused} />,
          tabBarLabel: 'Search',
          headerTitle: 'Find Jobs',
        }}
      />
      <Tabs.Screen
        name="calendar"
        options={{
          title: 'Calendar',
          tabBarIcon: ({ focused }) => <TabBarIcon icon="📅" focused={focused} />,
          tabBarLabel: 'Interviews',
          headerTitle: 'Interview Calendar',
        }}
      />
      <Tabs.Screen
        name="ai-tools"
        options={{
          title: 'AI Tools',
          tabBarIcon: ({ focused }) => <TabBarIcon icon="✨" focused={focused} />,
          tabBarLabel: 'AI Tools',
          headerTitle: 'AI Assistant',
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ focused }) => <TabBarIcon icon="👤" focused={focused} />,
          tabBarLabel: 'Profile',
          headerTitle: 'My Profile',
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  iconContainer: {
    width: 40,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconContainerFocused: {
    backgroundColor: colors.turquoise + '20',
  },
  iconEmoji: {
    fontSize: 20,
  },
});
