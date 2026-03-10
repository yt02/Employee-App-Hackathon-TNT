import React, { useState, useRef, useEffect } from 'react';
import { View, StyleSheet, FlatList, KeyboardAvoidingView, Platform, Text, Keyboard, ScrollView, Animated, Image, TouchableOpacity } from 'react-native';
import { TextInput, IconButton, Surface, ActivityIndicator, Button, Avatar, Chip, Card, Title, Paragraph } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import Markdown from 'react-native-markdown-display';
import { useAuth } from '../contexts/AuthContext';
import { sendChatMessageStream, confirmChatAction } from '../services/api';
import * as Calendar from 'expo-calendar';
import * as Notifications from 'expo-notifications';
import { COLORS, SPACING, SHADOWS } from '../constants/Theme';

const DEFAULT_SUGGESTIONS = [
    "📅 Check leave balance",
    "🏢 Available rooms",
    "📝 Apply for leave",
    "🎫 My tickets",
    "📍 Book a room",
    "🆕 New IT ticket"
];

const LEAVE_SUGGESTIONS = ["📊 Check balance", "📝 Apply annual leave", "🏥 Apply medical leave", "📋 My leave requests"];
const ROOM_SUGGESTIONS = ["🏢 View all rooms", "📍 Book Room A", "📍 Book Room B", "📅 My bookings"];
const TICKET_SUGGESTIONS = ["🆕 Software issue", "🆕 Hardware issue", "🌐 Network issue", "🎫 My tickets"];

const COMMAND_MENU = [
    { title: '/leave', desc: 'Apply for leave or check balance', icon: 'calendar-clock', command: 'I want to apply for leave' },
    { title: '/room', desc: 'Book a meeting workspace', icon: 'office-building', command: 'I want to book a room' },
    { title: '/ticket', desc: 'Create an IT support ticket', icon: 'ticket', command: 'I want to create an IT ticket' },
    { title: '/visitor', desc: 'Register a new guest visitor', icon: 'account-group', command: 'I want to register a visitor' },
    { title: '/shuttle', desc: 'Display shuttle menu', icon: 'bus', command: 'I want to display the shuttle menu' },
];

const VISITOR_FORM_FIELDS = [
    'visitor_name',
    'visitor_ic',
    'looking_for',
    'date',
    'time',
    'company',
    'visitor_email',
    'to_date',
    'purpose',
];

const VISITOR_LABELS = {
    visitor_name: 'Visitor Name',
    visitor_ic: 'Visitor IC / Passport',
    looking_for: 'Visiting Person / Department',
    date: 'Arrival Date',
    time: 'Arrival Time',
    company: 'Company (Optional)',
    visitor_email: 'Visitor Email (Optional)',
    to_date: 'End Date (Optional)',
    purpose: 'Purpose (Optional)',
};

const RoomList = ({ rooms, onBook }) => (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.roomListScroll}>
        {rooms.map((room, idx) => (
            <Surface key={idx} style={[styles.roomCard, SHADOWS.md]} elevation={0}>
                <Image source={{ uri: `https://picsum.photos/seed/${room.room_id}/400/200` }} style={styles.roomImage} />
                <View style={styles.roomCardContent}>
                    <Text style={styles.roomName}>{room.name}</Text>
                    <View style={styles.roomDetails}>
                        <MaterialCommunityIcons name="account-group" size={16} color={COLORS.textMuted} />
                        <Text style={styles.roomCapacity}> {room.capacity} seats</Text>
                    </View>
                    <View style={styles.featureChips}>
                        {(Array.isArray(room.features) ? room.features :
                            (typeof room.features === 'string' ? room.features.split(',') : [])
                        ).slice(0, 3).map((f, i) => (
                            <View key={i} style={styles.featureBadge}>
                                <Text style={styles.featureText}>{String(f).trim()}</Text>
                            </View>
                        ))}
                    </View>
                    <Button
                        mode="contained"
                        onPress={() => onBook(room.name)}
                        style={styles.roomButton}
                        buttonColor={COLORS.secondary}
                        labelStyle={styles.roomButtonLabel}
                        contentStyle={{ height: 36 }}
                    >
                        Book Now
                    </Button>
                </View>
            </Surface>
        ))}
    </ScrollView>
);

const TicketList = ({ tickets }) => (
    <View style={styles.ticketListContainer}>
        {tickets.map((tkt, idx) => {
            const isOpen = tkt.status === 'open';
            return (
                <Surface key={idx} style={[styles.ticketCard, SHADOWS.sm]} elevation={0}>
                    <View style={[styles.ticketAccent, { backgroundColor: isOpen ? COLORS.secondary : COLORS.success }]} />
                    <View style={styles.ticketInner}>
                        <View style={styles.ticketHeader}>
                            <Text style={styles.ticketId}>{tkt.ticket_id.toUpperCase()}</Text>
                            <View style={[styles.statusBadge, { backgroundColor: isOpen ? COLORS.secondary + '15' : COLORS.success + '15' }]}>
                                <Text style={[styles.statusText, { color: isOpen ? COLORS.secondary : COLORS.success }]}>{tkt.status.toUpperCase()}</Text>
                            </View>
                        </View>
                        <Text style={styles.ticketSubject} numberOfLines={1}>{tkt.subject}</Text>
                        <Text style={styles.ticketDesc} numberOfLines={2}>{tkt.description}</Text>
                        <View style={styles.ticketFooter}>
                            <View style={styles.priorityGroup}>
                                <MaterialCommunityIcons name="alert-circle-outline" size={14} color={COLORS.primary} />
                                <Text style={styles.priorityText}> {tkt.priority.toUpperCase()}</Text>
                            </View>
                            <Text style={styles.ticketDate}>{tkt.created_at.split(' ')[0]}</Text>
                        </View>
                    </View>
                </Surface>
            )
        })}
    </View>
);

