import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Title, Paragraph, Button, TextInput, HelperText, Chip, List } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { getVisitors, registerVisitor } from '../services/api';
import { COLORS, SPACING, SHADOWS } from '../constants/Theme';

export default function VisitorScreen() {
  const { user } = useAuth();
  const [visitors, setVisitors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [purpose, setPurpose] = useState('');
  const [visitDate, setVisitDate] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadVisitors();
  }, []);

  const loadVisitors = async () => {
    try {
      setLoading(true);
      const response = await getVisitors(user.user_id);
      if (response.success) {
        setVisitors(response.data);
      }
    } catch (err) {
      console.error('Error loading visitors:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRegisterVisitor = async () => {
    setError('');
    setSuccess('');

    if (!name || !email || !visitDate) {
      setError('Name, email, and visit date are required');
      return;
    }

    try {
      setLoading(true);
      const response = await registerVisitor({
        name,
        email,
        phone,
        purpose,
        visit_date: visitDate,
        host_employee_id: user.user_id
      });

      if (response.success) {
        setSuccess('Visitor registered successfully!');
        setName('');
        setEmail('');
        setPhone('');
        setPurpose('');
        setVisitDate('');
        setShowForm(false);
        setTimeout(() => setSuccess(''), 3000);
        loadVisitors();
      } else {
        setError(response.message || 'Failed to register visitor');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadVisitors(); }} />}
    >
      <View style={styles.header}>
        <Button
          mode="contained"
          onPress={() => setShowForm(!showForm)}
          icon={showForm ? "close" : "account-plus"}
          style={styles.actionButton}
        >
          {showForm ? "Cancel" : "Register Visitor"}
        </Button>
      </View>

      {showForm && (
        <Card style={styles.card}>
          <Card.Content>
            <Title>Visitor Registration</Title>

            <TextInput
              label="Visitor Name"
              value={name}
              onChangeText={setName}
              mode="outlined"
              style={styles.input}
            />

            <TextInput
              label="Email Address"
              value={email}
              onChangeText={setEmail}
              mode="outlined"
              keyboardType="email-address"
              style={styles.input}
            />

            <TextInput
              label="Phone Number"
              value={phone}
              onChangeText={setPhone}
              mode="outlined"
              keyboardType="phone-pad"
              style={styles.input}
            />

            <TextInput
              label="Visit Date (YYYY-MM-DD)"
              value={visitDate}
              onChangeText={setVisitDate}
              mode="outlined"
              style={styles.input}
              placeholder="2026-03-10"
            />

            <TextInput
              label="Purpose of Visit"
              value={purpose}
              onChangeText={setPurpose}
              mode="outlined"
              multiline
              numberOfLines={2}
              style={styles.input}
            />

            {error ? <HelperText type="error">{error}</HelperText> : null}
            {success ? <HelperText type="info">{success}</HelperText> : null}

            <Button
              mode="contained"
              onPress={handleRegisterVisitor}
              loading={loading}
              style={styles.submitButton}
            >
              Register
            </Button>
          </Card.Content>
        </Card>
      )}

      <Title style={styles.sectionTitle}>Upcoming Visitors</Title>
      {visitors.length === 0 ? (
        <Card style={styles.card}>
          <Card.Content>
            <Paragraph style={styles.emptyText}>No visitors registered</Paragraph>
          </Card.Content>
        </Card>
      ) : (
        visitors.map((visitor, index) => (
          <Card key={index} style={styles.visitorCard}>
            <List.Item
              title={visitor.name}
              description={`📅 ${visitor.visit_date}\n📧 ${visitor.email} | 📞 ${visitor.phone || 'N/A'}`}
              descriptionNumberOfLines={2}
              left={props => <List.Icon {...props} icon="account" color={COLORS.primary} />}
              right={props => (
                <Chip style={styles.statusChip}>{visitor.status || 'Scheduled'}</Chip>
              )}
            />
          </Card>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  header: { padding: 16 },
  actionButton: { borderRadius: 12 },
  card: { marginHorizontal: 16, marginBottom: 16, borderRadius: 16, elevation: 2 },
  visitorCard: { marginHorizontal: 16, marginBottom: 8, borderRadius: 12, elevation: 1 },
  input: { marginBottom: 12 },
  submitButton: { marginTop: 8 },
  sectionTitle: { marginLeft: 16, marginBottom: 8, fontSize: 18, fontWeight: '700' },
  statusChip: { alignSelf: 'center', backgroundColor: COLORS.primary + '15' },
  emptyText: { textAlign: 'center', color: COLORS.textMuted, paddingVertical: 20 }
});

