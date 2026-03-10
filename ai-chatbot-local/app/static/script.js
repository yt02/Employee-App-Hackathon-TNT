/* =====================================================
   Chin Hin Employee Assistant — Frontend Logic
   ===================================================== */

// --- DOM Elements ---
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const sendIcon = document.getElementById('sendIcon');
const loadingIcon = document.getElementById('loadingIcon');
const suggestionsContainer = document.getElementById('suggestionsContainer');
const suggestionsScroll = document.getElementById('suggestionsScroll');
const nudgeBanner = document.getElementById('nudgeBanner');
const nudgeDismiss = document.getElementById('nudgeDismiss');
const nudgeAction = document.getElementById('nudgeAction');
const sidebar = document.getElementById('sidebar');
const menuToggle = document.getElementById('menuToggle');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const clearChatBtn = document.getElementById('clearChatBtn');

// --- Suggestions Data ---
const defaultSuggestions = [
    { text: '📅 Check leave balance', message: "What's my leave balance?" },
    { text: '🏢 Available rooms', message: 'Show available meeting rooms' },
    { text: '📝 Apply for leave', message: 'Apply for 1 day annual leave tomorrow' },
    { text: '🎫 My tickets', message: 'Check my tickets' },
    { text: '📍 Book a room', message: 'Book Conference Room A for tomorrow at 2pm' },
    { text: '🆕 New IT ticket', message: 'Create an IT ticket for network issue' },
];

const contextualSuggestions = {
    leave: [
        { text: '📊 Check balance', message: "What's my leave balance?" },
        { text: '📝 Apply annual leave', message: 'Apply for 2 days annual leave starting next Monday' },
        { text: '🏥 Apply medical leave', message: 'Apply for 1 day medical leave tomorrow' },
        { text: '📋 My leave requests', message: 'Show my leave requests' },
    ],
    room: [
        { text: '🏢 View all rooms', message: 'Show available meeting rooms' },
        { text: '📍 Book Room A', message: 'Book Conference Room A for tomorrow at 2pm' },
        { text: '📍 Book Room B', message: 'Book Meeting Room B for tomorrow at 10am' },
        { text: '📅 My bookings', message: 'Show my room bookings' },
    ],
    ticket: [
        { text: '🆕 Software issue', message: 'Create an IT ticket for software issue' },
        { text: '🆕 Hardware issue', message: 'Create an IT ticket for laptop hardware issue' },
        { text: '🌐 Network issue', message: 'Create an IT ticket for network connectivity issue' },
        { text: '🎫 My tickets', message: 'Check my tickets' },
    ],
    default: defaultSuggestions
};

// --- User Context ---
let currentUserId = "emp_001"; // Default user ID for testing

