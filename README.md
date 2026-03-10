# Feel Sync 🌱

Feel Sync is a beautifully designed, intelligent mental wellness platform built to provide empathetic support, self-reflection, and mindfulness tools in a highly calming environment.

## ✨ Features and Detailed Working

### 1. **Dynamic Mood Journal & Tracker**
- **How it works:** Users can log their daily mood (rating from 1-5, which correlate to custom emojis) along with a text entry describing their feelings.
- The **Scrapbook Journal** displays past logs in a visually stunning horizontal "photo wall" layout. Your entries are playfully styled with washi tape, custom fonts, and cute emoji stickers, acting as a personal memory board.
- **Data Analytics:** The app uses Chart.js to render a beautiful trend line graph that automatically populates with the user's historical mood data points.

### 2. **MindBot AI Therapist (Hybrid Engine)**
- **How it works:** Users engage with a compassionate AI companion that actively listens and responds dynamically to their concerns.
- **Hybrid AI Logic:** The system uses a high-performance **Groq (Llama-3.3-70b)** engine as the primary driver for lightning-fast responses, with **OpenAI GPT** as an automatic failover backup.
- **Conversational Awareness:** The backend uses TextBlob for real-time sentiment analysis to detect specific emotions (anxiety, depression, stress, happiness) and adjusts the system prompts behind the scenes.
- **Crisis Detection:** The `ai_chat.py` engine flags severe indicators and will immediately provide priority crisis intervention resources and emergency contacts.

### 3. **Deep Intelligence Dashboard**
- **Mood Ratio:** Visualizes the balance of positive, neutral, and negative days using interactive doughnut charts.
- **Weekly Trends:** A bar graph showing **Average Mood by Day of Week**, helping users identify if certain days (like Mondays or Fridays) consistently impact their wellbeing.
- **Stability Insights:** Calculates mood stability and provides textual "Intelligence Insights" based on recent emotional patterns.

### 4. **Adaptive Botanical Theming**
- **Serene Environment:** The landing page features a calming backdrop of hand-painted vines, creepers, and delicate butterflies. 
- **Time-Based Gradients:** Once logged in, the application applies contextually appropriate soft pastel gradients:
  - **Morning**: Soft peachy pink
  - **Afternoon**: Gentle mint green
  - **Evening**: Soft lavender
  - **Night**: Muted pale blue-grey

### 5. **Robust System Architecture**
- **Frontend & Backend Separation:** Correctly structured with a `frontend` folder for assets and a `backend` folder for logic.
- **Secure Authentication:** Utilizes JSON Web Tokens (JWT) and secure password hashing via Werkzeug for safe user accounts.

---

## 🛠️ Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript, Chart.js.
- **Backend:** Python + Flask (`app.py`).
- **Database:** MySQL.
- **AI / NLP:** Groq Cloud API, OpenAI API, TextBlob.

---

## 🚀 Getting Started

### Prerequisites

1. Python 3.8 or higher
2. MySQL Server (running on port 3307, or adjustable in `backend/.env`)
3. A Groq API Key (Primary) and/or OpenAI API Key (Backup)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd Feel-Sync
   ```

2. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the `backend` folder:
   ```env
   GROQ_API_KEY=your_groq_key_here
   OPENAI_API_KEY=your_openai_key_here
   FLASK_SECRET_KEY=your_secure_key
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_PORT=3307
   ```

4. **Run the Application:**
   ```bash
   python app.py
   ```

5. **Access the App:**
   Open a browser and navigate to `http://127.0.0.1:5000/`.

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!
