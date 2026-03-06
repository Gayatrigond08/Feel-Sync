# Feel Sync 🌱

Feel Sync is a beautifully designed, intelligent mental wellness platform built to provide empathetic support, self-reflection, and mindfulness tools in a highly calming environment.

## ✨ Features and Detailed Working

### 1. **Dynamic Mood Journal & Tracker**
- **How it works:** Users can log their daily mood (rating from 1-5, which correlate to custom emojis) along with a text entry describing their feelings.
- The **Scrapbook Journal** displays past logs in a visually stunning horizontal "photo wall" layout. Your entries are playfully styled with washi tape, custom fonts, and cute emoji stickers, acting as a personal memory board.
- **Data Analytics:** The app uses Chart.js to render a beautiful trend line graph that automatically populates with the user's historical mood data points (matching dates with logged scores), allowing the user to track their emotional wellbeing over time.

### 2. **MindBot AI Therapist**
- **How it works:** Users engage with a compassionate AI companion that actively listens and responds dynamically to their concerns.
- **Conversational Awareness:** The backend uses OpenAI's GPT models paired with TextBlob. Natural Language Processing (NLP) runs sentiment analysis on user inputs to detect specific emotions (anxiety, depression, stress, happiness) and adjusts the system prompts behind the scenes before hitting the AI. 
- **Crisis Detection:** The `ai_chat.py` engine flags severe indicators and, overriding standard chatbot responses, will immediately return emergency helplines and priority crisis intervention text, ensuring user safety.

### 3. **Interactive Wellness Hub**
- **Guided Breathing:** Includes an interactive 4-7-8 breathing circle module that automatically drives breathing patterns via CSS animations and JavaScript timing.
- **Soul Whispers:** A dynamic feature delivering daily comfort—users can click to fetch new calming lyrics, empowering facts, and motivational thoughts drawn directly from the database and randomized on the front-end.
- **Mini Games:** Elements designed to ground the user during high-stress scenarios.

### 4. **Adaptive Botanical Theming**
- **Guest Experience:** The logged-out landing page features a completely custom, incredibly calming backdrop consisting of hand-painted, soft green vines, creepers, shrubs with small buds, and delicate butterflies—welcoming users immediately with a sense of peace. 
- **Time-Based Gradients:** Once logged in, the application actively checks the user's local system time and strictly applies contextually appropriate soft pastel gradients:
  - **Morning**: Soft peachy pink
  - **Afternoon**: Gentle mint green
  - **Evening**: Soft lavender
  - **Night**: Muted pale blue-grey

### 5. **Robust System Architecture**
- **Frontend & Backend Separation:** The project is correctly structured with a `frontend` folder containing raw CSS/JS/HTML assets and a `backend` folder housing the Python logic.
- **Secure Authentication:** The database (`feel_sync_db` running on MySQL) utilizes JSON Web Tokens (JWT) bound to `app.secret_key` alongside secure `pbkdf2` Werkzeug password hashing procedures for safe registration and login authentication via REST APIs.

---

## 🛠️ Technology Stack

- **Frontend:** Vanilla HTML5, CSS3, JavaScript, Chart.js.
- **Backend:** Python + Flask (`app.py`).
- **Database:** MySQL via `mysql-connector-python`.
- **Authentication:** PyJWT, Werkzeug.security.
- **AI / NLP:** OpenAI API, TextBlob.

---

## 🚀 Getting Started

### Prerequisites

1. Python 3.8 or higher
2. MySQL Server (running on port 3307, or adjustable in `backend/.env`)
3. An OpenAI API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd Feel-Sync
   ```

2. **Setup virtual environment (recommended):**
   ```bash
   cd backend
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
   Make sure you are in the `backend` folder. Create a `.env` file and add your specific configurations:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   FLASK_SECRET_KEY=your_secure_flask_key
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_PORT=3307
   ```

5. **Run the Application:**
   The application logic is smart. Running it will instantly build all MySQL tables if they are empty or missing, inject sample data, and hook up the frontend.
   ```bash
   python app.py
   ```

6. **Access the App:**
   Open a web browser and navigate to `http://127.0.0.1:5000/`.

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page or submit pull requests to help improve Feel Sync.
