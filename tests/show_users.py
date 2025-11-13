import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

try:
    # Connect to database
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'hostel_db'),
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print("Fetching ALL users from login table...\n")
    
    # Get all users
    with conn.cursor() as cur:
        cur.execute('SELECT id, username, password, role FROM login')
        users = cur.fetchall()
        
        print(f"Total users: {len(users)}\n")
        print("ID | Username       | Password       | Role")
        print("-" * 60)
        for user in users:
            print(f"{user['id']:2} | {user['username']:14} | {user['password']:14} | {user['role']}")
            
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
