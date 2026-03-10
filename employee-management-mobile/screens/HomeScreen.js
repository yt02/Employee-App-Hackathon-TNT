import React from 'react';
import { View, StyleSheet, ScrollView, Text, TouchableOpacity, Platform } from 'react-native';
import { Avatar, Card, Title, Paragraph, Button } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';
import { COLORS, SPACING, SHADOWS } from '../constants/Theme';

export default function HomeScreen({ navigation }) {
  const { user, logout } = useAuth();
  const role = user?.role || 'employee';

  const ALL_QUICK_ACTIONS = [
    { title: 'Assistant', icon: 'robot', screen: 'Assistant', color: COLORS.primary, roles: ['employee', 'hr_manager', 'facility_manager', 'fitness_instructor', 'shuttle_driver', 'admin'] },
    { title: 'Apply Leave', icon: 'calendar-remove', screen: 'Leave', color: '#818CF8', roles: ['employee', 'admin'] },
    { title: 'Book Room', icon: 'door', screen: 'Rooms', color: COLORS.secondary, roles: ['employee', 'admin'] },
    { title: 'Clock In/Out', icon: 'clock-outline', screen: 'Attendance', color: '#2DD4BF', roles: ['employee', 'admin'] },
    { title: 'Create Ticket', icon: 'ticket', screen: 'Tickets', color: '#F87171', roles: ['employee', 'admin'] },
    { title: 'Pending Tickets', icon: 'ticket-confirmation', screen: 'Tickets', color: '#F87171', roles: ['facility_manager', 'admin'] },
    { title: 'Start Route', icon: 'bus', screen: 'Shuttle', color: '#60A5FA', roles: ['shuttle_driver', 'admin'] },
  ];

  const quickActions = ALL_QUICK_ACTIONS.filter(action => action.roles.includes(role));

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.headerContainer}>
        <View style={styles.profileSection}>
          <Avatar.Text
            size={56}
            label={user?.name?.substring(0, 2).toUpperCase() || 'EM'}
            style={styles.avatar}
            labelStyle={styles.avatarLabel}
          />
          <View style={styles.headerText}>
            <Text style={styles.greeting}>Hello,</Text>
            <Text style={styles.userName}>{user?.name || 'Employee'}</Text>
            <View style={styles.badge}>
              <Text style={styles.roleLabel}>{user?.role?.replace('_', ' ').toUpperCase() || 'Employee'}</Text>
            </View>
          </View>
        </View>
      </View>

      <Title style={styles.sectionTitle}>Main Hub</Title>
      <View style={styles.actionsGrid}>
        {quickActions.map((action, index) => (
          <TouchableOpacity
            key={index}
            style={[styles.actionCard, SHADOWS.sm]}
            onPress={() => navigation.navigate(action.screen)}
            activeOpacity={0.7}
          >
            <View style={[styles.iconContainer, { backgroundColor: action.color + '15' }]}>
              <MaterialCommunityIcons name={action.icon} size={28} color={action.color} />
            </View>
            <Text style={styles.actionTitle}>{action.title}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.footer}>
        <Button
          mode="text"
          onPress={logout}
          style={styles.logoutButton}
          labelStyle={styles.logoutLabel}
          icon="logout"
        >
          Sign Out
        </Button>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  content: {
    paddingBottom: SPACING.xl,
  },
  headerContainer: {
    padding: SPACING.lg,
    paddingTop: SPACING.xl,
    backgroundColor: COLORS.surface,
    borderBottomLeftRadius: 32,
    borderBottomRightRadius: 32,
    ...SHADOWS.md,
  },
  profileSection: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    backgroundColor: COLORS.primary,
  },
  avatarLabel: {
    fontWeight: '700',
    color: COLORS.white,
  },
  headerText: {
    marginLeft: SPACING.md,
  },
  greeting: {
    fontSize: 14,
    color: COLORS.textMuted,
    fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif',
  },
  userName: {
    fontSize: 22,
    fontWeight: '800',
    color: COLORS.text,
    marginVertical: 2,
  },
  badge: {
    backgroundColor: COLORS.primary + '10',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    alignSelf: 'flex-start',
    marginTop: 4,
  },
  roleLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: COLORS.primary,
    letterSpacing: 0.5,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.text,
    marginLeft: SPACING.lg,
    marginTop: SPACING.xl,
    marginBottom: SPACING.md,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: SPACING.md,
  },
  actionCard: {
    width: '45%',
    margin: '2.5%',
    backgroundColor: COLORS.surface,
    borderRadius: 20,
    padding: SPACING.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: SPACING.sm,
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.text,
    textAlign: 'center',
  },
  footer: {
    marginTop: SPACING.xxl,
    alignItems: 'center',
  },
  logoutButton: {
    width: '60%',
  },
  logoutLabel: {
    color: COLORS.error,
    fontWeight: '600',
  },
});

