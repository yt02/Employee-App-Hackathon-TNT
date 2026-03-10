import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Title, Paragraph, Button, TextInput, HelperText, DataTable, Chip } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { getLeaveBalance, applyLeave, getLeaveHistory } from '../services/api';

export default function LeaveScreen() {
  const { user } = useAuth();
  const [balance, setBalance] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [leaveType, setLeaveType] = useState('annual');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [balanceRes, historyRes] = await Promise.all([
        getLeaveBalance(user.user_id),
        getLeaveHistory(user.user_id)
      ]);

      if (balanceRes.success) setBalance(balanceRes.data);
      if (historyRes.success) setHistory(historyRes.data);
    } catch (err) {
      console.error('Error loading leave data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const validateDate = (dateString) => {
    const regEx = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateString.match(regEx)) return false;
    const d = new Date(dateString);
    const dNum = d.getTime();
    if (!dNum && dNum !== 0) return false;
    return d.toISOString().slice(0, 10) === dateString;
  };

  const handleApplyLeave = async () => {
    setError('');
    setSuccess('');

    if (!startDate || !endDate || !reason) {
      setError('Please fill in all fields');
      return;
    }

    if (!validateDate(startDate) || !validateDate(endDate)) {
      setError('Please use YYYY-MM-DD format');
      return;
    }

    if (new Date(startDate) > new Date(endDate)) {
      setError('Start date cannot be after end date');
      return;
    }

    try {
      setLoading(true);
      const response = await applyLeave(user.user_id, {
        leave_type: leaveType,
        start_date: startDate,
        end_date: endDate,
        reason: reason
      });

      if (response.success) {
        setSuccess('Leave application submitted successfully!');
        setStartDate('');
        setEndDate('');
        setReason('');
        setShowForm(false);
        setTimeout(() => setSuccess(''), 3000);
        loadData();
      } else {
        setError(response.message || 'Failed to apply leave');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return '#4caf50';
      case 'pending': return '#ff9800';
      case 'rejected': return '#f44336';
      default: return '#757575';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} />}
    >
      {/* Leave Balance */}
      {balance && (
        <Card style={styles.card}>
          <Card.Content>
            <Title>Leave Balance</Title>
            <View style={styles.balanceGrid}>
              <View style={styles.balanceItem}>
                <Paragraph style={styles.balanceLabel}>Annual</Paragraph>
                <Title style={styles.balanceValue}>{balance.annual || 0}</Title>
              </View>
              <View style={styles.balanceItem}>
                <Paragraph style={styles.balanceLabel}>Sick</Paragraph>
                <Title style={styles.balanceValue}>{balance.sick || 0}</Title>
              </View>
              <View style={styles.balanceItem}>
                <Paragraph style={styles.balanceLabel}>Personal</Paragraph>
                <Title style={styles.balanceValue}>{balance.personal || 0}</Title>
              </View>
            </View>
          </Card.Content>
        </Card>
      )}

      {/* Apply Leave Button */}
      <Button
        mode="contained"
        onPress={() => setShowForm(!showForm)}
        style={styles.applyButton}
        icon={showForm ? 'close' : 'plus'}
      >
        {showForm ? 'Cancel' : 'Apply for Leave'}
      </Button>

      {/* Apply Leave Form */}
      {showForm && (
        <Card style={styles.card}>
          <Card.Content>
            <Title>Apply for Leave</Title>

            <Paragraph style={styles.label}>Leave Type</Paragraph>
            <View style={styles.chipContainer}>
              <Chip selected={leaveType === 'annual'} onPress={() => setLeaveType('annual')} style={styles.chip}>Annual</Chip>
              <Chip selected={leaveType === 'sick'} onPress={() => setLeaveType('sick')} style={styles.chip}>Sick</Chip>
              <Chip selected={leaveType === 'personal'} onPress={() => setLeaveType('personal')} style={styles.chip}>Personal</Chip>
            </View>

            <TextInput
              label="Start Date (YYYY-MM-DD)"
              value={startDate}
              onChangeText={setStartDate}
              mode="outlined"
              style={styles.input}
              placeholder="2026-02-10"
            />

            <TextInput
              label="End Date (YYYY-MM-DD)"
              value={endDate}
              onChangeText={setEndDate}
              mode="outlined"
              style={styles.input}
              placeholder="2026-02-12"
            />

            <TextInput
              label="Reason"
              value={reason}
              onChangeText={setReason}
              mode="outlined"
              multiline
              numberOfLines={3}
              style={styles.input}
            />

            {error ? <HelperText type="error" visible>{error}</HelperText> : null}
            {success ? <HelperText type="info" visible>{success}</HelperText> : null}

            <Button mode="contained" onPress={handleApplyLeave} loading={loading}>
              Submit Application
            </Button>
          </Card.Content>
        </Card>
      )}

      {/* Leave History */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Leave History</Title>
          {history.length === 0 ? (
            <Paragraph style={styles.emptyText}>No leave history</Paragraph>
          ) : (
            history.slice(0, 10).map((item, index) => (
              <View key={index} style={styles.historyItem}>
                <View style={styles.historyHeader}>
                  <Paragraph style={styles.historyType}>{item.leave_type?.toUpperCase()}</Paragraph>
                  <Chip
                    style={[styles.statusChip, { backgroundColor: getStatusColor(item.status) }]}
                    textStyle={{ color: 'white', fontSize: 11 }}
                  >
                    {item.status}
                  </Chip>
                </View>
                <Paragraph style={styles.historyDates}>
                  {item.start_date} to {item.end_date}
                </Paragraph>
                <Paragraph style={styles.historyReason}>{item.reason}</Paragraph>
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
  balanceGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  balanceItem: {
    alignItems: 'center',
  },
  balanceLabel: {
    fontSize: 12,
    color: '#666',
  },
  balanceValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#667eea',
  },
  applyButton: {
    marginHorizontal: 16,
    marginVertical: 8,
  },
  label: {
    marginTop: 16,
    marginBottom: 8,
    fontWeight: '600',
  },
  chipContainer: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  chip: {
    marginRight: 8,
  },
  input: {
    marginBottom: 12,
  },
  historyItem: {
    borderLeftWidth: 3,
    borderLeftColor: '#667eea',
    paddingLeft: 12,
    paddingVertical: 12,
    marginTop: 12,
    backgroundColor: '#f9f9f9',
    borderRadius: 4,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  historyType: {
    fontWeight: 'bold',
    fontSize: 14,
  },
  statusChip: {
    paddingVertical: 0,
    marginVertical: 0,
  },
  historyDates: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  historyReason: {
    fontSize: 13,
    fontStyle: 'italic',
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    marginTop: 16,
  },
});

