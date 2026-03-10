import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Title, Paragraph, Button, HelperText } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { clockIn, clockOut, getAttendance } from '../services/api';

export default function AttendanceScreen() {
  const { user } = useAuth();
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadAttendance();
  }, []);

  const loadAttendance = async () => {
    try {
      const response = await getAttendance(user.user_id);
      if (response.success) {
        setAttendance(response.data);
      }
    } catch (err) {
      console.error('Error loading attendance:', err);
    }
  };

  const handleClockIn = async () => {
    try {
      setLoading(true);
      setMessage('');
      const response = await clockIn(user.user_id);
      if (response.success) {
        setMessage('✅ Clocked in successfully!');
        loadAttendance();
      } else {
        setMessage('❌ ' + (response.message || 'Failed to clock in'));
      }
    } catch (err) {
      setMessage('❌ Network error');
    } finally {
      setLoading(false);
    }
  };

  const handleClockOut = async () => {
    try {
      setLoading(true);
      setMessage('');
      const response = await clockOut(user.user_id);
      if (response.success) {
        setMessage('✅ Clocked out successfully!');
        loadAttendance();
      } else {
        setMessage('❌ ' + (response.message || 'Failed to clock out'));
      }
    } catch (err) {
      setMessage('❌ Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>⏰ Clock In/Out</Title>
          <Paragraph style={styles.subtitle}>Track your attendance</Paragraph>
          
          <View style={styles.buttonRow}>
            <Button
              mode="contained"
              onPress={handleClockIn}
              loading={loading}
              style={[styles.button, { backgroundColor: '#4caf50' }]}
              icon="login"
            >
              Clock In
            </Button>
            <Button
              mode="contained"
              onPress={handleClockOut}
              loading={loading}
              style={[styles.button, { backgroundColor: '#f44336' }]}
              icon="logout"
            >
              Clock Out
            </Button>
          </View>

          {message ? <HelperText type="info" visible style={styles.message}>{message}</HelperText> : null}
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Recent Attendance</Title>
          {attendance.length === 0 ? (
            <Paragraph style={styles.emptyText}>No attendance records</Paragraph>
          ) : (
            attendance.slice(0, 10).map((record, index) => (
              <View key={index} style={styles.recordItem}>
                <Paragraph style={styles.recordDate}>📅 {record.date}</Paragraph>
                <View style={styles.timeRow}>
                  <Paragraph style={styles.timeText}>In: {record.clock_in || 'N/A'}</Paragraph>
                  <Paragraph style={styles.timeText}>Out: {record.clock_out || 'N/A'}</Paragraph>
                </View>
              </View>
            ))
          )}
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 16,
    marginBottom: 8,
    elevation: 2,
  },
  subtitle: {
    color: '#666',
    marginBottom: 16,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  button: {
    flex: 1,
    marginHorizontal: 4,
  },
  message: {
    marginTop: 12,
    textAlign: 'center',
  },
  recordItem: {
    backgroundColor: '#f9f9f9',
    padding: 12,
    marginTop: 8,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#667eea',
  },
  recordDate: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  timeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  timeText: {
    fontSize: 13,
    color: '#666',
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    marginTop: 16,
  },
});

