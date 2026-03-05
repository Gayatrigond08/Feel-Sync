# Feel Sync Web Application - MVP Implementation

## Project Overview
A mental wellness platform with mood tracking, AI-powered chat support, and wellness resources.

## Frontend Files (HTML Template)
1. **index.html** - Main landing page with navigation and sections
2. **style.css** - Modern, calming design with responsive layout
3. **script.js** - Frontend JavaScript for interactions and API calls

## Backend Files (Python Flask)
4. **app.py** - Main Flask application with routes and AI integration
5. **database.py** - MySQL database connection and models
6. **ai_chat.py** - AI mechanism for mental health support
7. **requirements.txt** - Python dependencies

## Database Schema
- Users table (id, username, email, password_hash, created_at)
- Mood_entries table (id, user_id, mood_score, notes, timestamp)
- Chat_sessions table (id, user_id, messages, timestamp)

## Key Features
- User registration/login
- Mood tracking with visual charts
- AI-powered mental health chatbot
- Wellness resources and tips
- Responsive design with calming colors

## AI Integration
- OpenAI GPT integration for mental health support
- Sentiment analysis for mood detection
- Personalized wellness recommendations