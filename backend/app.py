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

class AITherapist:
    def __init__(self):
        self.system_prompt = """
        You are MindBot, a compassionate AI mental health companion for the Feel Sync platform. Your role is to:
        1. Provide emotional support and active listening
        2. Offer evidence-based coping strategies
        3. Encourage professional help when needed
        4. Never diagnose or provide medical advice
        5. Be empathetic, non-judgmental, and supportive
        6. Keep responses concise but meaningful
        7. Ask follow-up questions to understand better
        
        Always prioritize user safety and well-being. If someone expresses suicidal thoughts or self-harm, 
        immediately encourage them to contact emergency services or a crisis hotline.
        """
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of user message"""
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity
            
            if sentiment > 0.1:
                return "positive"
            elif sentiment < -0.1:
                return "negative"
            else:
                return "neutral"
        except:
            return "neutral"
    
    def generate_response(self, user_message, conversation_history=None):
        """Generate AI response using OpenAI GPT"""
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    messages.append(msg)
            
            messages.append({"role": "user", "content": user_message})
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"AI response error: {e}")
            # Fallback responses based on sentiment
            sentiment = self.analyze_sentiment(user_message)
            return self.get_fallback_response(sentiment, user_message)
    
    def get_fallback_response(self, sentiment, user_message):
        """Provide fallback responses when AI service is unavailable"""
        user_message_lower = user_message.lower()
        
        # Crisis keywords
        crisis_keywords = ['suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm']
        if any(keyword in user_message_lower for keyword in crisis_keywords):
            return """I'm very concerned about what you're sharing. Please reach out for immediate help:
            
            🚨 Emergency: 911
            📞 Crisis Text Line: Text HOME to 741741
            📞 National Suicide Prevention Lifeline: 988
            
            You matter, and there are people who want to help you."""
        
        # Anxiety/stress keywords
        anxiety_keywords = ['anxious', 'anxiety', 'stressed', 'panic', 'worried', 'overwhelmed']
        if any(keyword in user_message_lower for keyword in anxiety_keywords):
            return """I hear that you're feeling anxious or stressed. Here are some techniques that might help:
            
            🌬️ Try the 4-7-8 breathing technique: Breathe in for 4, hold for 7, exhale for 8
            🧘 Practice grounding: Name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste
            💪 Remember: This feeling is temporary and you have the strength to get through it
            
            What's been causing you the most stress lately?"""
        
        # Depression keywords
        depression_keywords = ['depressed', 'sad', 'hopeless', 'empty', 'worthless', 'lonely']
        if any(keyword in user_message_lower for keyword in depression_keywords):
            return """I'm sorry you're going through such a difficult time. Your feelings are valid, and it's brave of you to reach out.
            
            💙 Remember: You are not alone in this
            🌱 Small steps count - even getting through today is an achievement
            🤝 Consider reaching out to a trusted friend, family member, or mental health professional
            
            What's one small thing that usually brings you even a tiny bit of comfort?"""
        
        # Positive sentiment
        if sentiment == "positive":
            return """I'm glad to hear some positivity in your message! It's wonderful when we can find moments of joy or accomplishment.
            
            ✨ Celebrating these moments, big or small, is so important for our mental health
            🌟 What's been going well for you lately?
            
            How can I support you in maintaining this positive momentum?"""
        
        # Neutral/general response
        return """Thank you for sharing with me. I'm here to listen and support you through whatever you're experiencing.
        
        🤗 Remember that it's okay to not be okay sometimes
        💭 Your thoughts and feelings matter
        🌈 Every day is a new opportunity for growth and healing
        
        What's on your mind today? I'm here to help however I can."""

ai_therapist = MentalHealthAI(os.getenv('OPENAI_API_KEY'))

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
            "SELECT mood_score, notes, timestamp FROM mood_entries WHERE user_id = %s AND timestamp >= %s ORDER BY timestamp ASC",
            (user_id, thirty_days_ago)
        )
        
        return jsonify({'mood_entries': mood_entries or []}), 200
        
    except Exception as e:
        print(f"Mood history error: {e}")
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