const VisitorList = ({ visitors }) => (
    <View style={styles.visitorListContainer}>
        {visitors.map((visitor, idx) => (
            <Surface key={idx} style={[styles.visitorCard, SHADOWS.sm]} elevation={0}>
                <View style={[styles.cardIconBox, { backgroundColor: COLORS.primary + '10' }]}>
                    <MaterialCommunityIcons name="account-check" size={24} color={COLORS.primary} />
                </View>
                <View style={styles.cardContent}>
                    <Text style={styles.cardTitle}>{visitor.visitor_name}</Text>
                    <Text style={styles.cardSub}>{visitor.company}</Text>
                    <View style={styles.cardFooter}>
                        <MaterialCommunityIcons name="calendar-clock" size={14} color={COLORS.textMuted} />
                        <Text style={styles.cardFooterText}> {visitor.date} @ {visitor.time}</Text>
                    </View>
                </View>
            </Surface>
        ))}
    </View>
);

const BookingList = ({ bookings }) => {
    const handleAddToCalendar = async (booking) => {
        try {
            const { status } = await Calendar.requestCalendarPermissionsAsync();
            if (status !== 'granted') {
                alert('Calendar permission is required to add events.');
                return;
            }

            const calendars = await Calendar.getCalendarsAsync(Calendar.EntityTypes.EVENT);
            const defaultCalendar = calendars.find(c => c.isPrimary) || calendars[0];

            if (!defaultCalendar) {
                alert('No native calendar found on this device.');
                return;
            }

            const startDate = new Date(`${booking.date}T${booking.start_time}:00`);
            const endDate = new Date(`${booking.date}T${booking.end_time}:00`);

            await Calendar.createEventAsync(defaultCalendar.id, {
                title: `📅 Meeting: ${booking.room_name || booking.room_id}`,
                startDate,
                endDate,
                location: booking.room_name || booking.room_id,
                notes: `Booking ID: ${booking.booking_id}\nPurpose: ${booking.purpose || 'N/A'}`,
            });

            alert('Added to calendar successfully!');
        } catch (e) {
            console.error(e);
            alert('Failed to add to calendar.');
        }
    };

    const handleSetReminder = async (booking) => {
        try {
            const { status } = await Notifications.requestPermissionsAsync();
            if (status !== 'granted') {
                alert('Notification permission is required to set reminders.');
                return;
            }

            const meetingTime = new Date(`${booking.date}T${booking.start_time}:00`);
            const reminderTime = new Date(meetingTime.getTime() - 15 * 60000); // 15 mins before

            if (reminderTime < new Date()) {
                alert('This meeting is too soon or in the past to set a reminder.');
                return;
            }

            await Notifications.scheduleNotificationAsync({
                content: {
                    title: "🔔 Meeting Reminder",
                    body: `Your meeting in ${booking.room_name || booking.room_id} starts in 15 minutes!`,
                    data: { bookingId: booking.booking_id },
                },
                trigger: reminderTime,
            });

            alert('Reminder set for 15 minutes before the meeting!');
        } catch (e) {
            console.error(e);
            alert('Failed to set reminder.');
        }
    };

    return (
        <View style={styles.bookingListContainer}>
            {bookings.map((booking, idx) => (
                <Surface key={idx} style={[styles.bookingCard, SHADOWS.sm]} elevation={0}>
                    <View style={styles.bookingHeader}>
                        <View style={[styles.cardIconBox, { backgroundColor: COLORS.primary + '15' }]}>
                            <MaterialCommunityIcons name="office-building" size={20} color={COLORS.primary} />
                        </View>
                        <View style={{ flex: 1 }}>
                            <Text style={styles.bookingRoomName} numberOfLines={1}>
                                {booking.room_name || booking.room_id}
                            </Text>
                            <Text style={styles.bookingIdText}>ID: {booking.booking_id}</Text>
                        </View>
                        <View style={styles.statusBadgeSmall}>
                            <Text style={styles.statusTextSmall}>CONFIRMED</Text>
                        </View>
                    </View>

                    <View style={styles.bookingDetailRow}>
                        <View style={styles.detailItem}>
                            <MaterialCommunityIcons name="calendar" size={14} color={COLORS.textMuted} />
                            <Text style={styles.detailText}> {booking.date}</Text>
                        </View>
                        <View style={styles.detailItem}>
                            <MaterialCommunityIcons name="clock-outline" size={14} color={COLORS.textMuted} />
                            <Text style={styles.detailText}> {booking.start_time} - {booking.end_time}</Text>
                        </View>
                    </View>

                    {booking.purpose && (
                        <View style={styles.purposeBox}>
                            <MaterialCommunityIcons name="text-subject" size={14} color={COLORS.textMuted} />
                            <Text style={styles.purposeText} numberOfLines={2}> {booking.purpose}</Text>
                        </View>
                    )}

                    <View style={styles.bookingActions}>
                        <TouchableOpacity style={styles.bookingActionBtn} onPress={() => handleAddToCalendar(booking)}>
                            <MaterialCommunityIcons name="calendar-plus" size={16} color={COLORS.secondary} />
                            <Text style={styles.bookingActionLabel}>Calendar</Text>
                        </TouchableOpacity>
                        <View style={styles.actionDivider} />
                        <TouchableOpacity style={styles.bookingActionBtn} onPress={() => handleSetReminder(booking)}>
                            <MaterialCommunityIcons name="bell-ring-outline" size={16} color={COLORS.success} />
                            <Text style={styles.bookingActionLabel}>Reminder</Text>
                        </TouchableOpacity>
                    </View>
                </Surface>
            ))}
        </View>
    );
};

const ShuttleList = ({ routes, onBook }) => (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.horizontalScroll}>
        {routes.map((route, idx) => (
            <Surface key={idx} style={[styles.shuttleCard, SHADOWS.md]} elevation={0}>
                <View style={styles.shuttleHeader}>
                    <View style={[styles.cardIconBox, { backgroundColor: COLORS.secondary + '15' }]}>
                        <MaterialCommunityIcons name="bus" size={20} color={COLORS.secondary} />
                    </View>
                    <View>
                        <Text style={styles.shuttleName}>{route.name}</Text>
                        <Text style={styles.shuttleTime}>Departs: {route.departure_time}</Text>
                    </View>
                </View>
                <View style={styles.stopsTrack}>
                    {route.stops.map((stop, sIdx) => (
                        <View key={sIdx} style={styles.stopPoint}>
                            <View style={[styles.stopDot, sIdx === 0 && { backgroundColor: COLORS.secondary }]} />
                            <Text style={styles.stopLabel} numberOfLines={1}>{stop}</Text>
                        </View>
                    ))}
                </View>
                <Button
                    mode="contained"
                    onPress={() => onBook(route.name)}
                    style={styles.actionButtonSm}
                    buttonColor={COLORS.secondary}
                >
                    Book Seat
                </Button>
            </Surface>
        ))}
    </ScrollView>
);

