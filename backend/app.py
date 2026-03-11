from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import pymysql.cursors
import os
from datetime import datetime, timedelta, timezone
import jwt
from functools import wraps
import openai
from textblob import TextBlob
import json
from ai_chat import MentalHealthAI

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
CORS(app)

# OpenAI API configuration
openai.api_key = os.getenv('OPENAI_API_KEY', '')

# MySQL Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'feel_sync_db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', 3307))
}

class DatabaseManager:
    def __init__(self):
        # We will create connections per query to avoid thread-safety issues in Flask
        pass
    
    def get_connection(self):
        try:
            return pymysql.connect(
                **DB_CONFIG,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
        except Exception as e:
            print(f"Error connecting to MySQL with PyMySQL: {e}")
            return None
    
    def disconnect(self):
        # Kept for backward compatibility if called
        pass
    
    def execute_query(self, query, params=None):
        connection = self.get_connection()
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    result = cursor.lastrowid
                
                return result
        except Exception as e:
            print(f"Database error: {e}")
            return None
        finally:
            connection.close()

db = DatabaseManager()

def log_activity(user_id, activity_type, activity_data=None):
    """Helper to log user activities into the database"""
    try:
        data_json = json.dumps(activity_data) if activity_data else None
        db.execute_query(
            "INSERT INTO user_activity (user_id, activity_type, activity_data, timestamp) VALUES (%s, %s, %s, %s)",
            (user_id, activity_type, data_json, datetime.now())
        )
    except Exception as e:
        print(f"Failed to log activity: {e}")


# MindBot - Mental Health AI Orchestrator
ai_therapist = MentalHealthAI()

# (Placeholder for existing assignment)

@app.route('/favicon.ico')
def favicon():
    return '', 204

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/daily-reflection')
def daily_reflection():
    return render_template('daily_reflection.html')

@app.route('/api/mood-analytics', methods=['GET'])
@token_required
def get_mood_analytics(current_user_id):
    try:
        # Fetch last 30 days of data
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Weekly Mood Trend
        weekly_trend = db.execute_query(
            """SELECT DATE_FORMAT(timestamp, '%%Y-%%m-%%d') as date, AVG(mood_score) as avg_score 
               FROM mood_entries 
               WHERE user_id = %s AND timestamp >= %s 
               GROUP BY date 
               ORDER BY date ASC""",
            (current_user_id, datetime.now() - timedelta(days=7))
        )
        
        # Emotion Distribution
        emotion_dist = db.execute_query(
            """SELECT mood_score, COUNT(*) as count 
               FROM mood_entries 
               WHERE user_id = %s 
               GROUP BY mood_score""",
            (current_user_id,)
        )
        
        # Positivie vs Negative
        # Scores 1-2 are negative, 3 is neutral, 4-5 are positive
        pos_neg_ratio = db.execute_query(
            """SELECT 
               SUM(CASE WHEN mood_score >= 4 THEN 1 ELSE 0 END) as positive,
               SUM(CASE WHEN mood_score <= 2 THEN 1 ELSE 0 END) as negative,
               SUM(CASE WHEN mood_score = 3 THEN 1 ELSE 0 END) as neutral
               FROM mood_entries 
               WHERE user_id = %s""",
            (current_user_id,)
        )
        
        # Convert Decimal/Date objects to serializable types
        if weekly_trend:
            for d in weekly_trend:
                if d.get('avg_score') is not None: d['avg_score'] = float(d['avg_score'])
        
        # Ensure ratio values are serializable
        ratio = pos_neg_ratio[0] if pos_neg_ratio else {'positive': 0, 'negative': 0, 'neutral': 0}
        for key in ratio:
            if ratio[key] is not None: ratio[key] = int(ratio[key])

        return jsonify({
            'weekly_trend': weekly_trend or [],
            'emotion_distribution': emotion_dist or [],
            'ratio': ratio
        }), 200
    except Exception as e:
        print(f"Mood analytics error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/chatbot', methods=['POST'])
@token_required
def mental_health_chatbot(current_user_id):
    try:
        data = request.get_json()
        user_message = data.get('message')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'message': 'Message is required'}), 400
            
        # Generate empathetic response using upgraded AI logic
        ai_result = ai_therapist.generate_personalized_response(user_message, conversation_history)
        response_text = ai_result['response']
        
        # Add suggestions if available
        if ai_result.get('suggested_technique'):
            tech = ai_result['suggested_technique']
            response_text += f"\n\n**Suggested Strategy:** {tech['name']}\n{tech['description']}"
            
        # Save to database
        db.execute_query(
            "INSERT INTO chat_sessions (user_id, message_type, content, timestamp) VALUES (%s, %s, %s, %s)",
            (current_user_id, 'user', user_message, datetime.now())
        )
        
        db.execute_query(
            "INSERT INTO chat_sessions (user_id, message_type, content, timestamp) VALUES (%s, %s, %s, %s)",
            (current_user_id, 'bot', response_text, datetime.now())
        )
        
        # Log activity
        log_activity(current_user_id, 'ai_chat', {'sentiment': ai_result.get('analysis', {}).get('sentiment')})

            
        return jsonify({'response': response_text}), 200
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/pattern-insights', methods=['GET'])
@token_required
def get_pattern_insights(current_user_id):
    try:
        # Most common emotion
        common_emotion = db.execute_query(
            """SELECT mood_score, COUNT(*) as count 
               FROM mood_entries 
               WHERE user_id = %s 
               GROUP BY mood_score 
               ORDER BY count DESC LIMIT 1""",
            (current_user_id,)
        )
        
        # Mood trends by day of week
        dow_trends = db.execute_query(
            """SELECT DAYNAME(timestamp) as day, AVG(mood_score) as avg_score 
               FROM mood_entries 
               WHERE user_id = %s 
               GROUP BY day 
               ORDER BY FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')""",
            (current_user_id,)
        )
        
        # Positive vs Negative entry percentage
        stats = db.execute_query(
            """SELECT 
               COUNT(*) as total,
               SUM(CASE WHEN mood_score >= 4 THEN 1 ELSE 0 END) as positive,
               SUM(CASE WHEN mood_score <= 2 THEN 1 ELSE 0 END) as negative
               FROM mood_entries 
               WHERE user_id = %s""",
            (current_user_id,)
        )
        
        total = int(stats[0]['total']) if stats and stats[0]['total'] > 0 else 1
        pos_pct = float(stats[0]['positive'] / total * 100) if stats else 0
        neg_pct = float(stats[0]['negative'] / total * 100) if stats else 0
        
        mood_map = {1: 'Sad 😢', 2: 'Down 😕', 3: 'Neutral 😐', 4: 'Good 🙂', 5: 'Happy 😊'}
        
        # Convert Decimal objects to serializable types
        if dow_trends:
            for d in dow_trends:
                if d.get('avg_score') is not None: d['avg_score'] = float(d['avg_score'])

        insights = {
            'common_emotion': mood_map.get(common_emotion[0]['mood_score'], 'N/A') if common_emotion else 'N/A',
            'day_trends': dow_trends or [],
            'pos_percentage': round(pos_pct, 1),
            'neg_percentage': round(neg_pct, 1)
        }
        
        return jsonify(insights), 200
    except Exception as e:
        print(f"Pattern insights error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/daily-reflection', methods=['POST'])
@token_required
def save_daily_reflection(current_user_id):
    try:
        data = request.get_json()
        smile = data.get('smile')
        challenge = data.get('challenge')
        grateful = data.get('grateful')
        
        if not all([smile, challenge, grateful]):
            return jsonify({'message': 'All fields are required'}), 400
            
        # Generate summary using enhanced AI orchestrator
        summary = ai_therapist.summarize_reflections(smile, challenge, grateful)

        # Store in database
        db.execute_query(
            """INSERT INTO daily_reflections (user_id, smile_today, challenge_today, grateful_for, summary) 
               VALUES (%s, %s, %s, %s, %s)""",
            (current_user_id, smile, challenge, grateful, summary)
        )
        
        # Log activity
        log_activity(current_user_id, 'reflection_logged')

        
        return jsonify({'summary': summary}), 201
    except Exception as e:
        print(f"Daily reflection error: {e}")
        return jsonify({'message': 'Internal server error'}), 500


@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'message': 'All fields are required'}), 400
        
        # Check if user already exists
        existing_user = db.execute_query(
            "SELECT id FROM users WHERE email = %s OR username = %s",
            (email, username)
        )
        
        if existing_user:
            return jsonify({'message': 'User already exists'}), 409
        
        # Hash password and create user
        password_hash = generate_password_hash(password)
        user_id = db.execute_query(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (%s, %s, %s, %s)",
            (username, email, password_hash, datetime.now())
        )
        
        if user_id:
            # Initialize default user preferences
            db.execute_query(
                "INSERT INTO user_preferences (user_id, theme, language) VALUES (%s, %s, %s)",
                (user_id, 'light', 'en')
            )
            
            # Log activity
            log_activity(user_id, 'account_created')
            
            return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
        else:
            return jsonify({'message': 'Failed to create user'}), 500
            
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Find user
        user = db.execute_query(
            "SELECT id, username, email, password_hash FROM users WHERE email = %s",
            (email,)
        )
        
        if not user or not check_password_hash(user[0]['password_hash'], password):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user[0]['id'],
            'exp': datetime.now(timezone.utc) + timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        # Log activity
        log_activity(user[0]['id'], 'login')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user[0]['id'],
                'username': user[0]['username'],
                'email': user[0]['email']
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/mood', methods=['POST'])
@token_required
def save_mood(current_user_id):
    try:
        data = request.get_json()
        mood_score = data.get('mood_score')
        notes = data.get('notes', '')
        
        if not mood_score or mood_score < 1 or mood_score > 5:
            return jsonify({'message': 'Valid mood score (1-5) is required'}), 400
        
        mood_id = db.execute_query(
            "INSERT INTO mood_entries (user_id, mood_score, notes, timestamp) VALUES (%s, %s, %s, %s)",
            (current_user_id, mood_score, notes, datetime.now())
        )
        
        if mood_id:
            # Log activity
            log_activity(current_user_id, 'mood_logged', {'score': mood_score})
            return jsonify({'message': 'Mood entry saved', 'mood_id': mood_id}), 201
        else:
            return jsonify({'message': 'Failed to save mood entry'}), 500
            
    except Exception as e:
        print(f"Mood save error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/mood', methods=['GET'])
@token_required
def get_mood_history(current_user_id):
    try:
        # Get last 30 days of mood entries
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        mood_entries = db.execute_query(
            "SELECT id, mood_score, notes, timestamp FROM mood_entries WHERE user_id = %s AND timestamp >= %s ORDER BY timestamp ASC",
            (current_user_id, thirty_days_ago)
        )
        
        return jsonify({'mood_entries': mood_entries or []}), 200
        
    except Exception as e:
        print(f"Mood history error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/mood/<int:mood_id>', methods=['DELETE'])
@token_required
def delete_mood(current_user_id, mood_id):
    try:
        result = db.execute_query(
            "DELETE FROM mood_entries WHERE id = %s AND user_id = %s",
            (mood_id, current_user_id)
        )
        return jsonify({'message': 'Mood entry deleted successfully'}), 200
    except Exception as e:
        print(f"Mood delete error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/mood/<int:mood_id>', methods=['PUT'])
@token_required
def update_mood(current_user_id, mood_id):
    try:
        data = request.get_json()
        mood_score = data.get('mood_score')
        notes = data.get('notes')
        
        if not mood_score or mood_score < 1 or mood_score > 5:
            return jsonify({'message': 'Valid mood score (1-5) is required'}), 400
            
        db.execute_query(
            "UPDATE mood_entries SET mood_score = %s, notes = %s WHERE id = %s AND user_id = %s",
            (mood_score, notes, mood_id, current_user_id)
        )
        return jsonify({'message': 'Mood entry updated successfully'}), 200
    except Exception as e:
        print(f"Mood update error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/analytics', methods=['GET'])
@token_required
def get_user_analytics(current_user_id):
    try:
        # Get mood analytics
        mood_stats = db.execute_query(
            "SELECT AVG(mood_score) as avg_mood, COUNT(*) as total_entries FROM mood_entries WHERE user_id = %s AND timestamp >= %s",
            (current_user_id, datetime.now() - timedelta(days=30))
        )
        
        # Get mood trend (last 7 days vs previous 7 days)
        last_week = db.execute_query(
            "SELECT AVG(mood_score) as avg_mood FROM mood_entries WHERE user_id = %s AND timestamp >= %s",
            (current_user_id, datetime.now() - timedelta(days=7))
        )
        
        prev_week = db.execute_query(
            "SELECT AVG(mood_score) as avg_mood FROM mood_entries WHERE user_id = %s AND timestamp BETWEEN %s AND %s",
            (current_user_id, datetime.now() - timedelta(days=14), datetime.now() - timedelta(days=7))
        )
        
        analytics = {
            'avg_mood_30_days': round(mood_stats[0]['avg_mood'] or 0, 1),
            'total_entries': mood_stats[0]['total_entries'],
            'mood_trend': {
                'last_week': round(last_week[0]['avg_mood'] or 0, 1),
                'previous_week': round(prev_week[0]['avg_mood'] or 0, 1)
            }
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        print(f"Analytics error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/resources', methods=['GET'])
def get_resources():
    try:
        category = request.args.get('category')
        if category:
            resources = db.execute_query(
                "SELECT * FROM wellness_resources WHERE category = %s AND is_active = TRUE",
                (category,)
            )
        else:
            resources = db.execute_query(
                "SELECT * FROM wellness_resources WHERE is_active = TRUE"
            )
        
        return jsonify({'resources': resources or []}), 200
        
    except Exception as e:
        print(f"Resources error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/preferences', methods=['GET'])
@token_required
def get_preferences(current_user_id):
    try:
        prefs = db.execute_query(
            "SELECT notification_enabled, reminder_time, theme, language FROM user_preferences WHERE user_id = %s",
            (current_user_id,)
        )
        
        if not prefs:
            # Create default if somehow missing
            db.execute_query(
                "INSERT IGNORE INTO user_preferences (user_id) VALUES (%s)",
                (current_user_id,)
            )
            prefs = [{'notification_enabled': 1, 'reminder_time': '09:00:00', 'theme': 'light', 'language': 'en'}]
            
        # Convert time object to string
        if prefs[0]['reminder_time']:
            prefs[0]['reminder_time'] = str(prefs[0]['reminder_time'])
            
        return jsonify(prefs[0]), 200
    except Exception as e:
        print(f"Preferences GET error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/preferences', methods=['PUT'])
@token_required
def update_preferences(current_user_id):
    try:
        data = request.get_json()
        theme = data.get('theme')
        language = data.get('language')
        notif = data.get('notification_enabled')
        reminder = data.get('reminder_time')
        
        # Build dynamic update query
        updates = []
        params = []
        
        if theme:
            updates.append("theme = %s")
            params.append(theme)
        if language:
            updates.append("language = %s")
            params.append(language)
        if notif is not None:
            updates.append("notification_enabled = %s")
            params.append(notif)
        if reminder:
            updates.append("reminder_time = %s")
            params.append(reminder)
            
        if not updates:
            return jsonify({'message': 'No fields to update'}), 400
            
        params.append(current_user_id)
        query = f"UPDATE user_preferences SET {', '.join(updates)} WHERE user_id = %s"
        
        db.execute_query(query, params)
        return jsonify({'message': 'Preferences updated successfully'}), 200
    except Exception as e:
        print(f"Preferences PUT error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/activity', methods=['GET'])
@token_required
def get_user_activity(current_user_id):
    try:
        activities = db.execute_query(
            "SELECT activity_type, activity_data, timestamp FROM user_activity WHERE user_id = %s ORDER BY timestamp DESC LIMIT 10",
            (current_user_id,)
        )
        
        # Ensure timestamp is string for JSON
        if activities:
            for activity in activities:
                activity['timestamp'] = activity['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                if activity['activity_data']:
                    try:
                        activity['activity_data'] = json.loads(activity['activity_data'])
                    except:
                        pass
        
        return jsonify({'activities': activities or []}), 200
    except Exception as e:
        print(f"Activity query error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    # Database connections are now managed per-query
    app.run(debug=True, host='0.0.0.0', port=5000)