// --- Markdown Renderer ---
function renderMarkdown(text) {
    if (!text) return '';
    console.log("RAW_API_PAYLOAD:", text);
    let html = text;

    // 0. Extract explicitly fenced complex JSON blocks
    // Many API responses use unpredictable backticks or ui-card prefixes.
    // We will scan the string manually to find valid JSON blocks starting near "status", "title", or "breakdown".
    let searchStart = 0;
    let extractedCards = [];

    // 1. FIRST: Extract explicitly named list blocks like ticket-list and room-list
    // By extracting these first, we prevent the aggressive JSON parser from stealing individual objects
    // like the "status" field inside each ticket.
    html = html
        .replace(/`{3,}room-list\s*([\s\S]*?)\s*`{3,}/g, (match, jsonString) => {
            const parsedCard = renderRoomListCard(jsonString);
            extractedCards.push(parsedCard);
            return `__COMPLEX_CARD_${extractedCards.length - 1}__`;
        })
        .replace(/`{3,}ticket-list\s*([\s\S]*?)\s*`{3,}/g, (match, jsonString) => {
            const parsedCard = renderTicketListCard(jsonString);
            extractedCards.push(parsedCard);
            return `__COMPLEX_CARD_${extractedCards.length - 1}__`;
        });

    while (true) {
        // Look for typical keys of our complex card
        let keywordIdx = html.indexOf('"status":', searchStart);
        if (keywordIdx === -1) keywordIdx = html.indexOf('"title":', searchStart);
        if (keywordIdx === -1) keywordIdx = html.indexOf('"breakdown":', searchStart);

        if (keywordIdx === -1) break; // no more complex cards

        // Walk backwards to find the opening brace of this object
        let openIdx = -1;
        for (let i = keywordIdx; i >= 0; i--) {
            if (html[i] === '{') {
                openIdx = i;
                break;
            }
        }

        if (openIdx === -1) {
            searchStart = keywordIdx + 1;
            continue;
        }

        // Manually parse braces to find the end, ignoring characters in strings
        let openBraces = 0;
        let endIndex = -1;
        let inString = false;
        let escapeNext = false;

        for (let i = openIdx; i < html.length; i++) {
            let char = html[i];

            if (escapeNext) {
                escapeNext = false;
                continue;
            }
            if (char === '\\') {
                escapeNext = true;
                continue;
            }
            if (char === '"') {
                inString = !inString;
            }

            if (!inString) {
                if (char === '{') openBraces++;
                if (char === '}') openBraces--;

                if (openBraces === 0) {
                    endIndex = i;
                    break;
                }
            }
        }

        if (endIndex !== -1) {
            let extractStr = html.substring(openIdx, endIndex + 1);
            let parsedCard = renderComplexCard(extractStr);

            // We replace everything from the opening brace to the closing brace.
            let replaceStart = openIdx;
            // Seek backwards to consume any `\n`, ```ui-card\n, or ``` that immediately preceded this block
            while (replaceStart > 0 && (html[replaceStart - 1] === '`' || html[replaceStart - 1] === '\n' || html[replaceStart - 1] === ' ')) {
                replaceStart--;
            }
            if (replaceStart >= 7 && html.substring(replaceStart - 7, replaceStart) === 'ui-card') replaceStart -= 7;
            if (replaceStart >= 4 && html.substring(replaceStart - 4, replaceStart) === '```\n') replaceStart -= 4;
            if (replaceStart >= 3 && html.substring(replaceStart - 3, replaceStart) === '```') replaceStart -= 3;

            let replaceEnd = endIndex + 1;
            // Seek forwards to consume any trailing ``` or \n
            while (replaceEnd < html.length && (html[replaceEnd] === '`' || html[replaceEnd] === '\n' || html[replaceEnd] === ' ')) {
                replaceEnd++;
            }

            let cardToken = `__COMPLEX_CARD_${extractedCards.length}__`;
            extractedCards.push(parsedCard);

            html = html.substring(0, replaceStart) + cardToken + html.substring(replaceEnd);
            searchStart = replaceStart + cardToken.length;
        } else {
            searchStart = keywordIdx + 1; // move past to avoid infinite loop
        }
    }

    html = html
        // 2. Clean leaked markdown JSON blocks
        .replace(/```json\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```/g, (match, jsonString) => {
            const parsedCard = tryRenderJSON(jsonString);
            extractedCards.push(parsedCard);
            return `__COMPLEX_CARD_${extractedCards.length - 1}__`;
        })
        // 3. Clean up inline JSON arrays like [{"label": "x", "value": "y"}]
        .replace(/(\[\s*\{[\s\S]*?\}\s*\])/g, (match) => {
            const parsedCard = tryRenderJSON(match);
            extractedCards.push(parsedCard);
            return `__COMPLEX_CARD_${extractedCards.length - 1}__`;
        })
        // 4. Aggressively match {"label": "...", "value": "..."} blocks without arrays
        .replace(/(\{(?:\s*"label"\s*:\s*"[^"]+"\s*,\s*"value"\s*:\s*"[^"]+"\s*)\})/g, (match) => {
            const parsedCard = tryRenderJSON(match, true);
            extractedCards.push(parsedCard);
            return `__COMPLEX_CARD_${extractedCards.length - 1}__`;
        })
        // Escape HTML but preserve structure
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Italic
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Inline code
        .replace(/`(.*?)`/g, '<code>$1</code>')
        // Knowledge Base Citations e.g. 【5:0†source】
        .replace(/【\d+:\d+†source】/g, '<span class="citation-badge" title="Knowledge Base Reference" onclick="alert(\'This links to the company handbook PDF source document.\')">📖 source</span>')
        // Parse [SUGGEST: Label | Action Message] syntax into Feature Cards
        .replace(/\[SUGGEST:\s*([^|\]]+?)\s*\|\s*([^\]]+?)\]/g, (match, label, action) => {
            let icon = '✨';
            const lowerLabel = label.toLowerCase();
            if (lowerLabel.includes('leave')) icon = '📅';
            else if (lowerLabel.includes('room') || lowerLabel.includes('book')) icon = '🏢';
            else if (lowerLabel.includes('ticket') || lowerLabel.includes('it')) icon = '🎫';

            return `<button class="inline-action-card" data-action="${action}">
                <span class="feature-icon">${icon}</span>
                <span class="feature-label">${label}</span>
            </button>`;
        })
        .replace(/\[([^\]]+?)\]/gi, (match, p1) => {
            if (p1.includes('SUGGEST:') || match.includes('](') || p1.includes('http')) return match;
            return `<button class="inline-action-card" data-action="${p1}">
                <span class="feature-icon">✨</span>
                <span class="feature-label">${p1}</span>
            </button>`;
        })
        // Horizontal rule
        .replace(/^---$/gm, '<hr>')
        // Unordered list items
        .replace(/^[\s]*[-•]\s+(.+)$/gm, '<li>$1</li>')
        // Ordered list items
        .replace(/^[\s]*\d+\.\s+(.+)$/gm, '<li>$1</li>')
        // Wrap consecutive <li> in <ul>
        .replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>')
        // Line breaks (double newline = paragraph break)
        .replace(/\n\n/g, '</p><p>')
        // Single newline = <br>
        .replace(/\n/g, '<br>');

    // Restore the complex cards that we protected from escaping and formatting
    extractedCards.forEach((cardHtml, index) => {
        html = html.replace(`__COMPLEX_CARD_${index}__`, cardHtml);
    });

    // Format any unescaped table structures nicely if possible
    html = html.replace(/<p><\/p>/g, '');

    return `<p>${html}</p>`;
}

