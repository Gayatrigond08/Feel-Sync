# Feel Sync 

Feel Sync is a beautifully designed, intelligent mental wellness platform built to provide empathetic support, self-reflection, and mindfulness tools.

## ✨ Features

- **MindBot AI Therapist:** Engage with a compassionate AI companion that actively listens, analyzes emotional sentiment using NLP, and provides tailored coping strategies and support. Includes built-in crisis detection protocols.
- **Scrapbook Journal:** Log your daily mood and thoughts in a visually stunning horizontal "photo wall" layout. Your entries are playfully styled with washi tape, custom fonts, and cute emoji stickers, acting as a personal memory board.
- **Mood Analytics & Tracking:** Track your mental state over time with visual analytics comparing your recent mood trends (30-day overview and 7-day rolling trends).
- **Wellness Hub:** Access curated resources including guided breathing exercises (like the interactive 4-7-8 breathing circle) and mindful "Soul Whispers" for daily affirmations and grounding.
- **Premium User Experience:** Features a modern, responsive, and animated user interface built with smooth gradients, floating glowing orbs, and clean glassmorphism components.

## 🛠️ Technology Stack

- **Frontend:** Vanilla HTML5, CSS3, and JavaScript (No heavy frameworks, highly optimized, and beautifully customized).
- **Backend:** Python powered by Flask.
- **Database:** MySQL.
- **Authentication:** JWT (JSON Web Tokens) with secure password hashing via Werkzeug.
- **AI / NLP:** OpenAI API for the conversational MindBot, and TextBlob for initial text-based sentiment analysis.

## 🚀 Getting Started

### Prerequisites

1. Python 3.8 or higher
2. MySQL Server (running on port 3307, or adjustable in `.env`)
3. An OpenAI API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd Feel-Sync
   ```

2. **Setup virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your specific configurations:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   FLASK_SECRET_KEY=your_secure_flask_key
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_PORT=3307
   DB_NAME=feel_sync_db
   ```

5. **Run the Application:**
   The application will automatically connect and create the necessary database tables (users, mood logs, chat sessions) on first launch if they don't already exist.
   ```bash
   python app.py
   ```

6. **Access the App:**
   Open a web browser and navigate to `http://127.0.0.1:5000/`.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page or submit pull requests to help improve Feel Sync.

## 📄 License
This project is provided under the MIT License.
