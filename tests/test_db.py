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
    
    print("✓ Database connection successful!")
    
    # Test login table
    with conn.cursor() as cur:
        cur.execute('SELECT COUNT(*) as count FROM login')
        count = cur.fetchone()['count']
        print(f"✓ Login records found: {count}")
        
        if count > 0:
            cur.execute('SELECT username, role FROM login LIMIT 5')
            print("\nSample users:")
            for row in cur.fetchall():
                print(f"  - Username: {row['username']}, Role: {row['role']}")
        else:
            print("\n⚠ No users found in login table!")
            
    conn.close()
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
