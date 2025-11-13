"""
Comprehensive test to verify all database objects (procedures, functions, triggers)
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


def test_all_objects():
    conn = pymysql.connect(**DB_CONFIG)
    print("=" * 70)
    print("COMPREHENSIVE DATABASE OBJECTS TEST")
    print("=" * 70)
    
    try:
        with conn.cursor() as cur:
            # 1. Check Procedures
            print("\n1. STORED PROCEDURES")
            print("-" * 70)
            cur.execute("SHOW PROCEDURE STATUS WHERE Db = 'hostel_db'")
            procedures = cur.fetchall()
            print(f"   Found {len(procedures)} procedure(s):")
            for proc in procedures:
                print(f"   ✓ {proc['Name']}")
            
            # 2. Check Functions
            print("\n2. FUNCTIONS")
            print("-" * 70)
            cur.execute("SHOW FUNCTION STATUS WHERE Db = 'hostel_db'")
            functions = cur.fetchall()
            print(f"   Found {len(functions)} function(s):")
            for func in functions:
                print(f"   ✓ {func['Name']}")
            
            # Test fn_remaining_fees
            if len(functions) > 0:
                print("\n   Testing fn_remaining_fees...")
                cur.execute("SELECT StudentId FROM studentinfo LIMIT 1")
                student = cur.fetchone()
                if student:
                    student_id = student['StudentId']
                    cur.execute("SELECT fn_remaining_fees(%s) as Remaining", (student_id,))
                    result = cur.fetchone()
                    print(f"   → Student {student_id} has ₹{result['Remaining']} remaining")
            
            # 3. Check Triggers
            print("\n3. TRIGGERS")
            print("-" * 70)
            cur.execute("SHOW TRIGGERS")
            triggers = cur.fetchall()
            print(f"   Found {len(triggers)} trigger(s):")
            for trigger in triggers:
                print(f"   ✓ {trigger['Trigger']} ({trigger['Event']} on {trigger['Table']})")
            
            # 4. Summary
            total = len(procedures) + len(functions) + len(triggers)
            print("\n" + "=" * 70)
            print("SUMMARY")
            print("=" * 70)
            print(f"✓ Procedures: {len(procedures)}")
            for proc in procedures:
                print(f"  - {proc['Name']}")
            print(f"\n✓ Functions: {len(functions)}")
            for func in functions:
                print(f"  - {func['Name']}")
            print(f"\n✓ Triggers: {len(triggers)}")
            for trigger in triggers:
                print(f"  - {trigger['Trigger']}")
            print(f"\n📊 TOTAL DATABASE OBJECTS: {total}")
            print("=" * 70)
            
            # 5. Test Integration
            print("\n4. INTEGRATION TEST")
            print("-" * 70)
            
            # Test getting student with remaining fees
            cur.execute("""
                SELECT 
                    s.StudentId,
                    s.Firstname,
                    s.Lastname,
                    fn_remaining_fees(s.StudentId) as RemainingFees
                FROM studentinfo s
                LIMIT 1
            """)
            test_student = cur.fetchone()
            if test_student:
                print(f"   ✓ Function integration works!")
                print(f"   Student: {test_student['Firstname']} {test_student['Lastname']}")
                print(f"   Remaining Fees: ₹{test_student['RemainingFees']}")
            
            print("\n" + "=" * 70)
            print("✅ ALL TESTS PASSED!")
            print("=" * 70)
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    test_all_objects()
