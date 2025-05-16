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
        console.log(`Fetching ${API_BASE_URL}${endpoint}`);
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

let currentUserId = localStorage.getItem('userId') || generateUserId();
let currentSessionId = null;

// Générer un ID utilisateur unique
function generateUserId() {
    const userId = 'user-' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('userId', userId);
    return userId;
}

// Fonctions d'affichage
function showEvents() {
    document.getElementById('eventsList').style.display = 'block';
    document.getElementById('eventDetails').style.display = 'none';
    document.getElementById('myBookings').style.display = 'none';
    loadEvents();
}

function showEventDetails(eventId) {
    document.getElementById('eventsList').style.display = 'none';
    document.getElementById('eventDetails').style.display = 'block';
    document.getElementById('myBookings').style.display = 'none';
    loadEventDetails(eventId);
}

function showMyBookings() {
    document.getElementById('eventsList').style.display = 'none';
    document.getElementById('eventDetails').style.display = 'none';
    document.getElementById('myBookings').style.display = 'block';
    loadMyBookings();
}

// Chargement des données
async function loadEvents() {
    const container = document.getElementById('eventsContainer');
    container.innerHTML = '<div class="loading"></div>';

    try {
        const events = await fetchApi('/events/');
        
        container.innerHTML = events.map(event => `
            <div class="col-md-4 mb-4">
                <div class="card event-card" onclick="showEventDetails('${event.id}')">
                    <img src="https://picsum.photos/400/200?random=${event.id}" class="card-img-top event-image" alt="${event.name}">
                    <div class="card-body">
                        <h5 class="card-title">${event.name}</h5>
                        <p class="card-text">${event.description}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">${event.venue}</small>
                            <div class="badge bg-primary">${event.categories.join(', ')}</div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<div class="alert alert-danger">Erreur lors du chargement des événements</div>';
        console.error('Error loading events:', error);
    }
}

async function loadEventDetails(eventId) {
    const container = document.getElementById('eventDetailsContent');
    container.innerHTML = '<div class="loading"></div>';

    try {
        const [eventResponse, sessionsResponse] = await Promise.all([
            fetchApi(`/events/${eventId}`),
            fetchApi(`/events/${eventId}/sessions`)
        ]);

        const event = await eventResponse;
        const sessions = await sessionsResponse;

        container.innerHTML = `
            <div class="card mb-4">
                <img src="https://picsum.photos/800/400?random=${event.id}" class="card-img-top" alt="${event.name}">
                <div class="card-body">
                    <h3 class="card-title">${event.name}</h3>
                    <p class="card-text">${event.description}</p>
                    <p><strong>Lieu:</strong> ${event.venue}</p>
                    <p><strong>Catégories:</strong> ${event.categories.join(', ')}</p>
                    
                    <h4 class="mt-4">Sessions disponibles</h4>
                    <div class="sessions-container">
                        ${sessions.map(session => `
                            <div class="session-card">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h5>Le ${new Date(session.start_time).toLocaleString()}</h5>
                                        <p class="seats-available">Places disponibles: ${session.available_seats}</p>
                                    </div>
                                    <div class="text-end">
                                        <div class="price">${session.current_price}€</div>
                                        <button class="btn btn-primary" onclick="openBookingModal('${session.id}', ${session.current_price})">
                                            Réserver
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        container.innerHTML = '<div class="alert alert-danger">Erreur lors du chargement des détails</div>';
    }
}

async function loadMyBookings() {
    const container = document.getElementById('bookingsContainer');
    container.innerHTML = '<div class="loading"></div>';

    try {
        const bookings = await fetchApi(`/users/${currentUserId}/bookings`);

        container.innerHTML = bookings.map(booking => `
            <div class="booking-card ${booking.status.toLowerCase()}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h5>Réservation #${booking.id}</h5>
                        <p>Nombre de places: ${booking.seats}</p>
                        <p>Prix par place: ${booking.price_per_seat}€</p>
                        <p>Total: ${booking.seats * booking.price_per_seat}€</p>
                        <p>Statut: <span class="badge bg-${getStatusBadgeColor(booking.status)}">${booking.status}</span></p>
                    </div>
                    <div>
                        ${booking.status === 'PENDING' ? `
                            <button class="btn btn-success" onclick="confirmBooking('${booking.id}')">Confirmer</button>
                            <button class="btn btn-danger" onclick="cancelBooking('${booking.id}')">Annuler</button>
                        ` : ''}
                        ${booking.status === 'CONFIRMED' ? `
                            <button class="btn btn-danger" onclick="cancelBooking('${booking.id}')">Annuler</button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<div class="alert alert-danger">Erreur lors du chargement des réservations</div>';
    }
}

// Gestion des réservations
function openBookingModal(sessionId, price) {
    currentSessionId = sessionId;
    document.getElementById('pricePerSeat').textContent = price;
    updateTotalPrice();
    new bootstrap.Modal(document.getElementById('bookingModal')).show();
}

function updateTotalPrice() {
    const seats = document.getElementById('seatsInput').value;
    const pricePerSeat = parseFloat(document.getElementById('pricePerSeat').textContent);
    document.getElementById('totalPrice').textContent = (seats * pricePerSeat).toFixed(2);
}

async function confirmBooking() {
    const seats = document.getElementById('seatsInput').value;
    
    try {
        const response = await fetchApi('/bookings/', {
            method: 'POST',
            body: JSON.stringify({
                user_id: currentUserId,
                session_id: currentSessionId,
                seats: parseInt(seats)
            })
        });

        if (response.ok) {
            const booking = await response;
            // Confirmer automatiquement la réservation
            await fetchApi(`/bookings/${booking.id}/confirm`, {
                method: 'POST'
            });
            
            bootstrap.Modal.getInstance(document.getElementById('bookingModal')).hide();
            showMyBookings();
        } else {
            alert('Erreur lors de la réservation');
        }
    } catch (error) {
        alert('Erreur lors de la réservation');
    }
}

async function cancelBooking(bookingId) {
    if (!confirm('Êtes-vous sûr de vouloir annuler cette réservation ?')) {
        return;
    }

    try {
        const response = await fetchApi(`/bookings/${bookingId}/cancel`, {
            method: 'POST'
        });

        if (response.ok) {
            loadMyBookings();
        } else {
            alert('Erreur lors de l\'annulation');
        }
    } catch (error) {
        alert('Erreur lors de l\'annulation');
    }
}

// Utilitaires
function getStatusBadgeColor(status) {
    switch (status) {
        case 'CONFIRMED': return 'success';
        case 'PENDING': return 'warning';
        case 'CANCELLED': return 'danger';
        default: return 'secondary';
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    showEvents();
    document.getElementById('seatsInput').addEventListener('input', updateTotalPrice);
}); 