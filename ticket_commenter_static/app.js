// Global state
let tickets = [];
let filteredTickets = [];
let currentTicketIndex = 0;
let saveTimeout = null;
let isSaving = false;

// API Configuration
const API_BASE = '';

// DOM Elements
const recurrentFilter = document.getElementById('recurrentFilter');
const agentNeededFilter = document.getElementById('agentNeededFilter');
const ticketIdSearch = document.getElementById('ticketIdSearch');
const resetFiltersBtn = document.getElementById('resetFiltersBtn');
const ticketCounter = document.getElementById('ticketCounter');
const subject = document.getElementById('subject');
const headerSummary = document.getElementById('headerSummary');
const ticketUrl = document.getElementById('ticketUrl');
const conversation = document.getElementById('conversation');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const ticketNumberInput = document.getElementById('ticketNumberInput');
const goToTicketBtn = document.getElementById('goToTicketBtn');
const commentsTextarea = document.getElementById('commentsTextarea');
const saveStatus = document.getElementById('saveStatus');

// Dropdown filters configuration
const dropdownFilters = {
    mailbox: {
        fieldName: 'mailbox_name',
        toggleBtn: document.getElementById('mailboxDropdownToggle'),
        dropdown: document.getElementById('mailboxDropdown'),
        checkboxesContainer: document.getElementById('mailboxCheckboxes'),
        selectedText: document.getElementById('mailboxSelectedText'),
        selectAllBtn: document.getElementById('mailboxSelectAll'),
        deselectAllBtn: document.getElementById('mailboxDeselectAll'),
        selected: []
    },
    tip: {
        fieldName: 'tip',
        toggleBtn: document.getElementById('tipDropdownToggle'),
        dropdown: document.getElementById('tipDropdown'),
        checkboxesContainer: document.getElementById('tipCheckboxes'),
        selectedText: document.getElementById('tipSelectedText'),
        selectAllBtn: document.getElementById('tipSelectAll'),
        deselectAllBtn: document.getElementById('tipDeselectAll'),
        selected: []
    },
    area: {
        fieldName: 'area',
        toggleBtn: document.getElementById('areaDropdownToggle'),
        dropdown: document.getElementById('areaDropdown'),
        checkboxesContainer: document.getElementById('areaCheckboxes'),
        selectedText: document.getElementById('areaSelectedText'),
        selectAllBtn: document.getElementById('areaSelectAll'),
        deselectAllBtn: document.getElementById('areaDeselectAll'),
        selected: []
    },
    sentiment: {
        fieldName: 'sentiment',
        toggleBtn: document.getElementById('sentimentDropdownToggle'),
        dropdown: document.getElementById('sentimentDropdown'),
        checkboxesContainer: document.getElementById('sentimentCheckboxes'),
        selectedText: document.getElementById('sentimentSelectedText'),
        selectAllBtn: document.getElementById('sentimentSelectAll'),
        deselectAllBtn: document.getElementById('sentimentDeselectAll'),
        selected: []
    },
    urgency: {
        fieldName: 'urgency',
        toggleBtn: document.getElementById('urgencyDropdownToggle'),
        dropdown: document.getElementById('urgencyDropdown'),
        checkboxesContainer: document.getElementById('urgencyCheckboxes'),
        selectedText: document.getElementById('urgencySelectedText'),
        selectAllBtn: document.getElementById('urgencySelectAll'),
        deselectAllBtn: document.getElementById('urgencyDeselectAll'),
        selected: []
    },
    platform: {
        fieldName: 'platform',
        toggleBtn: document.getElementById('platformDropdownToggle'),
        dropdown: document.getElementById('platformDropdown'),
        checkboxesContainer: document.getElementById('platformCheckboxes'),
        selectedText: document.getElementById('platformSelectedText'),
        selectAllBtn: document.getElementById('platformSelectAll'),
        deselectAllBtn: document.getElementById('platformDeselectAll'),
        selected: []
    },
    integration: {
        fieldName: 'integration',
        toggleBtn: document.getElementById('integrationDropdownToggle'),
        dropdown: document.getElementById('integrationDropdown'),
        checkboxesContainer: document.getElementById('integrationCheckboxes'),
        selectedText: document.getElementById('integrationSelectedText'),
        selectAllBtn: document.getElementById('integrationSelectAll'),
        deselectAllBtn: document.getElementById('integrationDeselectAll'),
        selected: []
    }
};

// Event Listeners - Setup dropdown filters
Object.keys(dropdownFilters).forEach(filterKey => {
    const filter = dropdownFilters[filterKey];
    filter.toggleBtn.addEventListener('click', (e) => toggleDropdown(e, filterKey));
    filter.selectAllBtn.addEventListener('click', () => selectAll(filterKey));
    filter.deselectAllBtn.addEventListener('click', () => deselectAll(filterKey));
});