function tryRenderJSON(jsonStr, inline = false) {
    try {
        let data;
        try {
            data = JSON.parse(jsonStr);
        } catch (e) {
            data = (new Function("return " + jsonStr))();
        }

        // Auto-Detect Meeting Room Arrays from stubborn LLMs
        if (Array.isArray(data) && data.length > 0 && typeof data[0] === 'object' && data[0] !== null) {
            if ('room_id' in data[0] || 'capacity' in data[0] || 'facilities' in data[0]) {
                return renderRoomListCard(jsonStr);
            }
        }

        if (Array.isArray(data)) {
            let out = '<div class="data-card-list">';
            data.forEach(item => {
                if (typeof item === 'object' && item !== null) {
                    if (item.label && item.value) {
                        out += `<div class="data-card-item"><strong>${item.label}</strong>: <span>${item.value}</span></div>`;
                    } else {
                        out += `<div class="data-card-item">${Object.entries(item).map(([k, v]) => `<strong>${formatKey(k)}:</strong> <span>${v}</span>`).join('<br>')}</div>`;
                    }
                } else {
                    out += `<div class="data-card-item">${item}</div>`;
                }
            });
            out += '</div>';
            return inline ? out : `\n\n${out}\n\n`;
        } else if (typeof data === 'object' && data !== null) { // Single object
            if (data.label && data.value) {
                return `<strong>${data.label}:</strong> ${data.value}`; // Handle the specific {label: '..', value: '..'} case cleanly
            }
            let out = '<ul class="json-object-list">';
            for (const [key, value] of Object.entries(data)) {
                out += `<li><strong>${formatKey(key)}:</strong> ${Array.isArray(value) ? value.join(', ') : value}</li>`;
            }
            out += '</ul>';
            return inline ? out : `\n\n${out}\n\n`;
        }
    } catch (e) {
        // Not valid JSON or parsing failed, return original string
        return jsonStr;
    }
    return jsonStr;
}

function renderComplexCard(jsonStr) {
    try {
        // Use loose JS evaluation instead of strict JSON.parse to allow LLM quirks (trailing commas, single quotes)
        let data;
        try {
            data = JSON.parse(jsonStr);
        } catch (e) {
            data = (new Function("return " + jsonStr))();
        }

        // Build a beautiful summary card
        let html = `<div class="complex-data-card">`;

        if (data.title) {
            html += `<h3 class="card-title">${data.title}</h3>`;
        }

        if (data.primary_value) {
            html += `<div class="card-primary-metric">
                <span class="metric-value">${data.primary_value}</span>
                ${data.primary_label ? `<span class="metric-label">${data.primary_label}</span>` : ''}
            </div>`;
        }

        if (data.warning) {
            html += `<div class="card-warning">${data.warning}</div>`;
        }

        if (data.breakdown && Array.isArray(data.breakdown)) {
            html += `<div class="card-breakdown-list">`;
            data.breakdown.forEach(item => {
                if (item.label && item.value) {
                    html += `<div class="card-breakdown-item">
                        <span class="breakdown-label">${item.label}</span>
                        <span class="breakdown-value">${item.value}</span>
                    </div>`;
                }
            });
            html += `</div>`;
        }

        html += `</div>`;
        return html;

    } catch (e) {
        console.error("Failed to parse complex card JSON", e);
        return tryRenderJSON(jsonStr); // fallback
    }
}

