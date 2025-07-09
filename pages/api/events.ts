import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // モックデータ（現在のFastAPIから移行）
  const mockEvents = [
    {
      title: "Tomorrowland 2024",
      date: "2024-07-19",
      place: "Boom, Belgium",
      genre: "Electronic/Psytrance",
      description: "The world's most famous electronic music festival",
      url: "https://www.tomorrowland.com",
      image: "https://images.unsplash.com/photo-1518005020951-eccb49447d0a"
    },
    {
      title: "Ultra Music Festival",
      date: "2024-03-24",
      place: "Miami, USA",
      genre: "Electronic/EDM",
      description: "Premier electronic music festival",
      url: "https://ultramusicfestival.com",
      image: "https://images.unsplash.com/photo-1506157786151-b8491531f063"
    },
    {
      title: "Creamfields",
      date: "2024-08-23",
      place: "Daresbury, UK",
      genre: "Electronic/Dance",
      description: "UK's biggest dance music festival",
      url: "https://creamfields.com",
      image: "https://images.unsplash.com/photo-1459749411175-04bf5292ceea"
    }
  ];

  res.status(200).json({
    success: true,
    events: mockEvents,
    total: mockEvents.length,
    source: "next_api",
    timestamp: new Date().toISOString()
  });
}