recurrentFilter.addEventListener('change', applyFilters);
agentNeededFilter.addEventListener('change', applyFilters);
ticketIdSearch.addEventListener('input', applyFilters);
resetFiltersBtn.addEventListener('click', resetFilters);
prevBtn.addEventListener('click', showPreviousTicket);
nextBtn.addEventListener('click', showNextTicket);
goToTicketBtn.addEventListener('click', jumpToTicket);
ticketNumberInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        jumpToTicket();
    }
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    Object.keys(dropdownFilters).forEach(filterKey => {
        const filter = dropdownFilters[filterKey];
        if (!filter.toggleBtn.contains(e.target) && !filter.dropdown.contains(e.target)) {
            filter.dropdown.classList.remove('show');
        }
    });
});

// Comments auto-save with debounce
commentsTextarea.addEventListener('input', () => {
    clearTimeout(saveTimeout);

    saveTimeout = setTimeout(() => {
        if (!isSaving) {
            saveComment();
        }
    }, 500);
});

// Keyboard navigation (Ctrl+Arrow keys)
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'ArrowLeft') {
        e.preventDefault();
        showPreviousTicket();
    } else if (e.ctrlKey && e.key === 'ArrowRight') {
        e.preventDefault();
        showNextTicket();
    }
});

// Auto-load tickets on page load
window.addEventListener('load', () => {
    loadTickets();
});

async function loadTickets() {
    try {
        const response = await fetch(`${API_BASE}/api/tickets`);
        if (!response.ok) {
            throw new Error('Failed to load tickets');
        }

        tickets = await response.json();
        console.log(`Loaded ${tickets.length} tickets`);
        populateFilters();

        // Restore saved state
        restoreFilterState();

        applyFilters();

        // Restore saved ticket index
        const savedIndex = localStorage.getItem('currentTicketIndex');
        if (savedIndex && filteredTickets.length > 0) {
            const index = parseInt(savedIndex);
            if (index >= 0 && index < filteredTickets.length) {
                currentTicketIndex = index;
                displayTicket(currentTicketIndex);
                updateNavigation();
            }
        }
    } catch (error) {
        console.error('Error loading tickets:', error);
        conversation.innerHTML = '<p class="placeholder">Eroare la încărcarea ticketelor</p>';
    }
}

