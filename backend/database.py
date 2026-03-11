import mysql.connector
from mysql.connector import Error
import os

class DatabaseSetup:
    def __init__(self):
        # Load configuration from environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        self.connection = None
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', 3307))
        }
    
    def connect_to_mysql(self):
        """Connect to MySQL server (without specific database)"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("Successfully connected to MySQL server")
            return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def create_database(self):
        """Create the feel_sync_db database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS feel_sync_db")
            cursor.execute("USE feel_sync_db")
            print("Database 'feel_sync_db' created/selected successfully")
            cursor.close()
            return True
        except Error as e:
            print(f"Error creating database: {e}")
            return False
    
    def create_tables(self):
        """Create all necessary tables for the Feel Sync application"""
        try:
            cursor = self.connection.cursor()
            
            # Users table
            users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_username (username)
            )
            """
            
            # Mood entries table
            mood_entries_table = """
            CREATE TABLE IF NOT EXISTS mood_entries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                mood_score INT NOT NULL CHECK (mood_score BETWEEN 1 AND 5),
                notes TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_timestamp (user_id, timestamp),
                INDEX idx_timestamp (timestamp)
            )
            """
            
            # Chat sessions table
            chat_sessions_table = """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                message_type ENUM('user', 'bot') NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sentiment VARCHAR(20) DEFAULT 'neutral',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_timestamp (user_id, timestamp),
                INDEX idx_timestamp (timestamp)
            )
            """
            
            # User preferences table
            user_preferences_table = """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                notification_enabled BOOLEAN DEFAULT TRUE,
                reminder_time TIME DEFAULT '09:00:00',
                theme VARCHAR(20) DEFAULT 'light',
                language VARCHAR(10) DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_prefs (user_id)
            )
            """
            
            # Wellness resources table
            wellness_resources_table = """
            CREATE TABLE IF NOT EXISTS wellness_resources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(50) NOT NULL,
                content_url VARCHAR(500),
                content_text TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_category (category),
                INDEX idx_active (is_active)
            )
            """
            
            # User activity log table
            user_activity_table = """
            CREATE TABLE IF NOT EXISTS user_activity (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                activity_type VARCHAR(50) NOT NULL,
                activity_data JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_activity (user_id, activity_type),
                INDEX idx_timestamp (timestamp)
            )
            """
            
            # Daily reflections table
            daily_reflections_table = """
            CREATE TABLE IF NOT EXISTS daily_reflections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                smile_today TEXT,
                challenge_today TEXT,
                grateful_for TEXT,
                summary TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_timestamp (user_id, timestamp)
            )
            """
            
            # Execute table creation queries
            tables = [
                ("users", users_table),
                ("mood_entries", mood_entries_table),
                ("chat_sessions", chat_sessions_table),
                ("user_preferences", user_preferences_table),
                ("wellness_resources", wellness_resources_table),
                ("user_activity", user_activity_table),
                ("daily_reflections", daily_reflections_table)
            ]
            
            # Drop wellness_resources to fix ENUM to VARCHAR transition
            cursor.execute("DROP TABLE IF EXISTS wellness_resources")
            
            for table_name, query in tables:
                cursor.execute(query)
                print(f"Table '{table_name}' created successfully")
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error creating tables: {e}")
            return False
    
    def insert_sample_data(self):
        """Insert sample wellness resources and demo data"""
        try:
            cursor = self.connection.cursor()
            
            # Ensure wellness_resources category can handle new options
            try:
                cursor.execute("ALTER TABLE wellness_resources MODIFY category VARCHAR(50) NOT NULL")
            except Error as e:
                # Ignore if it fails (e.g. column already changed or table doesn't exist yet)
                pass

            # Sample wellness resources
            wellness_resources = [
                ("Deep Breathing Space", "Follow the expanding circle to find your inner calm with the 4-7-8 method.", "meditation", 
                 "internal:breathing-app", "Focus on your breath. Inhale for 4 counts, hold for 4, exhale for 6."),
                
                ("Zen Garden Bubble Pop", "Pop the floating bubbles to discover positive affirmations and calm your mind.", "game",
                 "internal:game-app", "A playful way to release stress and find positive thoughts."),
                
                ("Creative Wellness Journal", "Express your thoughts with creative prompts and mood stickers.", "journal",
                 "internal:creative-journal", "A safe space for your daily reflections and creative expression."),
                
                ("Soul Whispers", "Receive comforting lyrics, empowering facts, and motivational thoughts.", "knowledge",
                 "internal:empower-app", "Daily wisdom for a stronger, more confident mind.")
            ]
            
            # Clear existing resources to avoid duplicates or old data
            cursor.execute("DELETE FROM wellness_resources")
            
            insert_resources_query = """
            INSERT INTO wellness_resources (title, description, category, content_url, content_text)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_resources_query, wellness_resources)
            
            # Create a demo user (optional)
            demo_user_query = """
            INSERT INTO users (username, email, password_hash) 
            VALUES ('demo_user', 'demo@feelsync.com', 'pbkdf2:sha256:600000$hbYELeopkXJ6d2eO$03bc97a9f6d4d49a3770387b32064161823eb55775ea70806134426e8fde7b40f1825f65')
            ON DUPLICATE KEY UPDATE username=username
            """
            cursor.execute(demo_user_query)
            
            self.connection.commit()
            print("Feel Sync data handles initialized successfully")
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error inserting sample data: {e}")
            return False
    
    def setup_database(self):
        """Complete database setup process"""
        print("Starting Feel Sync database setup...")
        
        if not self.connect_to_mysql():
            return False
        
        if not self.create_database():
            return False
        
        if not self.create_tables():
            return False
        
        if not self.insert_sample_data():
            return False
        
        print("Database setup completed successfully!")
        return True
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

def main():
    """Run database setup"""
    db_setup = DatabaseSetup()
    
    try:
        success = db_setup.setup_database()
        if success:
            print("\n✅ Feel Sync database is ready!")
            print("You can now run the Flask application with: python app.py")
        else:
            print("\n❌ Database setup failed. Please check the error messages above.")
    
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
    
    finally:
        db_setup.close_connection()

if __name__ == "__main__":
    main()