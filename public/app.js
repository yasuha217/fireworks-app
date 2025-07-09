// Global variables
let eventCardsContainer, searchForm, loadingElement;
// Use direct API URL for Vercel deployment
const API_BASE_URL = '/api';

// Global variable to prevent concurrent API calls
let isLoadingEvents = false;
let debounceTimeout;

// Debounced load events function
function loadEventsDebounced(query = '', location = '', genre = '', forceRefresh = false, source = 'major') {
    if (debounceTimeout) {
        clearTimeout(debounceTimeout);
    }
    
    debounceTimeout = setTimeout(() => {
        loadEvents(query, location, genre, forceRefresh, source);
    }, 300);
}

// Function to load events from the FastAPI backend
async function loadEvents(query = '', location = '', genre = '', forceRefresh = false, source = 'major') {
    try {
        if (isLoadingEvents && !forceRefresh) {
            console.log('Already loading events, skipping...');
            return;
        }
        
        if (!eventCardsContainer) {
            console.error('eventCardsContainer not available');
            return;
        }
        
        isLoadingEvents = true;
        showLoading(true);
        
        const params = new URLSearchParams();
        if (forceRefresh) params.append('force_refresh', 'true');
        params.append('source', source);
        
        // Add genre filter only for clubberia source
        if (source === 'clubberia') {
            params.append('genre', 'psy');
        }
        
        console.log(`Loading events with source: ${source}`);
        const response = await fetch(`${API_BASE_URL}/events?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`Received ${data.events?.length || 0} events from source: ${data.source}`);
        
        if (data.success) {
            displayEvents(data.events);
            showCacheInfo(data);
        } else {
            showError('Failed to load events from server');
        }
    } catch (error) {
        console.error('Error loading events:', error);
        showError(`Network error: ${error.message}. Make sure the FastAPI server is running on ${API_BASE_URL}`);
    } finally {
        isLoadingEvents = false;
        showLoading(false);
    }
}

// Function to search events (simplified - no client-side filtering needed)
function searchEvents(source) {
    loadEventsDebounced('', '', '', false, source);
}

// Function to create a single event card
function createCard(event) {
    const card = document.createElement('div');
    card.classList.add('event-card');
    
    // Force card styles for debugging
    card.style.cssText = `
        width: 100% !important;
        background: rgba(0, 0, 0, 0.8) !important;
        border: 1px solid #00ffff !important;
        border-radius: 8px !important;
        padding: 20px !important;
        color: white !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        transition: transform 0.25s !important;
    `;
    
    card.innerHTML = `
        <img src="${event.image}" alt="${event.title}" 
             onerror="this.src='https://images.unsplash.com/photo-1518005020951-eccb49447d0a?q=80&w=400&auto=format&fit=crop'" 
             loading="lazy"
             style="width: 100%; height: 180px; object-fit: cover; border-radius: 8px; margin-bottom: 15px;">
        <h3 style="color: #00ffff !important; margin: 15px 0 10px 0;">${event.title}</h3>
        <p style="color: white !important; margin: 8px 0;"><strong>Date:</strong> ${event.date}</p>
        <p style="color: white !important; margin: 8px 0;"><strong>Location:</strong> ${event.place}</p>
        <p style="color: white !important; margin: 8px 0;"><strong>Genre:</strong> ${event.genre}</p>
        <p class="event-description" style="color: rgba(255,255,255,0.8) !important; margin: 10px 0;">${event.description}</p>
        <a href="${event.url}" target="_blank" rel="noopener noreferrer" style="color: #ff00ff !important; text-decoration: underline;">View Details</a>
    `;
    
    return card;
}

// Function to render cards with fragment for better performance
function renderCards(arr) {
    if (!eventCardsContainer) {
        console.error('eventCardsContainer not found!');
        return;
    }
    
    eventCardsContainer.innerHTML = ""; // Clear container once
    
    if (arr.length === 0) {
        eventCardsContainer.innerHTML = `
            <div class="no-events">
                <h3>No events found</h3>
                <p>Try adjusting your search criteria</p>
            </div>
        `;
        eventCardsContainer.classList.add('loaded');
        return;
    }
    
    // Use document fragment for better performance
    const fragment = document.createDocumentFragment();
    arr.forEach(event => fragment.appendChild(createCard(event)));
    eventCardsContainer.appendChild(fragment); // Single DOM update
    
    // Add loaded class to show container with fade-in effect
    eventCardsContainer.classList.add('loaded');
    
    console.log(`Successfully rendered ${arr.length} event cards`);
}

// Function to display events (updated to use renderCards)
function displayEvents(events) {
    console.log(`Displaying ${events.length} events:`, events);
    
    // Force container visibility and grid layout
    if (eventCardsContainer) {
        eventCardsContainer.style.cssText = `
            display: grid !important;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)) !important;
            gap: 28px !important;
            padding: 32px 12px !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            visibility: visible !important;
            opacity: 1 !important;
        `;
    }
    
    renderCards(events);
}

// Function to show cache info
function showCacheInfo(data) {
    // キャッシュ情報を表示（デバッグ用）
    if (data.source && data.cache_info) {
        console.log(`Data source: ${data.source}`);
        console.log('Cache info:', data.cache_info);
        
        // UI上にもキャッシュ情報を表示
        const existingInfo = document.querySelector('.cache-info');
        if (existingInfo) existingInfo.remove();
        
        const cacheInfoDiv = document.createElement('div');
        cacheInfoDiv.className = 'cache-info';
        cacheInfoDiv.innerHTML = `
            <small style="color: rgba(255,255,255,0.6); margin-bottom: 10px; display: block;">
                Source: ${data.source} | Last updated: ${data.cache_info?.last_update || 'Unknown'}
            </small>
        `;
        
        const eventSection = document.querySelector('.event-list-section h2');
        if (eventSection) {
            eventSection.parentNode.insertBefore(cacheInfoDiv, eventSection.nextSibling);
        }
    }
}

// Function to show/hide loading spinner
function showLoading(show) {
    console.log('showLoading called with:', show);
    if (loadingElement) {
        if (show) {
            loadingElement.style.display = 'block';
            if (eventCardsContainer) {
                eventCardsContainer.style.display = 'none';
                console.log('Container hidden for loading');
            }
        } else {
            loadingElement.style.display = 'none';
            if (eventCardsContainer) {
                eventCardsContainer.style.display = 'block'; // Changed from 'grid' to 'block'
                eventCardsContainer.style.visibility = 'visible';
                eventCardsContainer.style.opacity = '1';
                console.log('Container shown after loading');
            }
        }
    }
}

// Function to show error messages
function showError(message) {
    if (eventCardsContainer) {
        eventCardsContainer.innerHTML = `
            <div class="error-message">
                <h3>Error</h3>
                <p>${message}</p>
                <button onclick="location.reload()" class="retry-button" style="
                    margin-top: 10px;
                    padding: 8px 16px;
                    background: #ff00ff;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                ">Retry</button>
            </div>
        `;
    }
}

// Health check function
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('Backend health:', data);
    } catch (error) {
        console.warn('Backend health check failed:', error);
    }
}

// Function to add refresh button
function addRefreshButton() {
    const searchSection = document.querySelector('.search-section');
    if (searchSection && !document.querySelector('.refresh-button')) {
        const refreshButton = document.createElement('button');
        refreshButton.className = 'refresh-button';
        refreshButton.innerHTML = '🔄 Refresh Events';
        refreshButton.style.cssText = `
            margin-top: 15px;
            padding: 10px 20px;
            background: linear-gradient(45deg, #ff00ff, #00ffff);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'Orbitron', sans-serif;
            transition: transform 0.3s;
        `;
        
        refreshButton.addEventListener('click', () => {
            const sourceFilter = document.getElementById('source-filter');
            const source = sourceFilter ? sourceFilter.value : 'major';
            loadEvents('', '', '', true, source); // Force refresh
        });
        
        refreshButton.addEventListener('mouseover', () => {
            refreshButton.style.transform = 'scale(1.05)';
        });
        
        refreshButton.addEventListener('mouseout', () => {
            refreshButton.style.transform = 'scale(1)';
        });
        
        searchSection.appendChild(refreshButton);
    }
}

// DOM Content Loaded Event Handler
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded');
    
    try {
        // Hide test message if JavaScript is working
        const testMessage = document.querySelector('.test-message');
        if (testMessage) {
            testMessage.style.display = 'none';
        }
        
        // Initialize global variables
        eventCardsContainer = document.getElementById('event-cards-container');
        searchForm = document.getElementById('search-form');
        loadingElement = document.getElementById('loading');
        
        console.log('Elements found:', {
            eventCardsContainer: !!eventCardsContainer,
            searchForm: !!searchForm,
            loadingElement: !!loadingElement
        });
        
        // Check if all required elements exist
        if (!eventCardsContainer) {
            console.error('ERROR: event-cards-container not found');
            return;
        }
        
        if (!searchForm) {
            console.error('ERROR: search-form not found');
            return;
        }
        
        if (!loadingElement) {
            console.error('ERROR: loading element not found');
            return;
        }
        
        // Handle search form submission
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const source = document.getElementById('source-filter').value;
            
            console.log('Form submitted with source:', source);
            loadEvents('', '', '', false, source);
        });
        
        // Handle source change to reload events with debounce
        let sourceChangeTimeout;
        let lastSource = 'clubberia'; // Track last source to prevent unnecessary reloads
        const sourceFilter = document.getElementById('source-filter');
        
        if (sourceFilter) {
            sourceFilter.addEventListener('change', (e) => {
                const source = e.target.value;
                
                // Prevent reload if source hasn't actually changed
                if (source === lastSource) {
                    console.log('Source unchanged, skipping reload');
                    return;
                }
                
                lastSource = source;
                
                // Clear previous timeout
                if (sourceChangeTimeout) {
                    clearTimeout(sourceChangeTimeout);
                }
                
                // Debounce the source change
                sourceChangeTimeout = setTimeout(() => {
                    console.log(`Source changed to: ${source}`);
                    loadEventsDebounced('', '', '', false, source);
                }, 300);
            });
        } else {
            console.error('Source filter not found!');
        }
        
        // Add refresh button functionality
        addRefreshButton();
        
        // Check backend health on startup
        checkBackendHealth();
        
        // Load initial events (start with major festivals for faster loading)
        console.log('Loading initial events...');
        
        // Prevent infinite loops by adding a flag
        if (!window.initialLoadComplete) {
            window.initialLoadComplete = true;
            
            // Use direct call instead of debounced to avoid timing issues
            setTimeout(() => {
                console.log('Starting automatic API load...');
                loadEvents('', '', '', false, 'clubberia');
            }, 100); // Small delay to ensure DOM is fully ready
        }
        
    } catch (error) {
        console.error('Error in DOMContentLoaded:', error);
        
        // Show error message to user
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(255, 0, 0, 0.8);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            z-index: 10000;
        `;
        errorDiv.innerHTML = `
            <h3>JavaScript Error</h3>
            <p>${error.message}</p>
            <p>Please check the console for more details</p>
        `;
        document.body.appendChild(errorDiv);
    }
});