async function saveComment() {
    if (filteredTickets.length === 0 || isSaving) return;

    isSaving = true;
    const ticketIndex = tickets.findIndex(t => t === filteredTickets[currentTicketIndex]);
    const comment = commentsTextarea.value;

    try {
        const response = await fetch(`${API_BASE}/api/tickets/${ticketIndex}/comment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ comment })
        });

        if (!response.ok) {
            throw new Error('Failed to save comment');
        }

        const result = await response.json();
        tickets[ticketIndex].Comments = result.comment;

        saveStatus.textContent = 'Saved ✓';
        saveStatus.className = 'save-status saved';

        setTimeout(() => {
            saveStatus.textContent = '';
            saveStatus.className = 'save-status';
        }, 1500);
    } catch (error) {
        console.error('Error saving comment:', error);
        saveStatus.textContent = 'Error!';
        saveStatus.className = 'save-status error';
    } finally {
        isSaving = false;
    }
}

function toggleDropdown(e, filterKey) {
    e.stopPropagation();
    dropdownFilters[filterKey].dropdown.classList.toggle('show');
}

function selectAll(filterKey) {
    const filter = dropdownFilters[filterKey];
    const checkboxes = filter.checkboxesContainer.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
    updateSelectedValues(filterKey);
}

function deselectAll(filterKey) {
    const filter = dropdownFilters[filterKey];
    const checkboxes = filter.checkboxesContainer.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    updateSelectedValues(filterKey);
}

function updateSelectedValues(filterKey) {
    const filter = dropdownFilters[filterKey];
    const checkboxes = filter.checkboxesContainer.querySelectorAll('input[type="checkbox"]');
    filter.selected = Array.from(checkboxes)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);

    // Update button text
    if (filter.selected.length === 0) {
        filter.selectedText.textContent = 'None selected';
    } else if (filter.selected.length === checkboxes.length) {
        filter.selectedText.textContent = 'All';
    } else if (filter.selected.length === 1) {
        filter.selectedText.textContent = filter.selected[0];
    } else {
        filter.selectedText.textContent = `${filter.selected.length} selected`;
    }

    applyFilters();
}

function populateFilters() {
    Object.keys(dropdownFilters).forEach(filterKey => {
        populateDropdownCheckboxes(filterKey);
    });
}

function populateDropdownCheckboxes(filterKey) {
    const filter = dropdownFilters[filterKey];
    const values = new Set();

    tickets.forEach(ticket => {
        const value = ticket[filter.fieldName];
        if (value && value !== '-' && value.trim() !== '') {
            values.add(value);
        }
    });

    filter.checkboxesContainer.innerHTML = '';

    Array.from(values).sort().forEach((value, index) => {
        const checkboxItem = document.createElement('div');
        checkboxItem.className = 'checkbox-item';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `${filterKey}-${index}`;
        checkbox.value = value;
        checkbox.checked = true; // Default: all selected
        checkbox.addEventListener('change', () => updateSelectedValues(filterKey));

        const label = document.createElement('label');
        label.htmlFor = `${filterKey}-${index}`;
        label.textContent = value;

        checkboxItem.appendChild(checkbox);
        checkboxItem.appendChild(label);
        filter.checkboxesContainer.appendChild(checkboxItem);
    });

    // Initialize selected values
    updateSelectedValues(filterKey);
}

function applyFilters() {
    saveFilterState();

    const ticketIdQuery = ticketIdSearch.value.trim().toLowerCase();

    filteredTickets = tickets.filter(ticket => {
        // Ticket ID search
        if (ticketIdQuery && !ticket.ticket_id.toString().toLowerCase().includes(ticketIdQuery)) {
            return false;
        }

        // Apply all dropdown filters (OR logic within each filter)
        for (const filterKey in dropdownFilters) {
            const filter = dropdownFilters[filterKey];
            const ticketValue = ticket[filter.fieldName];
            const isEmpty = !ticketValue || ticketValue === '-' || ticketValue.trim() === '';

            // If there are selections and ticket value is not empty and not in selections -> exclude
            if (filter.selected.length > 0 && !isEmpty && !filter.selected.includes(ticketValue)) {
                return false;
            }
        }

        // Recurrent filter
        if (recurrentFilter.value !== 'all') {
            const isRecurrent = ticket.is_recurrent?.toLowerCase() === 'true';
            const filterValue = recurrentFilter.value === 'true';
            if (isRecurrent !== filterValue) {
                return false;
            }
        }

        // Agent needed filter
        if (agentNeededFilter.value !== 'all') {
            const agentNeeded = ticket.agent_intervention_needed?.toLowerCase() === 'true';
            const filterValue = agentNeededFilter.value === 'true';
            if (agentNeeded !== filterValue) {
                return false;
            }
        }

        return true;
    });

    currentTicketIndex = 0;
    if (filteredTickets.length > 0) {
        displayTicket(currentTicketIndex);
    } else {
        conversation.innerHTML = '<p class="placeholder">Nu există tickete care să corespundă filtrelor selectate</p>';
        ticketCounter.textContent = 'No tickets found';
    }
    updateNavigation();
}

function saveFilterState() {
    const filterState = {
        dropdownFilters: {},
        recurrent: recurrentFilter.value,
        agentNeeded: agentNeededFilter.value,
        ticketId: ticketIdSearch.value
    };

    // Save selected values for all dropdown filters
    Object.keys(dropdownFilters).forEach(filterKey => {
        filterState.dropdownFilters[filterKey] = dropdownFilters[filterKey].selected;
    });

    localStorage.setItem('filterState', JSON.stringify(filterState));
}

function restoreFilterState() {
    const savedState = localStorage.getItem('filterState');
    if (savedState) {
        try {
            const filterState = JSON.parse(savedState);

            // Restore simple filters
            recurrentFilter.value = filterState.recurrent || 'all';
            agentNeededFilter.value = filterState.agentNeeded || 'all';
            ticketIdSearch.value = filterState.ticketId || '';

            // Restore dropdown filters
            if (filterState.dropdownFilters) {
                Object.keys(dropdownFilters).forEach(filterKey => {
                    const savedSelected = filterState.dropdownFilters[filterKey];
                    if (savedSelected && Array.isArray(savedSelected)) {
                        const filter = dropdownFilters[filterKey];
                        const checkboxes = filter.checkboxesContainer.querySelectorAll('input[type="checkbox"]');
                        checkboxes.forEach(checkbox => {
                            checkbox.checked = savedSelected.includes(checkbox.value);
                        });
                        updateSelectedValues(filterKey);
                    }
                });
            }
        } catch (e) {
            console.error('Error restoring filter state:', e);
        }
    }
}

function resetFilters() {
    // Reset all dropdown filters to all checked
    Object.keys(dropdownFilters).forEach(filterKey => {
        const filter = dropdownFilters[filterKey];
        const checkboxes = filter.checkboxesContainer.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
        updateSelectedValues(filterKey);
    });

    recurrentFilter.value = 'all';
    agentNeededFilter.value = 'all';
    ticketIdSearch.value = '';
    applyFilters();
}

function displayTicket(index) {
    if (!filteredTickets || filteredTickets.length === 0) return;

    const ticket = filteredTickets[index];

    ticketCounter.textContent = `Ticket ${index + 1} of ${filteredTickets.length}`;
    subject.textContent = ticket.subject || '-';
    headerSummary.textContent = ticket.summary || '-';
    ticketUrl.href = ticket.ticket_url || '#';

    const conversationText = ticket.gdrp_free_conversation || ticket.formatted_conversation || '';
    conversation.innerHTML = parseConversation(conversationText);
    conversation.scrollTop = 0;

    // Load comment
    commentsTextarea.value = ticket.Comments || '';

    // Update metadata
    updateMetadata('tip', ticket.tip || '-');
    updateMetadata('area', ticket.area || '-');
    updateMetadata('sentiment', ticket.sentiment || '-');
    updateMetadata('apreciere', ticket.apreciere_parere_support || '-');
    updateMetadata('urgency', ticket.urgency || '-');
    updateMetadata('is_recurrent', ticket.is_recurrent || '-');
    updateMetadata('agent_intervention_needed', ticket.agent_intervention_needed || '-');
    updateMetadata('user_goal', ticket.user_goal || '-');
    updateMetadata('pain_point', ticket.pain_point || '-');
    updateMetadata('problem_type', ticket.problem_type || '-');
    updateMetadata('affects_business_flow', ticket.affects_business_flow || '-');
    updateMetadata('platform', ticket.platform || '-');
    updateMetadata('integration', ticket.integration || '-');
    updateMetadata('mentioned_features', ticket.mentioned_features || '-');
    updateMetadata('specific_error_messages', ticket.specific_error_messages || '-');

    // Save current index to localStorage
    localStorage.setItem('currentTicketIndex', index);
}

function parseConversation(text) {
    if (!text || text.trim() === '') {
        return '<p class="placeholder">Nu există conversație disponibilă</p>';
    }

    const regex = /\[(CLIENT|AGENT)\s*-\s*([^\]]+)\]/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
        if (match.index > lastIndex) {
            const previousContent = text.substring(lastIndex, match.index).trim();
            if (previousContent && parts.length > 0) {
                parts[parts.length - 1].content += previousContent;
            }
        }

        parts.push({
            type: match[1],
            date: match[2],
            content: ''
        });

        lastIndex = match.index + match[0].length;
    }

    if (lastIndex < text.length && parts.length > 0) {
        parts[parts.length - 1].content = text.substring(lastIndex).trim();
    }

    if (parts.length === 0) {
        return `<div class="message"><div class="message-content">${escapeHtml(text)}</div></div>`;
    }

    return parts.map(part => {
        const typeClass = part.type.toLowerCase();
        return `
            <div class="message">
                <div class="message-header ${typeClass}">
                    <span>${part.type}</span>
                    <span class="message-date">${escapeHtml(part.date)}</span>
                </div>
                <div class="message-content">${escapeHtml(part.content)}</div>
            </div>
        `;
    }).join('');
}

function updateMetadata(field, value) {
    const element = document.getElementById(field);
    if (!element) return;

    element.textContent = value;
    element.className = 'value';

    const lowerValue = value.toLowerCase();
    if (lowerValue === 'negativ' || lowerValue === 'blocker') {
        element.classList.add(lowerValue);
    } else if (lowerValue === 'pozitiv') {
        element.classList.add('pozitiv');
    } else if (lowerValue === 'neutru') {
        element.classList.add('neutru');
    } else if (lowerValue === 'mediu') {
        element.classList.add('mediu');
    } else if (lowerValue === 'scazut') {
        element.classList.add('scazut');
    } else if (lowerValue === 'true') {
        element.classList.add('true');
    } else if (lowerValue === 'false') {
        element.classList.add('false');
    }
}

function showPreviousTicket() {
    if (currentTicketIndex > 0) {
        currentTicketIndex--;
        displayTicket(currentTicketIndex);
        updateNavigation();
    }
}

function showNextTicket() {
    if (currentTicketIndex < filteredTickets.length - 1) {
        currentTicketIndex++;
        displayTicket(currentTicketIndex);
        updateNavigation();
    }
}

function jumpToTicket() {
    const ticketNumber = parseInt(ticketNumberInput.value);

    if (isNaN(ticketNumber) || ticketNumber < 1) {
        alert('Please enter a valid ticket number (1 or greater)');
        return;
    }

    if (ticketNumber > filteredTickets.length) {
        alert(`Ticket number ${ticketNumber} is out of range. Max is ${filteredTickets.length}`);
        return;
    }

    currentTicketIndex = ticketNumber - 1;
    displayTicket(currentTicketIndex);
    updateNavigation();
    ticketNumberInput.value = '';
}

function updateNavigation() {
    prevBtn.disabled = currentTicketIndex === 0;
    nextBtn.disabled = currentTicketIndex === filteredTickets.length - 1 || filteredTickets.length === 0;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

updateNavigation();
