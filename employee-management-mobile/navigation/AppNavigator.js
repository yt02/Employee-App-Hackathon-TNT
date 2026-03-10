import React from 'react';
import { ScrollView, ActivityIndicator, View, Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Card, Title, List, Surface } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { COLORS, SPACING, SHADOWS } from '../constants/Theme';

// Screens
import HomeScreen from '../screens/HomeScreen';
import ChatbotScreen from '../screens/ChatbotScreen';
import LeaveScreen from '../screens/LeaveScreen';
import RoomsScreen from '../screens/RoomsScreen';
import AttendanceScreen from '../screens/AttendanceScreen';
import LoginScreen from '../screens/LoginScreen';
import CalendarScreen from '../screens/CalendarScreen';
import TicketsScreen from '../screens/TicketsScreen';
import VisitorScreen from '../screens/VisitorScreen';
import ShuttleScreen from '../screens/ShuttleScreen';

import { createNativeStackNavigator } from '@react-navigation/native-stack';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

const ROLE_PERMISSIONS = {
  employee: ["Assistant", "Home", "Leave", "Rooms", "Attendance", "More"],
  hr_manager: ["Assistant", "Home", "Leave", "Attendance", "More"],
  facility_manager: ["Assistant", "Home", "Rooms", "More"],
  fitness_instructor: ["Assistant", "Home", "More"],
  shuttle_driver: ["Assistant", "Home", "More"],
  admin: ["Assistant", "Home", "Leave", "Rooms", "Attendance", "More"],
};

const MORE_MODULES_PERMISSIONS = {
  employee: ["Calendar", "Tickets", "Visitor", "Shuttle"],
  hr_manager: ["Calendar"],
  facility_manager: ["Tickets", "Visitor"],
  fitness_instructor: [],
  shuttle_driver: ["Shuttle"],
  admin: ["Calendar", "Tickets", "Visitor", "Shuttle"],
};

const ALL_TABS = [
  {
    name: "Assistant",
    component: ChatbotScreen,
    icon: "robot",
    color: COLORS.secondary,
    title: "Work Assistant",
  },
  {
    name: "Home",
    component: HomeScreen,
    icon: "home-variant",
    color: COLORS.primary,
    title: "Dashboard",
  },
  {
    name: "Leave",
    component: LeaveScreen,
    icon: "calendar-clock",
    color: COLORS.primary,
    title: "Attendance",
  },
  {
    name: "Rooms",
    component: RoomsScreen,
    icon: "office-building",
    color: COLORS.primary,
    title: "Workspaces",
  },
  {
    name: "Attendance",
    component: AttendanceScreen,
    icon: "clock-check",
    color: COLORS.primary,
    title: "Check-In",
  },
];

function MainTabs() {
  const { user } = useAuth();
  const role = user?.role || 'employee';
  const allowedTabs = ROLE_PERMISSIONS[role] || ROLE_PERMISSIONS['employee'];

  const visibleTabs = ALL_TABS.filter(tab => allowedTabs.includes(tab.name));

  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.textMuted,
        tabBarStyle: {
          height: 65,
          paddingBottom: 10,
          paddingTop: 10,
          backgroundColor: COLORS.surface,
          borderTopWidth: 0,
          ...SHADOWS.md,
        },
        tabBarLabelStyle: {
          fontSize: 10,
          fontWeight: '600',
        },
        headerShown: true,
        headerStyle: {
          backgroundColor: COLORS.surface,
          elevation: 0,
          shadowOpacity: 0,
          borderBottomWidth: 1,
          borderBottomColor: COLORS.border,
        },
        headerTitleStyle: {
          color: COLORS.text,
          fontWeight: '800',
          fontSize: 18,
        },
      }}
    >
      {visibleTabs.map(tab => (
        <Tab.Screen
          key={tab.name}
          name={tab.name}
          component={tab.component}
          options={{
            tabBarIcon: ({ color, size, focused }) => (
              <MaterialCommunityIcons
                name={focused ? tab.icon : tab.icon + '-outline'}
                size={26}
                color={focused && tab.name === "Assistant" ? COLORS.secondary : color}
              />
            ),
            headerTitle: tab.title || tab.name,
          }}
        />
      ))}

      {allowedTabs.includes("More") && (
        <Tab.Screen
          name="More"
          component={MoreScreen}
          options={{
            tabBarIcon: ({ color, size, focused }) => (
              <MaterialCommunityIcons name={focused ? "view-grid" : "view-grid-outline"} size={26} color={color} />
            ),
            headerTitle: "All Services",
          }}
        />
      )}
    </Tab.Navigator>
  );
}

