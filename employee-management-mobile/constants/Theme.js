import { DefaultTheme } from 'react-native-paper';

export const COLORS = {
    primary: '#7C3AED',         // AI Purple
    primaryLight: '#A78BFA',    // Soft Purple
    secondary: '#06B6D4',       // AI Cyan (CTA)
    background: '#FAF5FF',      // Soft Lavender/White
    surface: '#FFFFFF',         // White
    text: '#1E1B4B',            // Deep Indigo
    textMuted: '#64748B',       // Slate Gray
    error: '#EF4444',           // Red
    success: '#10B981',         // Green
    white: '#FFFFFF',
    glass: 'rgba(255, 255, 255, 0.8)',
    border: '#E2E8F0',          // Slate 200
};

export const SPACING = {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
};

export const SHADOWS = {
    sm: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 2,
        elevation: 2,
    },
    md: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.1,
        shadowRadius: 6,
        elevation: 4,
    },
    lg: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.1,
        shadowRadius: 15,
        elevation: 8,
    },
};

export const PaperTheme = {
    ...DefaultTheme,
    roundness: 12,
    colors: {
        ...DefaultTheme.colors,
        primary: COLORS.primary,
        accent: COLORS.secondary,
        background: COLORS.background,
        surface: COLORS.surface,
        text: COLORS.text,
        error: COLORS.error,
        placeholder: COLORS.textMuted,
    },
};