const SuggestionButton = ({ label, command, onPress }) => (
    <Button
        mode="outlined"
        onPress={() => onPress(command)}
        style={styles.inlineSuggestion}
        labelStyle={styles.inlineSuggestionText}
        compact
        icon="arrow-right-circle-outline"
    >
        {label}
    </Button>
);

export default function ChatbotScreen() {
    const { user } = useAuth();

    // Internal Ref for accumulating stream
    const activeStreamText = useRef('');

    const [messages, setMessages] = useState([
        {
            id: '1',
            text: `Welcome back, ${user?.name || 'Employee'}! 👋\nI'm your AI assistant. Tell me what you need — I'll handle it instantly.`,
            sender: 'bot',
            timestamp: new Date().toISOString(),
        }
    ]);
    const [inputText, setInputText] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isThinking, setIsThinking] = useState(false);
    const [pendingAction, setPendingAction] = useState(null);
    const [actionBadge, setActionBadge] = useState(null);
    const [menuVisible, setMenuVisible] = useState(false);

    // Form State for Confirmation Tools
    const [formValues, setFormValues] = useState({});
    // Rich item context for Training/Wellness confirmations
    const lastCourseList = useRef([]);
    const lastWellnessList = useRef([]);
    const [confirmItemDetail, setConfirmItemDetail] = useState(null);

    const [suggestions, setSuggestions] = useState(DEFAULT_SUGGESTIONS);

    // Custom Picker State
    const [pickerVisible, setPickerVisible] = useState(false);
    const [pickerType, setPickerType] = useState('date'); // 'date' | 'time'
    const [pickerTarget, setPickerTarget] = useState(null); // the field key (e.g., 'start_date')

    const flatListRef = useRef(null);

    const scrollToBottom = () => {
        setTimeout(() => {
            flatListRef.current?.scrollToEnd({ animated: true });
        }, 100);
    };

    const addMessage = (text, sender, type = 'text', meta = null) => {
        const newMessage = {
            id: Date.now().toString() + Math.random().toString(36).substring(7),
            text,
            sender,
            type,
            meta,
            timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, newMessage]);
        scrollToBottom();
        return newMessage.id;
    };

    const updateStreamingMessage = (messageId, newText) => {
        setMessages(prev => prev.map(msg =>
            msg.id === messageId ? { ...msg, text: newText } : msg
        ));
        // Throttle scrolling slightly during fast streams
        if (newText.length % 50 === 0) scrollToBottom();
    };

    const handleSend = async (overrideText = null) => {
        const textToSend = typeof overrideText === 'string' ? overrideText : inputText.trim();
        if (!textToSend) return;

        setInputText('');
        setMenuVisible(false);
        Keyboard.dismiss();

        addMessage(textToSend, 'user');
        setIsTyping(true);
        setIsThinking(true);
        setActionBadge(null);

        // Prepare an empty bot message to stream into
        const streamMsgId = addMessage('', 'bot');
        activeStreamText.current = '';

        try {
            await sendChatMessageStream(textToSend, user?.user_id || 'emp_001', (event) => {

                if (event.type === 'action_started') {
                    setActionBadge('⚙️ Executing Functions...');
                    scrollToBottom();
                }
                else if (event.type === 'content') {
                    setIsThinking(false);
                    activeStreamText.current += event.text;
                    updateStreamingMessage(streamMsgId, activeStreamText.current);
                }
                else if (event.type === 'confirmation_required') {
                    setIsThinking(false);
                    setIsTyping(false);

                    setConfirmItemDetail(null);

                    const normalizedArgs = { ...(event.arguments || {}) };
                    if ((event.tool_name || '').includes('register_visitor')) {
                        VISITOR_FORM_FIELDS.forEach((field) => {
                            if (normalizedArgs[field] === undefined || normalizedArgs[field] === null) {
                                normalizedArgs[field] = '';
                            }
                        });
                    }

                    // Replace the stream message with a confirmation block
                    setMessages(prev => {
                        const filtered = prev.filter(m => m.id !== streamMsgId);
                        return [...filtered, {
                            id: Date.now().toString(),
                            text: activeStreamText.current.trim() || 'Review Details Before Proceeding',
                            sender: 'bot',
                            type: 'confirmation',
                            meta: { confirm_payload: { ...event, arguments: normalizedArgs } },
                            timestamp: new Date().toISOString()
                        }];
                    });

                    setPendingAction(event.tool_call_id);

                    // Initialize forms
                    const initialForms = {};
                    Object.entries(normalizedArgs).forEach(([k, v]) => {
                        if (k !== 'user_id' && k !== 'host_id') initialForms[k] = v;
                    });
                    setFormValues(initialForms);
                    scrollToBottom();
                }
                else if (event.type === 'error') {
                    setIsThinking(false);
                    activeStreamText.current += `\n\n❌ **Error:** ${event.text}`;
                    updateStreamingMessage(streamMsgId, activeStreamText.current);
                }
                else if (event.type === 'done') {
                    setIsTyping(false);
                    setIsThinking(false);
                    setActionBadge(null);
                }
            });

        } catch (error) {
            console.error(error);
            addMessage('Sorry, I encountered a network error. Please try again.', 'bot', 'error');
            setIsTyping(false);
            setIsThinking(false);
        }
    };

    const handleConfirmAction = async (confirmPayload, isConfirmed, messageId) => {
        setIsTyping(true);
        setIsThinking(true);
        setPendingAction(null);

        // We merged the user's edits from the native TextInputs
        const finalArguments = { ...confirmPayload.arguments, ...formValues };

        addMessage(isConfirmed ? "Confirmed payload." : "Cancelled operation.", 'user');

        try {
            const payload = {
                ...confirmPayload,
                arguments: finalArguments,
                confirmed: isConfirmed
            };

            // Mark old confirmation block as resolved visually
            setMessages(prev => prev.map(msg =>
                msg.id === messageId ? { ...msg, meta: { ...msg.meta, resolved: true, confirmed: isConfirmed } } : msg
            ));

            const response = await confirmChatAction(payload);

            setIsThinking(false);
            addMessage(response.answer, 'bot');

            // Update context suggestions
            if (confirmPayload.tool_name.includes('leave')) setSuggestions(LEAVE_SUGGESTIONS);
            else if (confirmPayload.tool_name.includes('room')) setSuggestions(ROOM_SUGGESTIONS);
            else if (confirmPayload.tool_name.includes('ticket')) setSuggestions(TICKET_SUGGESTIONS);
            else setSuggestions(DEFAULT_SUGGESTIONS);

        } catch (error) {
            console.error(error);
            addMessage('Sorry, the confirmation failed to process.', 'bot', 'error');
        } finally {
            setIsTyping(false);
            setIsThinking(false);
        }
    };

    const updateFormValue = (key, val) => {
        setFormValues(prev => ({ ...prev, [key]: val }));
    };

    const checkFormValidity = (payload) => {
        if (!payload || !payload.arguments) return true;

        // Fields to ignore in validation
        const ignored = ['user_id', 'host_id', 'to_date', 'visitor_email', 'company', 'purpose'];

        // Extract tool name to apply specific logic
        const toolName = payload.tool_name || "";

        // Define required fields per tool if needed
        let requiredFields = Object.keys(payload.arguments);

        if (toolName.includes("register_visitor")) {
            // Explicitly require these for visitors per user request
            requiredFields = ['visitor_name', 'visitor_ic', 'looking_for', 'date', 'time'];
        }

        for (const key of requiredFields) {
            if (ignored.includes(key)) continue;

            const currentVal = formValues[key];
            if (currentVal === undefined || currentVal === null || String(currentVal).trim() === '') {
                return false;
            }
        }
        return true;
    };

    const openPicker = (type, target) => {
        setPickerType(type);
        setPickerTarget(target);
        setPickerVisible(true);
    };

    const selectPickerValue = (value) => {
        if (pickerTarget) {
            updateFormValue(pickerTarget, value);
        }
        setPickerVisible(false);
    };

    const renderPickerModal = () => {
        if (!pickerVisible) return null;

        if (pickerType === 'date') {
            // NEW: Premium Calendar Grid
            const today = new Date();
            const days = [];

            // Generate next 28 days for a full month-like view
            for (let i = 0; i < 28; i++) {
                const d = new Date();
                d.setDate(today.getDate() + i);
                days.push({
                    iso: d.toISOString().split('T')[0],
                    day: d.getDate(),
                    weekday: d.toLocaleDateString(undefined, { weekday: 'short' }),
                    month: d.toLocaleDateString(undefined, { month: 'short' })
                });
            }

            return (
                <Surface style={[styles.pickerModal, SHADOWS.lg, { height: 'auto', maxHeight: 450 }]}>
                    <View style={styles.pickerHeader}>
                        <Title style={styles.pickerTitle}>Select Date</Title>
                        <IconButton icon="close" onPress={() => setPickerVisible(false)} />
                    </View>
                    <View style={styles.calendarGrid}>
                        {days.map((d, i) => (
                            <TouchableOpacity
                                key={i}
                                style={[
                                    styles.calendarDay,
                                    formValues[pickerTarget] === d.iso && styles.calendarDayActive
                                ]}
                                onPress={() => selectPickerValue(d.iso)}
                            >
                                <Text style={[styles.calendarMonth, formValues[pickerTarget] === d.iso && styles.whiteText]}>{d.month}</Text>
                                <Text style={[styles.calendarDate, formValues[pickerTarget] === d.iso && styles.whiteText]}>{d.day}</Text>
                                <Text style={[styles.calendarWeekday, formValues[pickerTarget] === d.iso && styles.whiteText]}>{d.weekday}</Text>
                            </TouchableOpacity>
                        ))}
                    </View>
                </Surface>
            );
        } else {
            // NEW: Premium Clock Grid (4 columns)
            const times = [];
            for (let h = 8; h <= 20; h++) {
                for (let m of ['00', '30']) {
                    const t = `${h.toString().padStart(2, '0')}:${m}`;
                    times.push(t);
                }
            }

            return (
                <Surface style={[styles.pickerModal, SHADOWS.lg, { height: 'auto', maxHeight: 400 }]}>
                    <View style={styles.pickerHeader}>
                        <Title style={styles.pickerTitle}>Select Time</Title>
                        <IconButton icon="close" onPress={() => setPickerVisible(false)} />
                    </View>
                    <ScrollView contentContainerStyle={styles.timeGrid}>
                        {times.map((t, i) => (
                            <TouchableOpacity
                                key={i}
                                style={[
                                    styles.timeSlot,
                                    formValues[pickerTarget] === t && styles.timeSlotActive
                                ]}
                                onPress={() => selectPickerValue(t)}
                            >
                                <Text style={[styles.timeSlotText, formValues[pickerTarget] === t && styles.whiteText]}>{t}</Text>
                            </TouchableOpacity>
                        ))}
                    </ScrollView>
                </Surface>
            );
        }
    };

    // Parse message into text segments and custom UI blocks
    const parseCustomBlocks = (text) => {
        if (!text) return [];

        const segments = [];
        let lastIndex = 0;

        // 1. Regex for JSON blocks
        const jsonRegex = /\`\`\`(room-list|booking-list|ticket-list|shuttle-list|visitor-list|json)\n([\s\S]*?)\n\`\`\`/g;
        // 2. Regex for inline suggestions [SUGGEST:Label|Command]
        const suggestRegex = /\[SUGGEST:([^\]\|]+)\|([^\]]+)\]/g;

        // Merge matches from all regexes
        const matches = [];
        let m;
        while ((m = jsonRegex.exec(text)) !== null) {
            matches.push({ index: m.index, length: m[0].length, type: m[1], data: m[2], full: m[0] });
        }
        while ((m = suggestRegex.exec(text)) !== null) {
            matches.push({ index: m.index, length: m[0].length, type: 'suggestion', label: m[1], command: m[2], full: m[0] });
        }

        // Sort matches by index
        matches.sort((a, b) => a.index - b.index);

        const pushText = (content) => {
            const trimmed = content.trim();
            // Skip empty segments or segments that are just a single dot (common streaming noise)
            if (!trimmed || trimmed === '.' || trimmed === '·') return;
            segments.push({ type: 'text', content: trimmed });
        };

        for (const match of matches) {
            if (match.index > lastIndex) {
                pushText(text.substring(lastIndex, match.index));
            }

            if (match.type === 'suggestion') {
                segments.push({ type: 'suggestion', label: match.label, command: match.command });
            } else {
                try {
                    const jsonData = JSON.parse(match.data);
                    segments.push({ type: match.type, data: jsonData });
                } catch (e) {
                    pushText(match.full);
                }
            }
            lastIndex = match.index + match.length;
        }

        if (lastIndex < text.length) {
            pushText(text.substring(lastIndex));
        }

        // Fallback if everything was filtered but originally there was content
        if (segments.length === 0 && text.trim().length > 0) {
            return [{ type: 'text', content: text.trim() }];
        }

        return segments;
    }

    const renderMessage = ({ item }) => {
        const isBot = item.sender === 'bot';

        if (item.type === 'confirmation') {
            const payload = item.meta?.confirm_payload;
            const isActive = pendingAction === payload?.tool_call_id;
            const isResolved = item.meta?.resolved;
            const wasConfirmed = item.meta?.confirmed;
            const accentColor = COLORS.secondary;
            const iconName = 'clipboard-check';
            const toolLabel = payload?.tool_name?.replace(/_/g, ' ');

            return (
                <View style={styles.botMessageContainer}>
                    <Avatar.Icon size={36} icon="robot" style={styles.botAvatar} color="#fff" />
                    <Surface style={[styles.messageBubble, styles.botBubble, styles.confirmationBubble, isResolved && { opacity: 0.7 }]}>

                        {/* Header */}
                        <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
                            <View style={{ backgroundColor: accentColor + '20', borderRadius: 12, padding: 8, marginRight: 10 }}>
                                <MaterialCommunityIcons name={iconName} size={22} color={accentColor} />
                            </View>
                            <View style={{ flex: 1 }}>
                                <Title style={[styles.confirmationTitle, { marginBottom: 0 }]}>{item.text || 'Confirm Action'}</Title>
                                <Text style={styles.confirmationSub}>{toolLabel}</Text>
                            </View>
                        </View>
                        <View style={styles.formContainer}>
                            {(() => {
                                const args = payload?.arguments || {};
                                const isVisitorForm = (payload?.tool_name || '').includes('register_visitor');
                                const orderedKeys = isVisitorForm
                                    ? VISITOR_FORM_FIELDS
                                    : Object.keys(args).filter((k) => k !== 'user_id' && k !== 'host_id');

                                return orderedKeys.map((key) => {
                                if (key === 'user_id' || key === 'host_id') return null;
                                const titleKey = isVisitorForm
                                    ? VISITOR_LABELS[key] || key.replace(/_/g, ' ').toUpperCase()
                                    : key.replace(/_/g, ' ').toUpperCase();
                                const isDate = key.toLowerCase().includes('date');
                                const isTime = key.toLowerCase().includes('time');
                                const currentValue = formValues[key] !== undefined ? formValues[key] : String(args[key] || '');

                                if (isDate || isTime) {
                                    return (
                                        <View key={key} style={styles.formGroup}>
                                            <Text style={styles.formLabel}>{titleKey}</Text>
                                            <TouchableOpacity
                                                onPress={() => isActive && openPicker(isDate ? 'date' : 'time', key)}
                                                style={[styles.pickerTrigger, !isActive && { opacity: 0.7 }]}
                                                disabled={!isActive}
                                            >
                                                <Text style={[styles.pickerTriggerText, !currentValue && { color: COLORS.textMuted }]}>
                                                    {currentValue || `Select ${titleKey}`}
                                                </Text>
                                                <MaterialCommunityIcons
                                                    name={isDate ? "calendar" : "clock-outline"}
                                                    size={20}
                                                    color={COLORS.primary}
                                                />
                                            </TouchableOpacity>
                                        </View>
                                    );
                                }

                                return (
                                    <View key={key} style={styles.formGroup}>
                                        <Text style={styles.formLabel}>{titleKey}</Text>
                                        <TextInput
                                            mode="outlined"
                                            style={styles.formInput}
                                            value={currentValue}
                                            onChangeText={(val) => updateFormValue(key, val)}
                                            disabled={!isActive}
                                            dense
                                            placeholder={`Enter ${titleKey}`}
                                        />
                                    </View>
                                )
                                });
                            })()}
                        </View>

                        {isActive && (
                            <View style={styles.confirmationActions}>
                                <Button mode="outlined" onPress={() => handleConfirmAction(payload, false, item.id)} textColor="#f44336" style={styles.cancelButton}>
                                    Cancel
                                </Button>
                                <Button
                                    mode="contained"
                                    onPress={() => handleConfirmAction(payload, true, item.id)}
                                    style={[styles.confirmButton, !checkFormValidity(payload) && styles.disabledButton]}
                                    buttonColor={checkFormValidity(payload) ? COLORS.secondary : COLORS.border}
                                    disabled={!checkFormValidity(payload)}
                                >
                                    Confirm
                                </Button>
                            </View>
                        )}
                        {isResolved && (
                            <Text style={[styles.resolvedBadge, { color: wasConfirmed ? '#4caf50' : '#f44336' }]}>
                                {wasConfirmed ? '✅ Proceeded' : '❌ Cancelled'}
                            </Text>
                        )}
                    </Surface>
                </View>
            );
        }

        if (!isBot) {
            return (
                <View style={styles.userMessageContainer}>
                    <Surface style={[styles.messageBubble, styles.userBubble]}>
                        <Text style={styles.userText}>{item.text}</Text>
                    </Surface>
                </View>
            );
        }

        const segments = parseCustomBlocks(item.text);

        return (
            <View style={styles.botMessageContainer}>
                <Avatar.Icon size={36} icon="robot" style={styles.botAvatar} color="#fff" />
                <View style={{ flex: 1 }}>
                    {segments.map((segment, idx) => {
                        if (segment.type === 'text') {
                            return (
                                <Surface key={idx} style={[styles.messageBubble, styles.botBubble, item.type === 'error' && styles.errorBubble, { marginBottom: 8 }]}>
                                    <Markdown style={markdownStyles}>
                                        {segment.content}
                                    </Markdown>
                                </Surface>
                            );
                        }
                        if (segment.type === 'room-list') {
                            return <RoomList key={idx} rooms={segment.data} onBook={(name) => handleSend(`Book ${name}`)} />;
                        }
                        if (segment.type === 'booking-list') {
                            return <BookingList key={idx} bookings={segment.data} />;
                        }
                        if (segment.type === 'ticket-list') {
                            return <TicketList key={idx} tickets={segment.data} />;
                        }
                        if (segment.type === 'shuttle-list') {
                            return <ShuttleList key={idx} routes={segment.data} onBook={(name) => handleSend(`Book shuttle for ${name}`)} />;
                        }
                        if (segment.type === 'visitor-list') {
                            return <VisitorList key={idx} visitors={segment.data} />;
                        }
                        if (segment.type === 'suggestion') {
                            return (
                                <View key={idx} style={styles.suggestionWrapper}>
                                    <SuggestionButton
                                        label={segment.label}
                                        command={segment.command}
                                        onPress={handleSend}
                                    />
                                </View>
                            );
                        }
                        return null;
                    })}

                    {/* Streaming indicator inside the bubble area */}
                    {item.id === messages[messages.length - 1].id && isTyping && (
                        <View style={styles.streamingIndicatorLine}>
                            {isThinking && <ActivityIndicator size={12} color="#667eea" style={{ marginRight: 6 }} />}
                            {actionBadge && <Text style={styles.actionBadge}>{actionBadge}</Text>}
                            {!isThinking && !actionBadge && <View style={styles.typingDot} />}
                        </View>
                    )}
                </View>
            </View>
        );
    };

    return (
        <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined} keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}>
            <FlatList
                ref={flatListRef}
                data={messages}
                keyExtractor={item => item.id}
                renderItem={renderMessage}
                contentContainerStyle={styles.flatListContent}
                onContentSizeChange={scrollToBottom}
                onLayout={scrollToBottom}
            />

            {/* Suggestion Chips */}
            <View>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.suggestionsContainer}>
                    {suggestions.map((suggestion, index) => (
                        <Chip
                            key={index}
                            style={styles.suggestionChip}
                            textStyle={styles.suggestionText}
                            onPress={() => handleSend(suggestion.replace(/^[^\w\s]+ /, '') /* strip icon */)}
                            disabled={isTyping}
                        >
                            {suggestion}
                        </Chip>
                    ))}
                </ScrollView>
            </View>

            {renderPickerModal()}

            {/* Telegram-style Command Menu Layer */}
            {menuVisible && (
                <Surface style={styles.commandMenuContainer} elevation={4}>
                    <View style={styles.commandMenuHeader}>
                        <Text style={styles.commandMenuTitle}>💬 Bot Commands</Text>
                        <IconButton icon="close" size={20} iconColor={COLORS.textMuted} onPress={() => setMenuVisible(false)} />
                    </View>
                    <ScrollView style={{ maxHeight: 250 }} showsVerticalScrollIndicator={false}>
                        {COMMAND_MENU.map((cmd, idx) => (
                            <TouchableOpacity key={idx} style={styles.commandListItem} onPress={() => handleSend(cmd.command)}>
                                <View style={styles.commandListIcon}>
                                    <MaterialCommunityIcons name={cmd.icon} size={22} color={COLORS.primary} />
                                </View>
                                <View>
                                    <Text style={styles.commandListTitle}>{cmd.title}</Text>
                                    <Text style={styles.commandListDesc}>{cmd.desc}</Text>
                                </View>
                            </TouchableOpacity>
                        ))}
                    </ScrollView>
                </Surface>
            )}

            <Surface style={styles.inputContainer} elevation={4}>
                <IconButton
                    icon={menuVisible ? "keyboard-close" : "reorder-horizontal"}
                    iconColor={COLORS.textMuted}
                    size={24}
                    onPress={() => setMenuVisible(!menuVisible)}
                />
                <TextInput
                    style={styles.input}
                    placeholder="Ask me anything..."
                    value={inputText}
                    onChangeText={setInputText}
                    multiline
                    maxLength={500}
                    mode="flat"
                    underlineColor="transparent"
                    activeUnderlineColor="transparent"
                    disabled={isTyping || pendingAction !== null}
                />
                <IconButton
                    icon={isTyping ? "dots-horizontal" : "send"}
                    iconColor="#fff"
                    containerColor={(inputText.trim() || isTyping) ? "#667eea" : "#ccc"}
                    size={24}
                    onPress={handleSend}
                    disabled={(!inputText.trim() && !isTyping) || pendingAction !== null}
                />
            </Surface>
        </KeyboardAvoidingView>
    );
}

const markdownStyles = StyleSheet.create({
    body: { color: COLORS.text, fontSize: 16, lineHeight: 24, fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif' },
    heading1: { fontSize: 22, fontWeight: '800', marginTop: 10, marginBottom: 5, color: COLORS.text },
    heading2: { fontSize: 18, fontWeight: '700', marginTop: 8, marginBottom: 5, color: COLORS.text },
    heading3: { fontSize: 16, fontWeight: '600', marginTop: 6, marginBottom: 5, color: COLORS.text },
    paragraph: { marginBottom: 8 },
    strong: { fontWeight: '700', color: COLORS.text },
    em: { fontStyle: 'italic' },
    link: { color: COLORS.secondary, textDecorationLine: 'underline' },
    list_item: { flexDirection: 'row', marginBottom: 4 },
    bullet_list: { marginLeft: 0 },
    ordered_list: { marginLeft: 0 },
    code_inline: { backgroundColor: COLORS.background, color: COLORS.primary, paddingHorizontal: 4, borderRadius: 4 },
});

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background },
    flatListContent: { padding: SPACING.md, paddingBottom: 20 },
    userMessageContainer: { alignItems: 'flex-end', marginBottom: 12 },
    botMessageContainer: { flexDirection: 'row', alignItems: 'flex-end', marginBottom: 16, maxWidth: '95%' },
    botAvatar: { backgroundColor: COLORS.primary, marginRight: 8 },
    messageBubble: { padding: 12, borderRadius: 20, maxWidth: '100%', ...SHADOWS.sm },
    userBubble: { backgroundColor: COLORS.primary, borderBottomRightRadius: 4 },
    botBubble: { backgroundColor: COLORS.surface, borderBottomLeftRadius: 4, minWidth: 60 },
    errorBubble: { backgroundColor: '#ffebee', borderWidth: 1, borderColor: '#ffcdd2' },
    confirmationBubble: { width: '100%', borderRadius: 20, ...SHADOWS.md },
    userText: { color: COLORS.white, fontSize: 16, lineHeight: 22 },
    botText: { color: COLORS.text, fontSize: 16, lineHeight: 22 },
    errorText: { color: COLORS.error },

    // Status badges inline inside the chat bubble
    streamingIndicatorLine: { flexDirection: 'row', alignItems: 'center', marginTop: 4, minHeight: 20 },
    actionBadge: { backgroundColor: COLORS.background, color: COLORS.primary, fontSize: 12, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 12, overflow: 'hidden', fontWeight: 'bold' },
    typingDot: { width: 8, height: 8, backgroundColor: COLORS.primary, borderRadius: 4, opacity: 0.6 },

    // Suggestion Chips
    suggestionsContainer: { paddingHorizontal: SPACING.md, paddingVertical: 8, paddingBottom: 12 },
    suggestionChip: { backgroundColor: COLORS.surface, marginRight: 8, ...SHADOWS.sm, borderColor: COLORS.border, borderWidth: 1, borderRadius: 20 },
    suggestionText: { color: COLORS.primary, fontSize: 14, fontWeight: '600' },

    // Forms
    confirmationTitle: { fontSize: 18, fontWeight: '800', color: COLORS.text, marginBottom: 4 },
    confirmationSub: { fontSize: 14, color: COLORS.textMuted, marginBottom: 16 },
    formContainer: { backgroundColor: COLORS.background, padding: 12, borderRadius: 12, marginBottom: 12 },
    formGroup: { marginBottom: 12 },
    formLabel: { fontSize: 12, fontWeight: '700', color: COLORS.textMuted, marginBottom: 4 },
    formInput: { backgroundColor: COLORS.surface, fontSize: 14, height: 40 },
    confirmationActions: { flexDirection: 'row', justifyContent: 'flex-end', marginTop: 12, borderTopWidth: 1, borderTopColor: COLORS.border, paddingTop: 12 },
    cancelButton: { marginRight: 8, borderColor: COLORS.error },
    confirmButton: { backgroundColor: COLORS.success },
    disabledButton: { opacity: 0.5 },
    resolvedBadge: { marginTop: 12, fontWeight: 'bold', textAlign: 'right' },

    // Custom Picker Modal
    pickerModal: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: COLORS.surface,
        borderTopLeftRadius: 24,
        borderTopRightRadius: 24,
        padding: 20,
        maxHeight: '60%',
        zIndex: 1000,
    },
    pickerHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 16,
    },
    pickerTitle: { fontSize: 18, fontWeight: '800' },
    pickerItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 14,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.border,
    },
    pickerItemLabel: { fontSize: 16, color: COLORS.text, fontWeight: '600' },
    pickerTrigger: {
        backgroundColor: COLORS.surface,
        borderWidth: 1,
        borderColor: COLORS.border,
        borderRadius: 8,
        height: 44,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: 12,
    },
    pickerTriggerText: { fontSize: 14, color: COLORS.text },

    // Input area
    inputContainer: { flexDirection: 'row', alignItems: 'center', padding: 8, paddingLeft: 0, backgroundColor: COLORS.surface, borderTopLeftRadius: 24, borderTopRightRadius: 24, ...SHADOWS.lg },
    input: { flex: 1, backgroundColor: 'transparent', maxHeight: 100, color: COLORS.text, paddingLeft: 0 },

    // Room Cards
    roomListScroll: { marginBottom: SPACING.md, paddingBottom: 4 },
    roomCard: { width: 220, marginRight: 16, borderRadius: 24, overflow: 'hidden', backgroundColor: COLORS.surface },
    roomImage: { height: 110, width: '100%', borderTopLeftRadius: 24, borderTopRightRadius: 24 },
    roomCardContent: { padding: 12 },
    roomName: { fontSize: 16, fontWeight: '800', color: COLORS.text, marginBottom: 2 },
    roomDetails: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
    roomCapacity: { fontSize: 13, color: COLORS.textMuted, fontWeight: '600' },
    featureChips: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 12 },
    featureBadge: { backgroundColor: COLORS.primary + '08', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8, marginRight: 6, marginBottom: 6 },
    featureText: { fontSize: 10, color: COLORS.primary, fontWeight: '700' },
    roomButton: { borderRadius: 12, marginTop: 4 },
    roomButtonLabel: { fontSize: 12, fontWeight: '800', letterSpacing: 0.5 },

    // Ticket Cards
    ticketListContainer: { marginBottom: SPACING.md },
    ticketCard: {
        backgroundColor: COLORS.surface,
        borderRadius: 20,
        marginBottom: 12,
        flexDirection: 'row',
        overflow: 'hidden',
    },
    ticketAccent: { width: 6 },
    ticketInner: { flex: 1, padding: 14 },
    ticketHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
    ticketId: { fontSize: 11, fontWeight: '800', color: COLORS.textMuted, letterSpacing: 1 },
    statusBadge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8 },
    statusText: { fontSize: 10, fontWeight: '800' },
    ticketSubject: { fontSize: 16, fontWeight: '800', color: COLORS.text, marginBottom: 4 },
    ticketDesc: { fontSize: 13, color: COLORS.textMuted, lineHeight: 18, marginBottom: 10 },
    ticketFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', borderTopWidth: 1, borderTopColor: COLORS.border, paddingTop: 10 },
    priorityGroup: { flexDirection: 'row', alignItems: 'center' },
    priorityText: { fontSize: 11, fontWeight: '700', color: COLORS.primary },
    ticketDate: { fontSize: 11, color: COLORS.textMuted, fontWeight: '600' },

    // Inline Suggestions
    suggestionWrapper: { marginBottom: 8, alignSelf: 'flex-start' },
    inlineSuggestion: { borderColor: COLORS.primary, borderRadius: 24, backgroundColor: COLORS.surface },
    inlineSuggestionText: { fontSize: 13, fontWeight: '700', color: COLORS.primary },

    // Command Menu
    commandMenuContainer: {
        backgroundColor: COLORS.surface,
        borderTopLeftRadius: 24,
        borderTopRightRadius: 24,
        paddingTop: 12,
        paddingBottom: 8,
        marginHorizontal: 8,
        marginBottom: -20, // To sit snugly behind the input container
        zIndex: 10,
        ...SHADOWS.md,
    },
    commandMenuHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 20,
        marginBottom: 4,
    },
    commandMenuTitle: {
        fontSize: 14,
        fontWeight: '800',
        color: COLORS.textMuted,
        textTransform: 'uppercase',
        letterSpacing: 1,
    },
    commandListItem: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 12,
        paddingHorizontal: 20,
        borderBottomWidth: StyleSheet.hairlineWidth,
        borderBottomColor: COLORS.border,
    },
    commandListIcon: {
        width: 36,
        height: 36,
        borderRadius: 18,
        backgroundColor: COLORS.primary + '15',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 12,
    },
    commandListTitle: {
        fontSize: 16,
        fontWeight: '700',
        color: COLORS.primary,
        marginBottom: 2,
    },
    commandListDesc: {
        fontSize: 13,
        color: COLORS.textMuted,
    },

    // New Custom Components Styles
    horizontalScroll: { marginBottom: SPACING.md, paddingBottom: 4 },
    visitorListContainer: { marginBottom: SPACING.md },
    visitorCard: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: COLORS.surface,
        padding: 12,
        borderRadius: 16,
        marginBottom: 8
    },
    cardIconBox: { width: 48, height: 48, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginRight: 12 },
    cardContent: { flex: 1 },
    cardTitle: { fontSize: 16, fontWeight: '800', color: COLORS.text },
    cardSub: { fontSize: 13, color: COLORS.textMuted, marginBottom: 4 },
    cardFooter: { flexDirection: 'row', alignItems: 'center' },
    cardFooterText: { fontSize: 11, color: COLORS.textMuted, fontWeight: '600' },

    shuttleCard: { width: 280, marginRight: 16, borderRadius: 24, padding: 16, backgroundColor: COLORS.surface },
    shuttleHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
    shuttleName: { fontSize: 16, fontWeight: '800' },
    shuttleTime: { fontSize: 12, color: COLORS.textMuted },
    stopsTrack: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20, borderTopWidth: 2, borderTopColor: COLORS.border, paddingTop: 10 },
    stopPoint: { alignItems: 'center', width: 60 },
    stopDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: COLORS.border, position: 'absolute', top: -15 },
    stopLabel: { fontSize: 10, color: COLORS.textMuted, marginTop: 4 },
    actionButtonSm: { borderRadius: 12 },

    // Booking Cards
    bookingListContainer: { marginBottom: SPACING.md },
    bookingCard: {
        backgroundColor: COLORS.surface,
        borderRadius: 24,
        padding: 16,
        marginBottom: 16,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    bookingHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 16,
    },
    bookingRoomName: {
        fontSize: 17,
        fontWeight: '800',
        color: COLORS.text,
        marginBottom: 2,
    },
    bookingIdText: {
        fontSize: 11,
        color: COLORS.textMuted,
        fontWeight: '600',
        letterSpacing: 0.5,
    },
    statusBadgeSmall: {
        backgroundColor: COLORS.success + '15',
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 8,
    },
    statusTextSmall: {
        fontSize: 9,
        fontWeight: '900',
        color: COLORS.success,
    },
    bookingDetailRow: {
        flexDirection: 'row',
        marginBottom: 12,
        backgroundColor: COLORS.background,
        padding: 10,
        borderRadius: 12,
    },
    detailItem: {
        flexDirection: 'row',
        alignItems: 'center',
        marginRight: 20,
    },
    detailText: {
        fontSize: 13,
        color: COLORS.text,
        fontWeight: '600',
    },
    purposeBox: {
        flexDirection: 'row',
        alignItems: 'flex-start',
        marginBottom: 16,
        paddingHorizontal: 4,
    },
    purposeText: {
        fontSize: 13,
        color: COLORS.textMuted,
        lineHeight: 18,
        flex: 1,
    },
    bookingActions: {
        flexDirection: 'row',
        borderTopWidth: 1,
        borderTopColor: COLORS.border,
        paddingTop: 12,
    },
    bookingActionBtn: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 4,
    },
    bookingActionLabel: {
        fontSize: 12,
        fontWeight: '700',
        color: COLORS.text,
        marginLeft: 6,
    },
    actionDivider: {
        width: 1,
        height: '100%',
        backgroundColor: COLORS.border,
    },

    // NEW: Grid Picker Styles
    calendarGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        padding: 12,
    },
    calendarDay: {
        width: '23%',
        backgroundColor: COLORS.background,
        borderRadius: 16,
        padding: 10,
        marginBottom: 10,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    calendarDayActive: {
        backgroundColor: COLORS.primary,
        borderColor: COLORS.primary,
    },
    calendarMonth: {
        fontSize: 10,
        fontWeight: '700',
        color: COLORS.textMuted,
        textTransform: 'uppercase',
    },
    calendarDate: {
        fontSize: 18,
        fontWeight: '800',
        marginVertical: 2,
    },
    calendarWeekday: {
        fontSize: 10,
        color: COLORS.textMuted,
    },
    timeGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        padding: 12,
    },
    timeSlot: {
        width: '23%',
        backgroundColor: COLORS.background,
        borderRadius: 12,
        paddingVertical: 12,
        marginBottom: 10,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    timeSlotActive: {
        backgroundColor: COLORS.primary,
        borderColor: COLORS.primary,
    },
    timeSlotText: {
        fontSize: 13,
        fontWeight: '700',
    },
    whiteText: {
        color: '#FFFFFF',
    },
});
