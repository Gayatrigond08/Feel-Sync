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
        conversation_history = data.get('history', []) # Added history support
        
        if not user_message:
            return jsonify({'message': 'Message is required'}), 400
            
        # Generate empathetic response using upgraded AI logic
        ai_result = ai_therapist.generate_personalized_response(user_message, conversation_history)
        response_text = ai_result['response']
        
        # Add suggestions if available
        if ai_result.get('suggested_technique'):
            tech = ai_result['suggested_technique']
            response_text += f"\n\n**Suggested Strategy:** {tech['name']}\n{tech['description']}"
            
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
            
        # Generate summary using OpenAI
        prompt = f"Based on these daily reflections, provide a short, supportive summary (2 sentences):\n1. What made me smile: {smile}\n2. Today's challenge: {challenge}\n3. Grateful for: {grateful}"
        
        summary = "Today was a day of reflection and growth. You found joy in the small things and faced challenges with resilience."
        
        if openai.api_key:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a supportive mental wellness assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100
                )
                summary = response.choices[0].message.content.strip()
            except Exception as ai_e:
                print(f"Summary AI error: {ai_e}")

        # Store in database
        db.execute_query(
            """INSERT INTO daily_reflections (user_id, smile_today, challenge_today, grateful_for, summary) 
               VALUES (%s, %s, %s, %s, %s)""",
            (current_user_id, smile, challenge, grateful, summary)
        )
        
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
def save_mood():
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)  # Default for demo
        mood_score = data.get('mood_score')
        notes = data.get('notes', '')
        
        if not mood_score or mood_score < 1 or mood_score > 5:
            return jsonify({'message': 'Valid mood score (1-5) is required'}), 400
        
        mood_id = db.execute_query(
            "INSERT INTO mood_entries (user_id, mood_score, notes, timestamp) VALUES (%s, %s, %s, %s)",
            (user_id, mood_score, notes, datetime.now())
        )
        
        if mood_id:
            return jsonify({'message': 'Mood entry saved', 'mood_id': mood_id}), 201
        else:
            return jsonify({'message': 'Failed to save mood entry'}), 500
            
    except Exception as e:
        print(f"Mood save error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/mood/<int:user_id>', methods=['GET'])
def get_mood_history(user_id):
    try:
        # Get last 30 days of mood entries
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        mood_entries = db.execute_query(
            "SELECT id, mood_score, notes, timestamp FROM mood_entries WHERE user_id = %s AND timestamp >= %s ORDER BY timestamp ASC",
            (user_id, thirty_days_ago)
        )
        
        return jsonify({'mood_entries': mood_entries or []}), 200
        
    except Exception as e:
        print(f"Mood history error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/mood/<int:mood_id>', methods=['DELETE'])
def delete_mood(mood_id):
    try:
        # For demo, we don't check user ownership, but in production we should
        result = db.execute_query(
            "DELETE FROM mood_entries WHERE id = %s",
            (mood_id,)
        )
        return jsonify({'message': 'Mood entry deleted successfully'}), 200
    except Exception as e:
        print(f"Mood delete error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/mood/<int:mood_id>', methods=['PUT'])
def update_mood(mood_id):
    try:
        data = request.get_json()
        mood_score = data.get('mood_score')
        notes = data.get('notes')
        
        if not mood_score or mood_score < 1 or mood_score > 5:
            return jsonify({'message': 'Valid mood score (1-5) is required'}), 400
            
        db.execute_query(
            "UPDATE mood_entries SET mood_score = %s, notes = %s WHERE id = %s",
            (mood_score, notes, mood_id)
        )
        return jsonify({'message': 'Mood entry updated successfully'}), 200
    except Exception as e:
        print(f"Mood update error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    try:
        data = request.get_json()
        user_message = data.get('message')
        user_id = data.get('user_id', 1)  # Default for demo
        
        if not user_message:
            return jsonify({'message': 'Message is required'}), 400
        
        # Get recent conversation history
        conversation_history = db.execute_query(
            "SELECT message_type, content FROM chat_sessions WHERE user_id = %s ORDER BY timestamp DESC LIMIT 10",
            (user_id,)
        )
        
        # Format history for AI
        formatted_history = []
        if conversation_history:
            for msg in reversed(conversation_history):
                role = "user" if msg['message_type'] == 'user' else "assistant"
                formatted_history.append({"role": role, "content": msg['content']})
        
        # Generate AI response
        ai_result = ai_therapist.generate_personalized_response(user_message, formatted_history)
        ai_response = ai_result['response']
        
        # Save conversation to database
        db.execute_query(
            "INSERT INTO chat_sessions (user_id, message_type, content, timestamp) VALUES (%s, %s, %s, %s)",
            (user_id, 'user', user_message, datetime.now())
        )
        
        db.execute_query(
            "INSERT INTO chat_sessions (user_id, message_type, content, timestamp) VALUES (%s, %s, %s, %s)",
            (user_id, 'bot', ai_response, datetime.now())
        )
        
        return jsonify({'response': ai_response}), 200
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/analytics/<int:user_id>', methods=['GET'])
def get_user_analytics(user_id):
    try:
        # Get mood analytics
        mood_stats = db.execute_query(
            "SELECT AVG(mood_score) as avg_mood, COUNT(*) as total_entries FROM mood_entries WHERE user_id = %s AND timestamp >= %s",
            (user_id, datetime.now() - timedelta(days=30))
        )
        
        # Get mood trend (last 7 days vs previous 7 days)
        last_week = db.execute_query(
            "SELECT AVG(mood_score) as avg_mood FROM mood_entries WHERE user_id = %s AND timestamp >= %s",
            (user_id, datetime.now() - timedelta(days=7))
        )
        
        prev_week = db.execute_query(
            "SELECT AVG(mood_score) as avg_mood FROM mood_entries WHERE user_id = %s AND timestamp BETWEEN %s AND %s",
            (user_id, datetime.now() - timedelta(days=14), datetime.now() - timedelta(days=7))
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

if __name__ == '__main__':
    # Database connections are now managed per-query
    app.run(debug=True, host='0.0.0.0', port=5000)