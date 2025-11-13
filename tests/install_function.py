"""
Script to install the fn_remaining_fees function
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '@AMS2trps'),
    'database': os.environ.get('DB_NAME', 'hostel_db'),
    'autocommit': True,
}


def install_function():
    conn = pymysql.connect(**DB_CONFIG)
    print("=" * 60)
    print("Installing fn_remaining_fees Function")
    print("=" * 60)
    
    try:
        with conn.cursor() as cur:
            print("\n1. Dropping existing function if exists...")
            cur.execute("DROP FUNCTION IF EXISTS fn_remaining_fees")
            print("   ✓ Old function dropped")
            
            print("\n2. Creating fn_remaining_fees function...")
            cur.execute("""
                CREATE FUNCTION fn_remaining_fees(p_student_id INT)
                RETURNS DECIMAL(10,2)
                DETERMINISTIC
                READS SQL DATA
                BEGIN
                    DECLARE total_fees DECIMAL(10,2) DEFAULT 50000.00;
                    DECLARE fees_paid DECIMAL(10,2) DEFAULT 0.00;
                    DECLARE remaining DECIMAL(10,2);
                    DECLARE column_exists INT DEFAULT 0;
                    
                    SELECT COUNT(*) INTO column_exists
                    FROM information_schema.columns
                    WHERE table_schema = 'hostel_db'
                    AND table_name = 'FeesInfo'
                    AND column_name = 'FeesPaid';
                    
                    IF column_exists > 0 THEN
                        SELECT COALESCE(FeesPaid, 0) INTO fees_paid
                        FROM FeesInfo
                        WHERE StudentId = p_student_id;
                    ELSE
                        SELECT COALESCE(Amount, 0) INTO fees_paid
                        FROM FeesInfo
                        WHERE StudentId = p_student_id;
                    END IF;
                    
                    SET remaining = total_fees - fees_paid;
                    
                    IF remaining < 0 THEN
                        RETURN 0;
                    ELSE
                        RETURN remaining;
                    END IF;
                END
            """)
            print("   ✓ fn_remaining_fees created")
            
            print("\n3. Verifying installation...")
            cur.execute("SHOW FUNCTION STATUS WHERE Db = 'hostel_db'")
            functions = cur.fetchall()
            print(f"   Found {len(functions)} function(s):")
            for func in functions:
                print(f"   - {func[1]} ({func[2]})")
            
            print("\n4. Testing function...")
            # Test with a sample student ID
            cur.execute("SELECT fn_remaining_fees(1) as Remaining")
            result = cur.fetchone()
            if result:
                print(f"   ✓ Function works! Test result: ₹{result[0]}")
            
            print("\n" + "=" * 60)
            print("✓ Function successfully installed!")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    install_function()