function renderRoomListCard(jsonStr) {
    try {
        let rooms;
        try {
            rooms = JSON.parse(jsonStr);
        } catch (e) {
            rooms = (new Function("return " + jsonStr))();
        }

        if (!Array.isArray(rooms) || rooms.length === 0) {
            return "<div class='card-warning'>No available rooms found at this time.</div>";
        }

        let html = `<div class="room-grid">`;

        rooms.forEach((room) => {
            const capacity = room.capacity || "?";
            const location = room.location || (room.floor ? `Floor ${room.floor}` : "Unknown Location");

            // Handle different feature array mappings based on current DB entries
            let features = [];
            if (Array.isArray(room.features)) features = room.features;
            else if (Array.isArray(room.facilities)) features = room.facilities;

            html += `
            <div class="room-card">
                <div class="room-card-header">
                    <div class="room-icon">🏢</div>
                    <div class="room-title-group">
                        <h4 class="room-name">${room.name}</h4>
                        <span class="room-capacity">👥 ${capacity} Pax</span>
                    </div>
                </div>
                
                <div class="room-card-body">
                    <div class="room-detail">
                        <span class="detail-icon">📍</span>
                        <span class="detail-text">${location}</span>
                    </div>
                    ${features.length > 0 ? `
                        <div class="room-features">
                            ${features.map(f => `<span class="feature-tag">${f}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
                
                <div class="room-card-footer">
                    <button class="btn-book-room" onclick="handleSuggestionClick('Book ${room.name}')">
                        Reserve Room
                    </button>
                </div>
            </div>`;
        });

        html += `</div>`;
        return html;

    } catch (e) {
        console.error("Failed to parse Room List JSON", e);
        return tryRenderJSON(jsonStr); // fallback
    }
}

function renderTicketListCard(jsonStr) {
    try {
        let tickets;
        try {
            // Strip any accidental markdown formatting if it leaked into the string
            const cleanStr = jsonStr.replace(/```(json|ticket-list)?|```/g, '').trim();
            tickets = JSON.parse(cleanStr);
        } catch (e) {
            console.error("Ticket JSON parse error:", e, "Raw:", jsonStr);
            return `<div class='card-warning'>Unable to load tickets due to an formatting error.</div>`;
        }

        if (!Array.isArray(tickets) || tickets.length === 0) {
            return "<div class='card-warning'>No support tickets found.</div>";
        }

        let html = `<div class="ticket-grid">`;

        tickets.forEach((ticket) => {
            const id = ticket.ticket_id || ticket.id || "TKT-UNKNOWN";
            const subject = ticket.subject || "No Subject";
            const category = ticket.category || "General";
            const priority = (ticket.priority || "Medium").toLowerCase();
            const status = (ticket.status || "Open").toLowerCase();
            const created = ticket.created_at || "Unknown Date";

            // Determine icons and colors based on priority and status
            let priorityIcon = "🟡";
            if (priority === "high" || priority === "urgent") priorityIcon = "🔴";
            else if (priority === "low") priorityIcon = "🟢";

            let statusBadgeClass = "status-badge-open";
            if (status.includes("resolve") || status.includes("close") || status.includes("done")) {
                statusBadgeClass = "status-badge-closed";
            }

            html += `
            <div class="ticket-card">
                <div class="ticket-card-header">
                    <div class="ticket-id-group">
                        <span class="ticket-icon">🎫</span>
                        <span class="ticket-id">${id}</span>
                    </div>
                    <span class="ticket-status ${statusBadgeClass}">${status.toUpperCase()}</span>
                </div>
                
                <div class="ticket-card-body">
                    <h4 class="ticket-subject">${subject}</h4>
                    
                    <div class="ticket-meta-grid">
                        <div class="ticket-meta-item">
                            <span class="meta-icon">📂</span>
                            <span class="meta-value">${category}</span>
                        </div>
                        <div class="ticket-meta-item">
                            <span class="meta-icon">${priorityIcon}</span>
                            <span class="meta-value">${priority.charAt(0).toUpperCase() + priority.slice(1)} Priority</span>
                        </div>
                        <div class="ticket-meta-item">
                            <span class="meta-icon">📅</span>
                            <span class="meta-value">${created.split(' ')[0]}</span>
                        </div>
                    </div>
                </div>
                
                <div class="ticket-card-footer">
                    <button class="btn-view-ticket" onclick="handleSuggestionClick('Check status of ticket ${id}')">
                        Track Updates
                    </button>
                </div>
            </div>`;
        });

        html += `</div>`;
        return html;

    } catch (e) {
        console.error("Failed to parse Ticket List JSON", e);
        return tryRenderJSON(jsonStr); // fallback
    }
}

function formatKey(key) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// --- Add Message ---
function addMessage(content, isUser = false, actionData = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = isUser ? 'A' : '🤖';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';

    // Action badge
    if (actionData && actionData.action_taken) {
        const badge = document.createElement('div');
        badge.className = 'action-badge';
        badge.innerHTML = `<span class="action-icon">⚡</span><span>${formatActionType(actionData.action_type)}</span>`;
        bubbleDiv.appendChild(badge);
    }

    // Message content
    const contentDiv = document.createElement('div');
    contentDiv.innerHTML = renderMarkdown(content);
    bubbleDiv.appendChild(contentDiv);

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);

    scrollToBottom();

    // Update suggestions based on response context
    if (!isUser && actionData) {
        updateSuggestionsFromContext(actionData);
    }
}

// --- Typing Indicator ---
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

// --- Format Action Type ---
function formatActionType(actionType) {
    const names = {
        'check_leave_balance': '📅 Checked Leave Balance',
        'apply_leave': '📝 Leave Applied',
        'list_rooms': '🏢 Listed Rooms',
        'book_room': '📍 Room Booked',
        'check_tickets': '🎫 Tickets Retrieved',
        'create_ticket': '🆕 Ticket Created'
    };
    return names[actionType] || '✓ Action Completed';
}

// --- Update Suggestions ---
function updateSuggestionsFromContext(actionData) {
    let suggestions = contextualSuggestions.default;

    if (actionData.action_type) {
        const type = actionData.action_type;
        if (type.includes('leave')) suggestions = contextualSuggestions.leave;
        else if (type.includes('room')) suggestions = contextualSuggestions.room;
        else if (type.includes('ticket')) suggestions = contextualSuggestions.ticket;
    }

    renderSuggestions(suggestions);
}

function renderSuggestions(suggestions) {
    suggestionsScroll.innerHTML = '';
    suggestions.forEach(s => {
        const chip = document.createElement('button');
        chip.className = 'suggestion-chip';
        chip.textContent = s.text;
        chip.dataset.message = s.message;
        chip.addEventListener('click', () => handleSuggestionClick(s.message));
        suggestionsScroll.appendChild(chip);
    });
}

function handleSuggestionClick(message) {
    messageInput.value = message;
    submitMessage(message);
}

// --- Send Message ---
async function submitMessage(message) {
    if (!message.trim()) return;

    // Add user message
    addMessage(message.trim(), true);
    messageInput.value = '';
    autoResizeTextarea();

    // Disable input
    setInputState(true);

    // Create bot message container immediately
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = '🤖';
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';

    // Add typing indicator bubble
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-dots';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    bubbleDiv.appendChild(typingIndicator);

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();

    try {
        const response = await fetch('/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message.trim(),
                user_id: currentUserId
            })
        });

        if (!response.ok) throw new Error('Network error');

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let fullResponseText = "";
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            let lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (let line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.substring(6).trim();
                    if (!dataStr) continue;

                    try {
                        const event = JSON.parse(dataStr);

                        if (event.type === 'action_started') {
                            // Show a small badge that tools are running without breaking the text flow
                            const badge = document.createElement('div');
                            badge.className = 'action-badge';
                            badge.style.display = 'inline-flex';
                            badge.style.marginTop = '4px';
                            badge.style.marginBottom = '8px';
                            badge.innerHTML = `<span class="action-icon">⚙️</span><span>Executing Functions...</span>`;

                            // Insert before the typing indicator
                            if (typingIndicator.parentNode) {
                                bubbleDiv.insertBefore(badge, typingIndicator);
                            } else {
                                bubbleDiv.appendChild(badge);
                            }
                            scrollToBottom();
                        }
                        else if (event.type === 'content') {
                            // First character of response, remove typing indicator
                            if (typingIndicator.parentNode) {
                                typingIndicator.remove();

                                // Create the container for markdown rendering
                                const markdownContainer = document.createElement('div');
                                markdownContainer.id = 'current-stream-content';
                                bubbleDiv.appendChild(markdownContainer);
                            }

                            fullResponseText += event.text;

                            // Every time a chunk comes in, rerender the whole string buffer via markdown
                            // This gives a very smooth formatting experience.
                            const container = bubbleDiv.querySelector('#current-stream-content');
                            if (container) {
                                container.innerHTML = renderMarkdown(fullResponseText);
                                scrollToBottom();
                            }
                        }
                        else if (event.type === 'confirmation_required') {
                            // If confirmation requires intercept, clear the text bubble, remove typing indicator
                            if (typingIndicator.parentNode) {
                                typingIndicator.remove();
                            }
                            messageDiv.remove(); // We replace the standard div with the interactive confirmation div
                            addConfirmationCard({
                                thread_id: event.thread_id,
                                run_id: event.run_id,
                                tool_call_id: event.tool_call_id,
                                tool_name: event.tool_name,
                                arguments: event.arguments
                            });
                            setInputState(false);
                            return; // Stop processing stream, UI is waiting for user button click
                        }
                        else if (event.type === 'error') {
                            if (typingIndicator.parentNode) typingIndicator.remove();
                            fullResponseText += `\\n\\n❌ **Error:** ${event.text}`;
                            const container = bubbleDiv.querySelector('#current-stream-content') || bubbleDiv;
                            container.innerHTML = renderMarkdown(fullResponseText);
                        }
                        else if (event.type === 'done') {
                            // Normal completion, nothing extra needed. The final text is already rendered.
                        }
                    } catch (e) {
                        console.error('Error parsing SSE json:', e, dataStr);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error:', error);
        if (typingIndicator.parentNode) typingIndicator.remove();
        bubbleDiv.innerHTML = renderMarkdown("Sorry, I encountered an error connecting to the server. Please try again.");
    }

    // Re-enable input
    setInputState(false);
    messageInput.focus();
}

