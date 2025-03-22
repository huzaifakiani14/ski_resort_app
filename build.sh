#!/bin/bash

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Build the frontend
echo "Building the frontend..."
cd ski-resort-frontend
npm install
npm run build
cd ..

echo "Build completed successfully!" 