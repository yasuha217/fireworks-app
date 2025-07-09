import { useState, useEffect } from 'react';
import Head from 'next/head';

interface Event {
  title: string;
  date: string;
  place: string;
  genre: string;
  description: string;
  url: string;
  image: string;
}

export default function Home() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await fetch('/api/events');
      const data = await response.json();
      if (data.success) {
        setEvents(data.events);
      }
    } catch (error) {
      console.error('Error fetching events:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>PsyFinder - Find Your Next Psychedelic Trance Event</title>
        <meta name="description" content="Find psychedelic trance events" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;700&display=swap" rel="stylesheet" />
      </Head>

      <main className="container">
        <header className="header">
          <h1 className="title">PsyFinder</h1>
          <p className="subtitle">Find Your Next Psychedelic Trance Event</p>
        </header>

        <section className="search-section">
          <form className="search-form">
            <select id="source-filter" className="filter-select">
              <option value="major">Major Festivals</option>
              <option value="clubberia">Tokyo Events</option>
            </select>
            <button type="submit" className="search-button">Search Events</button>
          </form>
        </section>

        <section className="event-list-section">
          <h2>Upcoming Events</h2>
          
          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              <p>Loading events...</p>
            </div>
          ) : (
            <div id="event-cards-container" className="events-grid">
              {events.map((event, index) => (
                <div key={index} className="event-card">
                  <img 
                    src={event.image} 
                    alt={event.title}
                    onError={(e) => {
                      e.currentTarget.src = 'https://images.unsplash.com/photo-1518005020951-eccb49447d0a?q=80&w=400&auto=format&fit=crop';
                    }}
                  />
                  <h3>{event.title}</h3>
                  <p><strong>Date:</strong> {event.date}</p>
                  <p><strong>Location:</strong> {event.place}</p>
                  <p><strong>Genre:</strong> {event.genre}</p>
                  <p className="event-description">{event.description}</p>
                  <a href={event.url} target="_blank" rel="noopener noreferrer">
                    View Details
                  </a>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </>
  );
}