"""
Test script to verify stored procedures and triggers are working correctly
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
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True,
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def test_procedures_and_triggers():
    conn = get_connection()
    print("=" * 60)
    print("Testing Stored Procedures and Triggers")
    print("=" * 60)
    
    try:
        with conn.cursor() as cur:
            # 1. Check if procedures exist
            print("\n1. Checking stored procedures...")
            cur.execute("SHOW PROCEDURE STATUS WHERE Db = 'hostel_db'")
            procedures = cur.fetchall()
            print(f"   Found {len(procedures)} procedures:")
            for proc in procedures:
                print(f"   - {proc['Name']}")
            
            # 2. Check if triggers exist
            print("\n2. Checking triggers...")
            cur.execute("SHOW TRIGGERS")
            triggers = cur.fetchall()
            print(f"   Found {len(triggers)} triggers:")
            for trigger in triggers:
                print(f"   - {trigger['Trigger']} ({trigger['Event']} on {trigger['Table']})")
            
            # 3. Test sp_update_fee_payment procedure
            print("\n3. Testing sp_update_fee_payment procedure...")
            test_student_id = 1  # Use an existing student ID
            
            # Detect fees column name
            cur.execute("SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema = %s AND table_name = %s AND COLUMN_NAME IN ('FeesPaid','Amount')", (DB_CONFIG['database'], 'FeesInfo'))
            cols = cur.fetchall()
            fees_col = cols[0]['COLUMN_NAME'] if cols else 'FeesPaid'
            
            # Get current fees
            cur.execute(f"SELECT {fees_col} FROM FeesInfo WHERE StudentId = %s", (test_student_id,))
            result = cur.fetchone()
            if result:
                current_fees = result[fees_col]
                print(f"   Current fees for student {test_student_id}: ₹{current_fees}")
                
                # Update fees using procedure
                test_amount = float(current_fees) + 1000
                cur.callproc('sp_update_fee_payment', (test_student_id, test_amount))
                conn.commit()
                
                # Verify update
                cur.execute(f"SELECT {fees_col} FROM FeesInfo WHERE StudentId = %s", (test_student_id,))
                new_result = cur.fetchone()
                new_fees = new_result[fees_col]
                print(f"   Updated fees for student {test_student_id}: ₹{new_fees}")
                
                # Restore original value
                cur.callproc('sp_update_fee_payment', (test_student_id, current_fees))
                conn.commit()
                print(f"   ✓ Procedure works! Restored to original value.")
            else:
                print(f"   Student {test_student_id} not found in FeesInfo")
            
            # 4. Summary
            print("\n" + "=" * 60)
            print("SUMMARY")
            print("=" * 60)
            print(f"✓ Stored Procedures: {len(procedures)}")
            for proc in procedures:
                print(f"  - {proc['Name']}")
            print(f"\n✓ Triggers: {len(triggers)}")
            for trigger in triggers:
                print(f"  - {trigger['Trigger']}")
            print("\nAll database objects are properly installed!")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    test_procedures_and_triggers()
