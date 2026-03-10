import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { Provider as PaperProvider, DefaultTheme } from 'react-native-paper';
import { enableScreens } from 'react-native-screens';
import { AuthProvider } from './contexts/AuthContext';
import AppNavigator from './navigation/AppNavigator';
import { PaperTheme } from './constants/Theme';

// Enable screens for better performance
enableScreens();

export default function App() {
  return (
    <PaperProvider theme={PaperTheme}>
      <AuthProvider>
        <AppNavigator />
        <StatusBar style="light" />
      </AuthProvider>
    </PaperProvider>
  );
}
