/**
 * MedMatch Mobile App - Root Layout
 * Expo SDK 54 with React Native 0.81
 */
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { ThemeProvider, useTheme } from '../contexts/ThemeContext';
import { NotificationProvider } from '../contexts/NotificationContext';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import '../global.css';

function RootLayoutNav() {
  const { isLoading } = useAuth();
  const { isDark } = useTheme();

  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, isDark && styles.loadingContainerDark]}>
        <ActivityIndicator size="large" color="#4f46e5" />
      </View>
    );
  }

  return (
    <>
      <StatusBar style={isDark ? 'light' : 'dark'} />
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: isDark ? '#1a1a2e' : '#ffffff',
          },
          headerTintColor: isDark ? '#ffffff' : '#1a1a2e',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
          contentStyle: {
            backgroundColor: isDark ? '#0f0f1a' : '#f5f5f5',
          },
        }}
      >
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="(auth)" options={{ headerShown: false }} />
        <Stack.Screen 
          name="job/[id]" 
          options={{ 
            title: 'Job Details',
            presentation: 'card',
          }} 
        />
        <Stack.Screen 
          name="interview/practice" 
          options={{ 
            title: 'Interview Practice',
            presentation: 'modal',
          }} 
        />
        <Stack.Screen 
          name="video-interview" 
          options={{ 
            title: 'Video Interview',
            presentation: 'fullScreenModal',
          }} 
        />
        <Stack.Screen 
          name="id-verification" 
          options={{ 
            title: 'ID Verification',
            presentation: 'modal',
          }} 
        />
        <Stack.Screen 
          name="account" 
          options={{ 
            title: 'Account Settings',
            presentation: 'card',
            headerShown: false,
          }} 
        />
        <Stack.Screen 
          name="credentials" 
          options={{ 
            title: 'My Credentials',
            presentation: 'card',
            headerShown: false,
          }} 
        />
      </Stack>
    </>
  );
}

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <ThemeProvider>
          <AuthProvider>
            <NotificationProvider>
              <RootLayoutNav />
            </NotificationProvider>
          </AuthProvider>
        </ThemeProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  loadingContainerDark: {
    backgroundColor: '#0f0f1a',
  },
});
