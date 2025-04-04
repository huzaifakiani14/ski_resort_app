# Ski Resort Finder

A modern web application that helps users find ski resorts based on location or description. Built with React.js and Python Flask.

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

## Prerequisites

- Python 3.8 or higher
- Node.js and npm
- Google Maps API key (with Places API enabled)

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd ski_resort_finder
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Google Maps API key
   # GOOGLE_MAPS_API_KEY=your_api_key_here
   ```

5. Run the Flask server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ski-resort-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Google Maps API key
   # REACT_APP_GOOGLE_MAPS_API_KEY=your_api_key_here
   ```

4. Start the development server:
   ```bash
   npm start
   ```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Enter a location or description in the search box
3. Use the filters to refine your search results
4. Click on a resort card to view more details
5. Visit the resort's website directly from the application

## Environment Variables

The application requires two environment variables:

1. Backend (`ski_resort_finder/.env`):
   ```
   GOOGLE_MAPS_API_KEY=your_api_key_here
   ```

2. Frontend (`ski-resort-frontend/.env`):
   ```
   REACT_APP_GOOGLE_MAPS_API_KEY=your_api_key_here
   ```

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