function setInputState(loading) {
    messageInput.disabled = loading;
    sendButton.disabled = loading;
    sendIcon.style.display = loading ? 'none' : 'block';
    loadingIcon.style.display = loading ? 'flex' : 'none';
}

// --- Confirmation Dialog ---
function addConfirmationCard(confirmData) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = '🤖';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble confirmation-bubble';

    let actionFormatted = confirmData.tool_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

    // Build the args form
    let argsHtml = `<div class="confirmation-form" id="confirm-form-${confirmData.tool_call_id}">`;
    for (const [key, value] of Object.entries(confirmData.arguments)) {
        if (key !== 'user_id') {
            argsHtml += `<div class="form-group">
                <label class="form-label">${formatKey(key)}</label>`;

            // Dynamic input types based on parameter names
            if (key.includes('date')) {
                argsHtml += `<input type="date" class="form-input" name="${key}" value="${value}" required>`;
            } else if (key.includes('time')) {
                argsHtml += `<input type="time" class="form-input" name="${key}" value="${value}" required>`;
            } else if (key === 'leave_type') {
                // specific select field mapping
                argsHtml += `<select class="form-select" name="${key}" required>
                    <option value="" disabled ${!value ? 'selected' : ''}>Select Leave Type</option>
                    <option value="annual_leave" ${value === 'annual_leave' ? 'selected' : ''}>Annual Leave</option>
                    <option value="medical_leave" ${value === 'medical_leave' ? 'selected' : ''}>Medical Leave</option>
                    <option value="unpaid_leave" ${value === 'unpaid_leave' ? 'selected' : ''}>Unpaid Leave</option>
                 </select>`;
            } else if (key === 'category') {
                argsHtml += `<select class="form-select" name="${key}" required>
                    <option value="" disabled ${!value ? 'selected' : ''}>Select Category</option>
                    <option value="hardware" ${value === 'hardware' ? 'selected' : ''}>Hardware</option>
                    <option value="software" ${value === 'software' ? 'selected' : ''}>Software</option>
                    <option value="network" ${value === 'network' ? 'selected' : ''}>Network</option>
                    <option value="access" ${value === 'access' ? 'selected' : ''}>Access/Permissions</option>
                    <option value="other" ${value === 'other' ? 'selected' : ''}>Other</option>
                </select>`;
            } else if (key === 'priority') {
                argsHtml += `<select class="form-select" name="${key}" required>
                    <option value="" disabled ${!value ? 'selected' : ''}>Select Priority</option>
                    <option value="low" ${value === 'low' ? 'selected' : ''}>Low</option>
                    <option value="medium" ${value === 'medium' ? 'selected' : ''}>Medium</option>
                    <option value="high" ${value === 'high' ? 'selected' : ''}>High</option>
                    <option value="urgent" ${value === 'urgent' ? 'selected' : ''}>Urgent</option>
                </select>`;
            } else if (key === 'description' || key === 'purpose' || key === 'reason') {
                argsHtml += `<textarea class="form-textarea" name="${key}" required placeholder="Please provide details...">${value}</textarea>`;
            } else {
                argsHtml += `<input type="text" class="form-input" name="${key}" value="${value}" required>`;
            }

            argsHtml += `</div>`;
        }
    }
    argsHtml += '</div>';

    bubbleDiv.innerHTML = `
        <div class="confirmation-card">
            <h3 class="confirmation-title">Review Details Before Proceeding</h3>
            <p class="confirmation-subtitle">You can modify the ${formatKey(confirmData.tool_name)} request details below before confirming.</p>
            ${argsHtml}
            <div class="confirmation-actions">
                <button class="btn-confirm" id="btn-confirm-${confirmData.tool_call_id}">${actionFormatted}</button>
                <button class="btn-cancel" id="btn-cancel-${confirmData.tool_call_id}">Cancel Request</button>
            </div>
        </div>
    `;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();

    // Attach listeners
    const confirmBtn = document.getElementById(`btn-confirm-${confirmData.tool_call_id}`);
    const cancelBtn = document.getElementById(`btn-cancel-${confirmData.tool_call_id}`);
    const form = document.getElementById(`confirm-form-${confirmData.tool_call_id}`);

    confirmBtn.addEventListener('click', () => {
        submitConfirmation(confirmData, true, messageDiv);
    });
    cancelBtn.addEventListener('click', () => {
        submitConfirmation(confirmData, false, messageDiv);
    });

    // Real-time validation
    form.addEventListener('input', () => {
        validateConfirmationForm(confirmData.tool_call_id);
    });

    // Run initial validation
    validateConfirmationForm(confirmData.tool_call_id);
}

