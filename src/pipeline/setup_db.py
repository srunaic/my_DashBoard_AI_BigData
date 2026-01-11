import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_PORT = int(os.getenv("DB_PORT", 3306))

def setup_database():
    print("Connecting to MySQL server...")
    try:
        # Connect to MySQL Server (no DB selected yet)
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        # Read schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), '../../schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Execute statements
        print("Executing schema.sql...")
        # Simple split by semicolon. NOTE: This might break if semicolons are in strings.
        # But for our schema.sql, it's fine.
        statements = sql_script.split(';')
        
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                    print("Executed statement.")
                except mysql.connector.Error as err:
                    print(f"Error executing statement: {err}")
                    
        conn.commit()
        cursor.close()
        conn.close()
        print("Database setup completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    setup_database()
