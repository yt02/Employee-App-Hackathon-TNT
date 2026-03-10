import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Title, Paragraph, Button, TextInput, HelperText, Chip, List, Divider } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { getTickets, createTicket } from '../services/api';
import { COLORS, SPACING, SHADOWS } from '../constants/Theme';

export default function TicketsScreen() {
  const { user } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Software');
  const [priority, setPriority] = useState('Medium');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const categories = ['Software', 'Hardware', 'Network', 'Access', 'Other'];
  const priorities = ['Low', 'Medium', 'High', 'Urgent'];

  useEffect(() => {
    loadTickets();
  }, []);

  const loadTickets = async () => {
    try {
      setLoading(true);
      const response = await getTickets(user.user_id);
      if (response.success) {
        setTickets(response.data);
      }
    } catch (err) {
      console.error('Error loading tickets:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleCreateTicket = async () => {
    setError('');
    setSuccess('');

    if (!title || !description) {
      setError('Please fill in title and description');
      return;
    }

    try {
      setLoading(true);
      const response = await createTicket(user.user_id, {
        title,
        description,
        category,
        priority
      });

      if (response.success) {
        setSuccess('Ticket created successfully!');
        setTitle('');
        setDescription('');
        setShowForm(false);
        setTimeout(() => setSuccess(''), 3000);
        loadTickets();
      } else {
        setError(response.message || 'Failed to create ticket');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (p) => {
    switch (p.toLowerCase()) {
      case 'urgent': return '#f44336';
      case 'high': return '#ff9800';
      case 'medium': return '#2196f3';
      case 'low': return '#4caf50';
      default: return '#757575';
    }
  };

  const getStatusColor = (s) => {
    switch (s.toLowerCase()) {
      case 'open': return '#2196f3';
      case 'in_progress': return '#ff9800';
      case 'resolved': return '#4caf50';
      case 'closed': return '#757575';
      default: return '#757575';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadTickets(); }} />}
    >
      <View style={styles.header}>
        <Button
          mode="contained"
          onPress={() => setShowForm(!showForm)}
          icon={showForm ? "close" : "plus"}
          style={styles.actionButton}
        >
          {showForm ? "Cancel" : "Create New Ticket"}
        </Button>
      </View>

      {showForm && (
        <Card style={styles.card}>
          <Card.Content>
            <Title>Submit Support Ticket</Title>

            <TextInput
              label="Title"
              value={title}
              onChangeText={setTitle}
              mode="outlined"
              style={styles.input}
            />

            <Paragraph style={styles.label}>Category</Paragraph>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.chipScroll}>
              {categories.map(cat => (
                <Chip
                  key={cat}
                  selected={category === cat}
                  onPress={() => setCategory(cat)}
                  style={styles.chip}
                >
                  {cat}
                </Chip>
              ))}
            </ScrollView>

            <Paragraph style={styles.label}>Priority</Paragraph>
            <View style={styles.priorityContainer}>
              {priorities.map(p => (
                <Chip
                  key={p}
                  selected={priority === p}
                  onPress={() => setPriority(p)}
                  style={styles.chip}
                >
                  {p}
                </Chip>
              ))}
            </View>

            <TextInput
              label="Description"
              value={description}
              onChangeText={setDescription}
              mode="outlined"
              multiline
              numberOfLines={4}
              style={styles.input}
            />

            {error ? <HelperText type="error">{error}</HelperText> : null}
            {success ? <HelperText type="info">{success}</HelperText> : null}

            <Button
              mode="contained"
              onPress={handleCreateTicket}
              loading={loading}
              style={styles.submitButton}
            >
              Submit Ticket
            </Button>
          </Card.Content>
        </Card>
      )}

      <Title style={styles.sectionTitle}>My Tickets</Title>
      {tickets.length === 0 ? (
        <Card style={styles.card}>
          <Card.Content>
            <Paragraph style={styles.emptyText}>No tickets found</Paragraph>
          </Card.Content>
        </Card>
      ) : (
        tickets.map((ticket, index) => (
          <Card key={index} style={styles.ticketCard}>
            <Card.Content>
              <View style={styles.ticketHeader}>
                <Title style={styles.ticketTitle}>{ticket.title}</Title>
                <Chip
                  style={{ backgroundColor: getStatusColor(ticket.status || 'open') }}
                  textStyle={{ color: 'white', fontSize: 10 }}
                >
                  {(ticket.status || 'open').toUpperCase()}
                </Chip>
              </View>

              <View style={styles.metaRow}>
                <View style={[styles.metaBadge, { backgroundColor: getPriorityColor(ticket.priority || 'Medium') + '20' }]}>
                  <Paragraph style={[styles.metaText, { color: getPriorityColor(ticket.priority || 'Medium') }]}>
                    {ticket.priority || 'Medium'}
                  </Paragraph>
                </View>
                <Paragraph style={styles.categoryText}>{ticket.category}</Paragraph>
                <Paragraph style={styles.dateText}>{ticket.created_at?.split('T')[0] || 'Today'}</Paragraph>
              </View>

              <Paragraph numberOfLines={2} style={styles.description}>
                {ticket.description}
              </Paragraph>
            </Card.Content>
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
  ticketCard: { marginHorizontal: 16, marginBottom: 12, borderRadius: 16, elevation: 1 },
  input: { marginBottom: 12 },
  label: { marginTop: 8, marginBottom: 4, fontWeight: '600' },
  chipScroll: { marginBottom: 8 },
  chip: { marginRight: 8, marginBottom: 4 },
  priorityContainer: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 12 },
  submitButton: { marginTop: 8 },
  sectionTitle: { marginLeft: 16, marginBottom: 8, fontSize: 18, fontWeight: '700' },
  ticketHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  ticketTitle: { flex: 1, fontSize: 16, marginRight: 8 },
  metaRow: { flexDirection: 'row', alignItems: 'center', marginTop: 4, marginBottom: 8 },
  metaBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 4, marginRight: 8 },
  metaText: { fontSize: 10, fontWeight: '700' },
  categoryText: { fontSize: 12, color: COLORS.textMuted, marginRight: 8 },
  dateText: { fontSize: 12, color: COLORS.textMuted },
  description: { fontSize: 14, color: COLORS.text, opacity: 0.8 },
  emptyText: { textAlign: 'center', color: COLORS.textMuted, paddingVertical: 20 },
});