function validateConfirmationForm(toolCallId) {
    const form = document.getElementById(`confirm-form-${toolCallId}`);
    const confirmBtn = document.getElementById(`btn-confirm-${toolCallId}`);
    if (!form || !confirmBtn) return;

    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let allValid = true;

    inputs.forEach(input => {
        if (!input.value || input.value.trim() === '') {
            allValid = false;
            input.classList.add('input-invalid');
        } else {
            input.classList.remove('input-invalid');
        }
    });

    confirmBtn.disabled = !allValid;
    if (allValid) {
        confirmBtn.classList.add('btn-pulse');
    } else {
        confirmBtn.classList.remove('btn-pulse');
    }
}

async function submitConfirmation(confirmData, confirmed, messageDiv) {
    // Disable the buttons
    const buttons = messageDiv.querySelectorAll('button');
    buttons.forEach(b => b.disabled = true);

    // Scrape updated form values if confirmed
    if (confirmed) {
        const formContainer = document.getElementById(`confirm-form-${confirmData.tool_call_id}`);
        if (formContainer) {
            const inputs = formContainer.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                confirmData.arguments[input.name] = input.value;
                input.disabled = true; // freeze the inputs
            });
        }
    }

    setInputState(true);
    showTypingIndicator();

    try {
        const response = await fetch('/chat/confirm', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                thread_id: confirmData.thread_id,
                run_id: confirmData.run_id,
                tool_call_id: confirmData.tool_call_id,
                tool_name: confirmData.tool_name,
                arguments: confirmData.arguments,
                confirmed: confirmed
            })
        });

        if (!response.ok) throw new Error('Network error');
        const data = await response.json();

        hideTypingIndicator();

        // Add completion badge to original confirmation card to signify it's done
        const confCard = messageDiv.querySelector('.confirmation-card');
        if (confCard) {
            confCard.style.opacity = '0.75';
            const statusDiv = document.createElement('div');
            statusDiv.className = confirmed ? 'status-badge-success' : 'status-badge-cancelled';
            statusDiv.innerText = confirmed ? '✅ Executed' : '❌ Cancelled';
            statusDiv.style.marginTop = '12px';
            confCard.appendChild(statusDiv);
        }

        addMessage(data.answer, false, data);

    } catch (error) {
        console.error('Error:', error);
        hideTypingIndicator();
        addMessage('Sorry, I encountered an error while confirming the action. Please try again or refresh the page.', false);
    }

    setInputState(false);
    messageInput.focus();
}