function MoreScreen({ navigation }) {
  const { user } = useAuth();
  const role = user?.role || 'employee';
  const allowedModules = MORE_MODULES_PERMISSIONS[role] || MORE_MODULES_PERMISSIONS['employee'];

  const allModules = [
    { name: 'Ask Assistant', icon: 'robot', screen: 'Assistant', color: COLORS.secondary },
    { name: 'Calendar', icon: 'calendar', screen: 'Calendar', color: '#818CF8' },
    { name: 'Tickets', icon: 'ticket', screen: 'Tickets', color: '#F87171' },
    { name: 'Visitor', icon: 'account-group', screen: 'Visitor', color: '#2DD4BF' },
    { name: 'Shuttle', icon: 'bus', screen: 'Shuttle', color: '#60A5FA' },
  ];

  const visibleModules = allModules.filter(m => allowedModules.includes(m.name));

  return (
    <ScrollView style={{ flex: 1, backgroundColor: COLORS.background }}>
      <View style={{ padding: SPACING.lg }}>
        <Text style={{ fontSize: 20, fontWeight: '800', color: COLORS.text, marginBottom: SPACING.md }}>All Services</Text>
        {visibleModules.map((module, index) => (
          <Surface
            key={index}
            style={{
              backgroundColor: COLORS.surface,
              marginTop: SPACING.md,
              borderRadius: 16,
              overflow: 'hidden',
              ...SHADOWS.sm,
            }}
          >
            <List.Item
              title={module.name}
              titleStyle={{ fontWeight: '600', color: COLORS.text }}
              left={props => (
                <View style={{
                  backgroundColor: module.color + '15',
                  borderRadius: 12,
                  width: 40,
                  height: 40,
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginLeft: 8
                }}>
                  <MaterialCommunityIcons name={module.icon} size={22} color={module.color} />
                </View>
              )}
              right={props => <List.Icon {...props} icon="chevron-right" color={COLORS.textMuted} />}
              onPress={() => navigation.navigate(module.screen)}
              style={{ paddingVertical: 8 }}
            />
          </Surface>
        ))}
      </View>
    </ScrollView>
  );
}

const COMMON_HEADER_STYLING = {
  headerStyle: {
    backgroundColor: COLORS.surface,
  },
  headerTitleStyle: {
    color: COLORS.text,
    fontWeight: '800',
    fontSize: 18,
  },
  headerTintColor: COLORS.primary,
  headerShadowVisible: false,
};

function MainStack() {
  return (
    <Stack.Navigator screenOptions={COMMON_HEADER_STYLING}>
      <Stack.Screen name="MainTabs" component={MainTabs} options={{ headerShown: false }} />
      <Stack.Screen name="Calendar" component={CalendarScreen} options={{ headerTitle: 'Company Calendar' }} />
      <Stack.Screen name="Tickets" component={TicketsScreen} options={{ headerTitle: 'IT Support Tickets' }} />
      <Stack.Screen name="Visitor" component={VisitorScreen} options={{ headerTitle: 'Visitor Pass' }} />
      <Stack.Screen name="Shuttle" component={ShuttleScreen} options={{ headerTitle: 'Shuttle Routes' }} />
    </Stack.Navigator>
  );
}

export default function AppNavigator() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: COLORS.primary }}>
        <ActivityIndicator size="large" color="#fff" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      {user ? <MainStack /> : <LoginScreen />}
    </NavigationContainer>
  );
}

