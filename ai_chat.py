import openai
import os
from textblob import TextBlob
import json
import random
from datetime import datetime

class MentalHealthAI:
    """
    Advanced AI Mental Health Support System
    Provides empathetic responses, crisis detection, and therapeutic techniques
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm',
            'want to die', 'better off dead', 'no point living', 'end my life'
        ]
        
        self.anxiety_keywords = [
            'anxious', 'anxiety', 'panic', 'worried', 'stressed', 'overwhelmed',
            'nervous', 'fear', 'scared', 'tension', 'restless'
        ]
        
        self.depression_keywords = [
            'depressed', 'sad', 'hopeless', 'empty', 'worthless', 'lonely',
            'meaningless', 'numb', 'tired', 'exhausted', 'dark'
        ]
        
        self.therapeutic_techniques = {
            'breathing': {
                'name': '4-7-8 Breathing Technique',
                'description': 'Inhale for 4 counts, hold for 7, exhale for 8. Repeat 4 times.',
                'benefits': 'Reduces anxiety and promotes relaxation'
            },
            'grounding': {
                'name': '5-4-3-2-1 Grounding Technique',
                'description': 'Name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste.',
                'benefits': 'Helps with anxiety and panic attacks'
            },
            'progressive_relaxation': {
                'name': 'Progressive Muscle Relaxation',
                'description': 'Tense and relax each muscle group for 5 seconds, starting from toes to head.',
                'benefits': 'Reduces physical tension and stress'
            },
            'mindfulness': {
                'name': 'Mindful Observation',
                'description': 'Focus on one object for 2 minutes, noticing all its details without judgment.',
                'benefits': 'Improves focus and reduces racing thoughts'
            }
        }
    
    def analyze_sentiment(self, text):
        """Analyze emotional sentiment of user input"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.3:
                sentiment = "very_positive"
            elif polarity > 0.1:
                sentiment = "positive"
            elif polarity > -0.1:
                sentiment = "neutral"
            elif polarity > -0.3:
                sentiment = "negative"
            else:
                sentiment = "very_negative"
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': abs(polarity)
            }
        except:
            return {
                'sentiment': 'neutral',
                'polarity': 0,
                'subjectivity': 0,
                'confidence': 0
            }
    
    def detect_crisis(self, text):
        """Detect potential mental health crisis situations"""
        text_lower = text.lower()
        crisis_score = 0
        detected_keywords = []
        
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                crisis_score += 1
                detected_keywords.append(keyword)
        
        # Additional context analysis
        high_risk_phrases = [
            'no one would miss me', 'tired of living', 'can\'t go on',
            'nothing matters', 'permanent solution', 'goodbye forever'
        ]
        
        for phrase in high_risk_phrases:
            if phrase in text_lower:
                crisis_score += 2
                detected_keywords.append(phrase)
        
        return {
            'is_crisis': crisis_score > 0,
            'severity': 'high' if crisis_score >= 3 else 'medium' if crisis_score >= 1 else 'low',
            'score': crisis_score,
            'keywords': detected_keywords
        }
    
    def get_crisis_response(self):
        """Provide immediate crisis intervention response"""
        return """🚨 I'm very concerned about what you're sharing. Your life has value and meaning.

**IMMEDIATE HELP AVAILABLE:**
🆘 Emergency: 911
📞 National Suicide Prevention Lifeline: 988
📱 Crisis Text Line: Text HOME to 741741
🌐 Online Chat: suicidepreventionlifeline.org

**Remember:**
• You are not alone in this
• These feelings can change with proper support
• Many people who felt this way found help and hope
• Professional counselors are trained to help with exactly what you're experiencing

Please reach out to one of these resources right now. They're available 24/7 and want to help you."""
    
    def categorize_mental_health_concern(self, text):
        """Categorize the type of mental health concern"""
        text_lower = text.lower()
        categories = []
        
        # Check for anxiety
        anxiety_count = sum(1 for keyword in self.anxiety_keywords if keyword in text_lower)
        if anxiety_count > 0:
            categories.append(('anxiety', anxiety_count))
        
        # Check for depression
        depression_count = sum(1 for keyword in self.depression_keywords if keyword in text_lower)
        if depression_count > 0:
            categories.append(('depression', depression_count))
        
        # Check for stress
        stress_keywords = ['stress', 'pressure', 'overwhelmed', 'burden', 'exhausted']
        stress_count = sum(1 for keyword in stress_keywords if keyword in text_lower)
        if stress_count > 0:
            categories.append(('stress', stress_count))
        
        # Sort by frequency
        categories.sort(key=lambda x: x[1], reverse=True)
        return [cat[0] for cat in categories]
    
    def suggest_technique(self, categories):
        """Suggest appropriate therapeutic technique based on concerns"""
        if not categories:
            return random.choice(list(self.therapeutic_techniques.values()))
        
        primary_concern = categories[0]
        
        technique_mapping = {
            'anxiety': 'breathing',
            'stress': 'progressive_relaxation',
            'depression': 'mindfulness'
        }
        
        suggested_technique = technique_mapping.get(primary_concern, 'grounding')
        return self.therapeutic_techniques[suggested_technique]
    
    def generate_personalized_response(self, user_message, user_history=None):
        """Generate personalized AI response based on user input and history"""
        
        # Analyze the message
        sentiment_analysis = self.analyze_sentiment(user_message)
        crisis_detection = self.detect_crisis(user_message)
        categories = self.categorize_mental_health_concern(user_message)
        
        # Handle crisis situations immediately
        if crisis_detection['is_crisis']:
            return {
                'response': self.get_crisis_response(),
                'analysis': {
                    'sentiment': sentiment_analysis,
                    'crisis': crisis_detection,
                    'categories': categories
                },
                'suggested_technique': None,
                'priority': 'crisis'
            }
        
        # Try to use OpenAI API if available
        if self.api_key and self.api_key != "your_openai_api_key_here":
            try:
                ai_response = self.get_openai_response(user_message, user_history, sentiment_analysis, categories)
                if ai_response:
                    return {
                        'response': ai_response,
                        'analysis': {
                            'sentiment': sentiment_analysis,
                            'crisis': crisis_detection,
                            'categories': categories
                        },
                        'suggested_technique': self.suggest_technique(categories),
                        'priority': 'normal'
                    }
            except Exception as e:
                print(f"OpenAI API error: {e}")
        
        # Fallback to rule-based responses
        fallback_response = self.get_fallback_response(user_message, sentiment_analysis, categories)
        
        return {
            'response': fallback_response,
            'analysis': {
                'sentiment': sentiment_analysis,
                'crisis': crisis_detection,
                'categories': categories
            },
            'suggested_technique': self.suggest_technique(categories),
            'priority': 'normal'
        }
    
    def get_openai_response(self, user_message, user_history, sentiment_analysis, categories):
        """Get response from OpenAI GPT model"""
        try:
            # Build context-aware system prompt
            system_prompt = f"""You are MindBot, a compassionate AI mental health companion. 

Current user sentiment: {sentiment_analysis['sentiment']}
Detected concerns: {', '.join(categories) if categories else 'general support'}

Guidelines:
1. Be empathetic, warm, and non-judgmental
2. Provide emotional support and validation
3. Suggest practical coping strategies when appropriate
4. Encourage professional help for serious concerns
5. Keep responses concise but meaningful (2-3 paragraphs max)
6. Never diagnose or provide medical advice
7. Ask follow-up questions to understand better
8. Use emojis sparingly but appropriately

Respond as a caring mental health companion would."""

            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent conversation history
            if user_history:
                for msg in user_history[-4:]:  # Last 4 messages for context
                    messages.append(msg)
            
            messages.append({"role": "user", "content": user_message})
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=250,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
    
    def get_fallback_response(self, user_message, sentiment_analysis, categories):
        """Generate rule-based response when AI service is unavailable"""
        user_message_lower = user_message.lower()
        sentiment = sentiment_analysis['sentiment']
        
        # Anxiety-focused responses
        if 'anxiety' in categories:
            responses = [
                """I can hear the anxiety in your message, and I want you to know that what you're feeling is valid. Anxiety can be overwhelming, but there are ways to manage it.

🌬️ Try this right now: Take a slow, deep breath in for 4 counts, hold it for 4, then exhale for 6. This can help activate your body's relaxation response.

What specific situation or thought is contributing most to your anxiety right now?""",
                
                """Anxiety has a way of making everything feel urgent and overwhelming. You're not alone in feeling this way, and it's okay to take things one moment at a time.

🧘 Here's a grounding technique: Look around and name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.

Remember, anxiety is temporary. What usually helps you feel more grounded?"""
            ]
            return random.choice(responses)
        
        # Depression-focused responses
        elif 'depression' in categories:
            responses = [
                """I hear the heaviness in your words, and I want you to know that reaching out here shows incredible strength. Depression can make everything feel dark, but you don't have to face this alone.

💙 Your feelings are valid, and it's okay to not be okay right now. Even small steps forward count as progress.

What's one tiny thing that used to bring you even a moment of comfort? Sometimes reconnecting with small joys can be a starting point.""",
                
                """Thank you for sharing something so difficult with me. Depression can make it feel like there's no way forward, but please know that these feelings can change with proper support.

🌱 You matter, and your life has value even when it doesn't feel that way. Consider reaching out to a mental health professional who can provide the support you deserve.

Is there anyone in your life you feel comfortable talking to about how you're feeling?"""
            ]
            return random.choice(responses)
        
        # Stress-focused responses
        elif 'stress' in categories:
            responses = [
                """It sounds like you're carrying a heavy load right now. Stress can feel overwhelming, but acknowledging it like you just did is an important first step.

💪 Remember: You don't have to handle everything at once. It's okay to prioritize and take breaks.

What's the biggest source of stress for you right now? Sometimes talking through it can help us see new perspectives.""",
                
                """I can sense the pressure you're under. Stress affects all of us, and it's completely normal to feel overwhelmed sometimes.

🌿 Try this: Take 5 minutes to step away from whatever is stressing you. Focus only on your breathing. This isn't avoiding the problem—it's giving your mind space to reset.

What would feel most helpful to you right now—talking through the situation or learning some stress management techniques?"""
            ]
            return random.choice(responses)
        
        # Positive sentiment responses
        elif sentiment in ['positive', 'very_positive']:
            responses = [
                """I'm so glad to hear some positivity in your message! It's wonderful when we can find moments of joy or accomplishment, especially when we're working on our mental health.

✨ Celebrating these positive moments, no matter how small, is so important. They remind us that good feelings are possible and worth working toward.

What's been going well for you lately? I'd love to hear more about what's bringing you joy.""",
                
                """Your positive energy comes through in your message, and it's beautiful to witness! These moments of lightness are precious and worth acknowledging.

🌟 How does it feel to experience this positivity? Sometimes reflecting on what contributes to our good moments can help us cultivate more of them.

What would you like to focus on to maintain this positive momentum?"""
            ]
            return random.choice(responses)
        
        # General supportive responses
        else:
            responses = [
                """Thank you for reaching out and sharing with me. I'm here to listen and support you through whatever you're experiencing.

🤗 It takes courage to talk about our mental health, and I want you to know that your thoughts and feelings matter.

What's on your mind today? Whether it's something specific or just a general feeling, I'm here to help however I can.""",
                
                """I appreciate you taking the time to connect here. Mental health is so important, and it's wonderful that you're being proactive about your wellbeing.

💭 Remember that it's completely normal to have ups and downs. Every day is a new opportunity for growth, healing, and self-compassion.

How are you feeling right now, and what kind of support would be most helpful to you today?""",
                
                """Hello! I'm glad you're here. Whether you're having a good day or a challenging one, this is a safe space to share whatever is on your mind.

🌈 Your mental health journey is unique to you, and there's no right or wrong way to feel. I'm here to provide support, encouragement, and practical strategies.

What would you like to talk about today? I'm listening with care and without judgment."""
            ]
            return random.choice(responses)

# Example usage and testing
if __name__ == "__main__":
    # Initialize the AI system
    ai = MentalHealthAI()
    
    # Test messages
    test_messages = [
        "I'm feeling really anxious about my job interview tomorrow",
        "I've been feeling so sad and empty lately, like nothing matters",
        "I'm so stressed with all these deadlines at work",
        "I had a great day today! Finally finished my project",
        "I don't see the point in anything anymore, maybe everyone would be better off without me"
    ]
    
    print("=== Mental Health AI Testing ===\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: {message}")
        response = ai.generate_personalized_response(message)
        print(f"Response: {response['response']}")
        print(f"Analysis: {response['analysis']}")
        print(f"Priority: {response['priority']}")
        if response['suggested_technique']:
            technique = response['suggested_technique']
            print(f"Suggested Technique: {technique['name']} - {technique['description']}")
        print("-" * 80)