// --- Scroll ---
function scrollToBottom() {
    requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}

// --- Auto-Resize Textarea ---
function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

// --- Event Listeners ---

// Form submit
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    submitMessage(messageInput.value);
});

// Inline Action Buttons (Delegate from chatMessages)
chatMessages.addEventListener('click', (e) => {
    const btn = e.target.closest('.inline-action-btn, .inline-action-card');
    if (btn) {
        const action = btn.dataset.action;
        messageInput.value = action;
        submitMessage(action);
    }
});

// Textarea: Enter to send, Shift+Enter for newline
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitMessage(messageInput.value);
    }
});

messageInput.addEventListener('input', autoResizeTextarea);

// Suggestion chips (initial ones from HTML)
document.querySelectorAll('.suggestion-chip[data-message]').forEach(chip => {
    chip.addEventListener('click', () => handleSuggestionClick(chip.dataset.message));
});

// Feature cards in welcome message
document.querySelectorAll('.feature-card[data-action]').forEach(card => {
    card.addEventListener('click', () => {
        const action = card.dataset.action;
        messageInput.value = action;
        submitMessage(action);
    });
});

// Sidebar nav items
document.querySelectorAll('.nav-item[data-action]').forEach(item => {
    item.addEventListener('click', () => {
        const action = item.dataset.action;
        messageInput.value = action;
        // Close sidebar on mobile
        closeSidebar();
        submitMessage(action);
    });
});

