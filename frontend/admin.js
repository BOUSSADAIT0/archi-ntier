// Configuration
const API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:18000' : 'http://' + window.location.hostname + ':18000';

// Configuration fetch par défaut
const defaultFetchOptions = {
    mode: 'cors',
    credentials: 'same-origin',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
};

// Fonction fetch avec gestion des erreurs
async function fetchApi(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...defaultFetchOptions,
            ...options,
        });
        
        if (!response.ok) {
            const errorData = await response.text();
            console.error('API Error:', {
                status: response.status,
                statusText: response.statusText,
                data: errorData
            });
            throw new Error(`HTTP error! status: ${response.status} - ${errorData}`);
        }
        
        return response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Fonctions d'affichage
function showEventsList() {
    document.getElementById('eventsList').style.display = 'block';
    document.getElementById('addEventForm').style.display = 'none';
    loadEvents();
}

function showAddEventForm() {
    document.getElementById('eventsList').style.display = 'none';
    document.getElementById('addEventForm').style.display = 'block';
}

// Chargement des événements
async function loadEvents() {
    const container = document.getElementById('eventsTableBody');
    container.innerHTML = '<tr><td colspan="5" class="text-center"><div class="loading"></div></td></tr>';

    try {
        const events = await fetchApi('/events/');
        
        container.innerHTML = events.map(event => `
            <tr>
                <td>${event.name}</td>
                <td>${event.venue}</td>
                <td>${event.categories.join(', ')}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="openAddSessionModal('${event.id}')">
                        Ajouter une session
                    </button>
                </td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editEvent('${event.id}')">
                        Modifier
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteEvent('${event.id}')">
                        Supprimer
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        container.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Erreur lors du chargement des événements</td></tr>';
    }
}

// Gestion des événements
async function createEvent(event) {
    try {
        await fetchApi('/events/', {
            method: 'POST',
            body: JSON.stringify(event)
        });
        showEventsList();
    } catch (error) {
        alert('Erreur lors de la création de l\'événement');
    }
}

async function deleteEvent(eventId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet événement ?')) {
        return;
    }

    try {
        await fetchApi(`/events/${eventId}`, {
            method: 'DELETE'
        });
        loadEvents();
    } catch (error) {
        alert('Erreur lors de la suppression de l\'événement');
    }
}

// Gestion des sessions
function openAddSessionModal(eventId) {
    document.getElementById('sessionEventId').value = eventId;
    new bootstrap.Modal(document.getElementById('addSessionModal')).show();
}

async function submitSession() {
    const eventId = document.getElementById('sessionEventId').value;
    const session = {
        start_time: document.getElementById('sessionStartTime').value,
        end_time: document.getElementById('sessionEndTime').value,
        capacity: parseInt(document.getElementById('sessionCapacity').value),
        base_price: parseFloat(document.getElementById('sessionBasePrice').value)
    };

    try {
        await fetchApi(`/events/${eventId}/sessions`, {
            method: 'POST',
            body: JSON.stringify(session)
        });
        bootstrap.Modal.getInstance(document.getElementById('addSessionModal')).hide();
        loadEvents();
    } catch (error) {
        alert('Erreur lors de la création de la session');
    }
}

// Gestionnaires d'événements
document.addEventListener('DOMContentLoaded', () => {
    showEventsList();

    // Gestionnaire pour le formulaire d'ajout d'événement
    document.getElementById('eventForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const event = {
            name: document.getElementById('eventName').value,
            description: document.getElementById('eventDescription').value,
            venue: document.getElementById('eventVenue').value,
            categories: document.getElementById('eventCategories').value.split(',').map(c => c.trim())
        };

        await createEvent(event);
    });
}); 