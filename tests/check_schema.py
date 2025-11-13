import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'hostel_db'),
        cursorclass=pymysql.cursors.DictCursor
    )
    
    with conn.cursor() as cur:
        # Check blockinfo table structure
        cur.execute("DESCRIBE blockinfo")
        print("blockinfo table columns:")
        for row in cur.fetchall():
            print(f"  - {row['Field']} ({row['Type']})")
        
        print("\nSample data from blockinfo:")
        cur.execute("SELECT * FROM blockinfo LIMIT 3")
        for row in cur.fetchall():
            print(f"  {row}")
            
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