// Nudge banner
nudgeDismiss.addEventListener('click', () => {
    nudgeBanner.classList.add('hidden');
});

nudgeAction.addEventListener('click', () => {
    submitMessage("Check my pending leave requests");
    nudgeBanner.classList.add('hidden');
});

// Mobile sidebar toggle
menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    sidebarOverlay.classList.toggle('active');
});

sidebarOverlay.addEventListener('click', closeSidebar);

function closeSidebar() {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('active');
}

// Clear chat
clearChatBtn.addEventListener('click', () => {
    // Keep only the welcome message
    const welcome = document.getElementById('welcomeMessage');
    chatMessages.innerHTML = '';
    if (welcome) chatMessages.appendChild(welcome);
    // Reset suggestions
    renderSuggestions(defaultSuggestions);
    // Show nudge banner again
    nudgeBanner.classList.remove('hidden');
});

// --- User Data Loading ---
async function loadUserData(userId) {
    try {
        const response = await fetch(`/api/user/${userId}`);
        if (!response.ok) throw new Error('Failed to fetch user data');

        const user = await response.json();

        // Update DOM elements
        const userNameElements = document.querySelectorAll('.user-name');
        userNameElements.forEach(el => el.textContent = `${user.name} (@${user.username})`);

        const userRoleElements = document.querySelectorAll('.user-role');
        const formattedRole = user.role.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        userRoleElements.forEach(el => el.textContent = formattedRole);

        const userAvatarElements = document.querySelectorAll('.user-avatar');
        if (user.name) {
            userAvatarElements.forEach(el => el.textContent = user.name.charAt(0).toUpperCase());
        }

        const welcomeTitle = document.querySelector('.welcome-title');
        if (welcomeTitle && user.name) {
            const firstName = user.name.split(' ')[0];
            welcomeTitle.textContent = `Welcome back, ${firstName} (@${user.username})! 👋`;
        }
    } catch (error) {
        console.error('Error loading user data:', error);
    }
}

// --- Init ---
loadUserData(currentUserId);
messageInput.focus();
