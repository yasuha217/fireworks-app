const express = require('express');
const cors = require('cors');
const axios = require('axios');
const cheerio = require('cheerio');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Serve static files from public directory
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Search events endpoint
app.get('/api/search', async (req, res) => {
    try {
        const { query, location, genre } = req.query;
        
        // For now, return mock data with search parameters
        const mockEvents = [
            {
                id: 1,
                title: "Cosmic Resonance",
                date: "2025/07/20",
                location: "Koh Phangan, Thailand",
                genre: "Progressive Psytrance",
                image: "https://images.unsplash.com/photo-1518005020951-eccb49447d0a?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                link: "#",
                description: "A transcendent journey through progressive psytrance"
            },
            {
                id: 2,
                title: "Quantum Leap Festival",
                date: "2025/08/15",
                location: "Goa, India",
                genre: "Full-On Psytrance",
                image: "https://images.unsplash.com/photo-1517457375823-0706694789e8?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                link: "#",
                description: "High-energy full-on psytrance in the birthplace of Goa trance"
            },
            {
                id: 3,
                title: "Mystic Forest Gathering",
                date: "2025/09/01",
                location: "Amazon Rainforest, Brazil",
                genre: "Forest Psytrance",
                image: "https://images.unsplash.com/photo-1500382017468-9049ce8b650c?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                link: "#",
                description: "Dark forest psytrance deep in the Amazon jungle"
            },
            {
                id: 4,
                title: "Hitech Madness",
                date: "2025/09/15",
                location: "Tokyo, Japan",
                genre: "Hitech Psytrance",
                image: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                link: "#",
                description: "Ultra-fast hitech psytrance in the neon city"
            },
            {
                id: 5,
                title: "Tribal Gathering",
                date: "2025/10/05",
                location: "Sahara Desert, Morocco",
                genre: "Tribal Psytrance",
                image: "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                link: "#",
                description: "Ancient tribal rhythms meet modern psytrance"
            }
        ];

        // Filter events based on search parameters
        let filteredEvents = mockEvents;

        if (query) {
            filteredEvents = filteredEvents.filter(event => 
                event.title.toLowerCase().includes(query.toLowerCase()) ||
                event.description.toLowerCase().includes(query.toLowerCase())
            );
        }

        if (location) {
            filteredEvents = filteredEvents.filter(event => 
                event.location.toLowerCase().includes(location.toLowerCase())
            );
        }

        if (genre) {
            filteredEvents = filteredEvents.filter(event => 
                event.genre.toLowerCase().includes(genre.toLowerCase())
            );
        }

        res.json({
            success: true,
            events: filteredEvents,
            total: filteredEvents.length
        });

    } catch (error) {
        console.error('Search error:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to search events'
        });
    }
});

// Future scraping endpoints
app.get('/api/scrape/resident-advisor', async (req, res) => {
    // TODO: Implement Resident Advisor scraping
    res.json({ message: 'Resident Advisor scraping not implemented yet' });
});

app.get('/api/scrape/eventbrite', async (req, res) => {
    // TODO: Implement Eventbrite scraping
    res.json({ message: 'Eventbrite scraping not implemented yet' });
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});