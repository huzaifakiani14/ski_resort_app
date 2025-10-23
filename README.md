# Ski Resort Finder

A modern web application that helps users find ski resorts based on location or description. Built with React.js and Python Flask, deployed on Vercel.

## Features

- Search for ski resorts by location or description
- Real-time filtering by rating and distance
- Detailed resort information with photos
- User reviews and ratings
- Responsive design with winter theme
- Interactive UI with animations
- Recent search history

## Tech Stack

- Frontend: React.js
- Backend: Python Flask
- APIs: Google Places API
- Styling: CSS3 with animations
- Natural Language Processing: spaCy, Sentence Transformers
- Deployment: Vercel

## Prerequisites

- Python 3.9 or higher
- Node.js 18.x and npm
- Google Maps API key (with Places API and Geocoding API enabled)

## Setup

### Environment Variables

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your Google Maps API key:
   ```
   GOOGLE_MAPS_API_KEY=your_api_key_here
   ```

### Local Development

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Node.js dependencies:
   ```bash
   cd ski-resort-frontend
   npm install
   cd ..
   ```

3. Start the development servers:
   ```bash
   npm run dev
   ```

This will start both the Flask backend (port 5001) and React frontend (port 3000).

### Production Deployment on Vercel

1. Push your code to a GitHub repository
2. Connect your repository to Vercel
3. Set the environment variable `GOOGLE_MAPS_API_KEY` in Vercel dashboard
4. Deploy!

The application will be automatically built and deployed with:
- Backend API at `/api/*` routes
- Frontend at the root routes

## Project Structure

```
ski-resort-app/
├── api/                    # Vercel serverless functions
│   └── index.py           # Main API handler
├── ski_resort_finder/     # Backend logic
│   ├── __init__.py
│   ├── app.py            # Flask app (for local dev)
│   └── ski_resort.py     # Core ski resort finder logic
├── ski-resort-frontend/   # React frontend
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   └── App.css       # Styling
│   └── package.json
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── package.json         # Root package configuration
```

## API Endpoints

- `GET /api/test` - Test backend connectivity
- `POST /api/search` - Search for ski resorts

## Usage

1. Open your browser and navigate to the application URL
2. Enter a location or description in the search box
3. Use the filters to refine your search results
4. Click on a resort card to view more details
5. Visit the resort's website directly from the application

## Environment Variables

The application requires one environment variable:

- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key with Places API and Geocoding API enabled

Make sure to:
- Never commit your actual API keys to version control
- Keep your API keys secure and don't share them publicly
- Use different API keys for development and production environments

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.