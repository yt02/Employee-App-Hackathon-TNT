import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Title, Paragraph, Button, List, Chip, HelperText } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { getShuttleRoutes, bookShuttle, getShuttleBookings } from '../services/api';
import { COLORS, SPACING, SHADOWS } from '../constants/Theme';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export default function ShuttleScreen() {
  const { user } = useAuth();
  const [routes, setRoutes] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [routesRes, bookingsRes] = await Promise.all([
        getShuttleRoutes(),
        getShuttleBookings(user.user_id)
      ]);

      if (routesRes.success) setRoutes(routesRes.data);
      if (bookingsRes.success) setBookings(bookingsRes.data);
    } catch (err) {
      console.error('Error loading shuttle data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleBookShuttle = async (route) => {
    setError('');
    setSuccess('');

    try {
      setLoading(true);
      const response = await bookShuttle(user.user_id, {
        route_id: route.id,
        pickup_point: route.stops[0], // Default to first stop
        destination: route.stops[route.stops.length - 1], // Default to last stop
        date: new Date().toISOString().split('T')[0],
        time: route.departure_time
      });

      if (response.success) {
        setSuccess(`Booked ${route.name} successfully!`);
        setTimeout(() => setSuccess(''), 3000);
        loadData();
      } else {
        setError(response.message || 'Failed to book shuttle');
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
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} />}
    >
      <Title style={styles.sectionTitle}>Available Routes</Title>

      {error ? <HelperText type="error" style={styles.msg}>{error}</HelperText> : null}
      {success ? <HelperText type="info" style={styles.msg}>{success}</HelperText> : null}

      {routes.length === 0 ? (
        <Paragraph style={styles.emptyText}>No routes available</Paragraph>
      ) : (
        routes.map((route, index) => (
          <Card key={index} style={styles.card}>
            <Card.Content>
              <View style={styles.routeHeader}>
                <Title>{route.name}</Title>
                <Chip icon="clock" style={styles.timeChip}>{route.departure_time}</Chip>
              </View>

              <View style={styles.stopsContainer}>
                {route.stops.map((stop, sIdx) => (
                  <View key={sIdx} style={styles.stopRow}>
                    <MaterialCommunityIcons
                      name={sIdx === 0 ? "record-circle" : (sIdx === route.stops.length - 1 ? "map-marker" : "circle-outline")}
                      size={18}
                      color={sIdx === 0 ? COLORS.primary : (sIdx === route.stops.length - 1 ? COLORS.secondary : COLORS.textMuted)}
                    />
                    <Paragraph style={styles.stopText}>{stop}</Paragraph>
                  </View>
                ))}
              </View>

              <Button
                mode="contained"
                onPress={() => handleBookShuttle(route)}
                loading={loading}
                style={styles.bookButton}
              >
                Book Seat
              </Button>
            </Card.Content>
          </Card>
        ))
      )}

      <Title style={styles.sectionTitle}>My Bookings</Title>
      {bookings.length === 0 ? (
        <Card style={styles.card}>
          <Card.Content>
            <Paragraph style={styles.emptyText}>No active bookings</Paragraph>
          </Card.Content>
        </Card>
      ) : (
        bookings.map((booking, index) => (
          <Card key={index} style={styles.bookingCard}>
            <List.Item
              title={booking.route_name}
              description={`📅 ${booking.date} | ⏰ ${booking.time}\n📍 ${booking.pickup_point} → ${booking.destination}`}
              descriptionNumberOfLines={2}
              left={props => <List.Icon {...props} icon="bus" color={COLORS.primary} />}
              right={props => (
                <Chip style={styles.statusChip}>{booking.status}</Chip>
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
  sectionTitle: { marginLeft: 16, marginTop: 16, marginBottom: 8, fontSize: 18, fontWeight: '700' },
  card: { marginHorizontal: 16, marginBottom: 16, borderRadius: 16, elevation: 2 },
  bookingCard: { marginHorizontal: 16, marginBottom: 8, borderRadius: 12, elevation: 1 },
  routeHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  timeChip: { backgroundColor: COLORS.primary + '15' },
  stopsContainer: { marginLeft: 8, marginBottom: 16 },
  stopRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 4 },
  stopText: { marginLeft: 12, fontSize: 14 },
  bookButton: { borderRadius: 12 },
  statusChip: { alignSelf: 'center', backgroundColor: COLORS.success + '20' },
  emptyText: { textAlign: 'center', color: COLORS.textMuted, paddingVertical: 20 },
  msg: { marginHorizontal: 16 }
});

