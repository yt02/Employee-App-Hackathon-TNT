import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Title, Paragraph, Button, TextInput, HelperText, Chip, List } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { getRooms, bookRoom, getUserBookings, cancelBooking } from '../services/api';

function normalizeFacilities(room) {
  const raw = room?.facilities ?? room?.features;

  if (Array.isArray(raw)) {
    return raw.map((item) => String(item).trim()).filter(Boolean);
  }

  if (typeof raw === 'string') {
    // Support comma-separated strings and JSON-ish arrays serialized as strings.
    const trimmed = raw.trim();
    if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
      try {
        const parsed = JSON.parse(trimmed);
        if (Array.isArray(parsed)) {
          return parsed.map((item) => String(item).trim()).filter(Boolean);
        }
      } catch (_) {
        // Fall back to simple split below.
      }
    }
    return raw.split(',').map((item) => item.trim()).filter(Boolean);
  }

  return [];
}

export default function RoomsScreen() {
  const { user } = useAuth();
  const [rooms, setRooms] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showBookForm, setShowBookForm] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState(null);

  // Form state
  const [date, setDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [purpose, setPurpose] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [roomsRes, bookingsRes] = await Promise.all([
        getRooms(),
        getUserBookings(user.user_id)
      ]);

      if (roomsRes.success) {
        const normalizedRooms = (roomsRes.data || []).map((room) => {
          const safeRoom = room && typeof room === 'object' ? room : {};
          return {
            ...safeRoom,
            facilities: normalizeFacilities(safeRoom),
          };
        });
        setRooms(normalizedRooms);
      }
      if (bookingsRes.success) setBookings(bookingsRes.data);
    } catch (err) {
      console.error('Error loading rooms data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const validateTime = (timeString) => {
    const regEx = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
    return regEx.test(timeString);
  };

  const handleBookRoom = async () => {
    setError('');
    setSuccess('');

    if (!selectedRoom || !date || !startTime || !endTime || !purpose) {
      setError('Please fill in all fields');
      return;
    }

    if (!startTime.includes(':') || !endTime.includes(':')) {
      setError('Use HH:MM format (e.g., 09:00)');
      return;
    }

    try {
      setLoading(true);
      const response = await bookRoom(user.user_id, {
        room_id: selectedRoom.room_id,
        date: date,
        start_time: startTime,
        end_time: endTime,
        purpose: purpose
      });

      if (response.success) {
        setSuccess('Room booked successfully!');
        setDate('');
        setStartTime('');
        setEndTime('');
        setPurpose('');
        setShowBookForm(false);
        setSelectedRoom(null);
        setTimeout(() => setSuccess(''), 3000);
        loadData();
      } else {
        setError(response.data?.message || response.message || 'Failed to book room');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelBooking = async (bookingId) => {
    try {
      const response = await cancelBooking(bookingId, user.user_id);
      if (response.success) {
        loadData();
      }
    } catch (err) {
      console.error('Error canceling booking:', err);
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} />}
    >
      {/* Available Rooms */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Available Meeting Rooms</Title>
          {rooms.map((room, index) => (
            <List.Item
              key={index}
              title={room.name}
              description={`Capacity: ${room.capacity}${room.facilities.length ? ` | ${room.facilities.join(', ')}` : ''}`}
              left={props => <List.Icon {...props} icon="door" />}
              right={props => (
                <Button
                  mode="contained"
                  compact
                  onPress={() => {
                    setSelectedRoom(room);
                    setShowBookForm(true);
                  }}
                >
                  Book
                </Button>
              )}
              style={styles.roomItem}
            />
          ))}
        </Card.Content>
      </Card>

      {/* Booking Form */}
      {showBookForm && selectedRoom && (
        <Card style={styles.card}>
          <Card.Content>
            <Title>Book {selectedRoom.name}</Title>

            <TextInput
              label="Date (YYYY-MM-DD)"
              value={date}
              onChangeText={setDate}
              mode="outlined"
              style={styles.input}
              placeholder="2026-02-10"
            />

            <View style={styles.timeRow}>
              <TextInput
                label="Start Time (HH:MM)"
                value={startTime}
                onChangeText={setStartTime}
                mode="outlined"
                style={[styles.input, styles.timeInput]}
                placeholder="09:00"
              />
              <TextInput
                label="End Time (HH:MM)"
                value={endTime}
                onChangeText={setEndTime}
                mode="outlined"
                style={[styles.input, styles.timeInput]}
                placeholder="10:00"
              />
            </View>

            <TextInput
              label="Purpose"
              value={purpose}
              onChangeText={setPurpose}
              mode="outlined"
              multiline
              numberOfLines={2}
              style={styles.input}
            />

            {error ? <HelperText type="error" visible>{error}</HelperText> : null}
            {success ? <HelperText type="info" visible>{success}</HelperText> : null}

            <View style={styles.buttonRow}>
              <Button mode="outlined" onPress={() => { setShowBookForm(false); setSelectedRoom(null); }} style={styles.cancelButton}>
                Cancel
              </Button>
              <Button mode="contained" onPress={handleBookRoom} loading={loading} style={styles.submitButton}>
                Confirm Booking
              </Button>
            </View>
          </Card.Content>
        </Card>
      )}

      {/* My Bookings */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>My Bookings</Title>
          {bookings.length === 0 ? (
            <Paragraph style={styles.emptyText}>No bookings yet</Paragraph>
          ) : (
            bookings.map((booking, index) => (
              <View key={index} style={styles.bookingItem}>
                <View style={styles.bookingHeader}>
                  <Paragraph style={styles.bookingRoom}>{booking.room_name}</Paragraph>
                  <Chip
                    style={[styles.statusChip, { backgroundColor: booking.status === 'confirmed' ? '#4caf50' : '#ff9800' }]}
                    textStyle={{ color: 'white', fontSize: 11 }}
                  >
                    {booking.status}
                  </Chip>
                </View>
                <Paragraph style={styles.bookingDate}>
                  📅 {booking.date} | ⏰ {booking.start_time} - {booking.end_time}
                </Paragraph>
                <Paragraph style={styles.bookingPurpose}>{booking.purpose}</Paragraph>
                {booking.status === 'confirmed' && (
                  <Button
                    mode="text"
                    compact
                    onPress={() => handleCancelBooking(booking.booking_id)}
                    style={styles.cancelBookingButton}
                  >
                    Cancel Booking
                  </Button>
                )}
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
  roomItem: {
    backgroundColor: '#f9f9f9',
    marginTop: 8,
    borderRadius: 8,
  },
  input: {
    marginBottom: 12,
  },
  timeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  timeInput: {
    width: '48%',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  cancelButton: {
    flex: 1,
    marginRight: 8,
  },
  submitButton: {
    flex: 1,
  },
  bookingItem: {
    borderLeftWidth: 3,
    borderLeftColor: '#764ba2',
    paddingLeft: 12,
    paddingVertical: 12,
    marginTop: 12,
    backgroundColor: '#f9f9f9',
    borderRadius: 4,
  },
  bookingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  bookingRoom: {
    fontWeight: 'bold',
    fontSize: 14,
  },
  statusChip: {
    paddingVertical: 0,
    marginVertical: 0,
  },
  bookingDate: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  bookingPurpose: {
    fontSize: 13,
    fontStyle: 'italic',
  },
  cancelBookingButton: {
    alignSelf: 'flex-start',
    marginTop: 4,
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    marginTop: 16,
  },
});
