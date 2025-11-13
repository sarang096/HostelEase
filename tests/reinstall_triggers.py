"""
Script to reinstall updated triggers with vacancy validation
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


def reinstall_triggers():
    conn = pymysql.connect(**DB_CONFIG)
    print("=" * 60)
    print("Reinstalling Triggers with Vacancy Validation")
    print("=" * 60)
    
    try:
        with conn.cursor() as cur:
            print("\n1. Dropping existing triggers...")
            cur.execute("DROP TRIGGER IF EXISTS trg_reduce_room_vacancy")
            cur.execute("DROP TRIGGER IF EXISTS trg_increase_room_vacancy")
            print("   ✓ Old triggers dropped")
            
            print("\n2. Creating updated trigger: trg_reduce_room_vacancy...")
            cur.execute("""
                CREATE TRIGGER trg_reduce_room_vacancy
                BEFORE INSERT ON studentinfo
                FOR EACH ROW
                BEGIN
                    DECLARE room_vacancy INT;
                    
                    IF NEW.RoomId IS NOT NULL THEN
                        SELECT Vacancy INTO room_vacancy
                        FROM RoomInfo
                        WHERE RoomNo = NEW.RoomId;
                        
                        IF room_vacancy IS NULL THEN
                            SIGNAL SQLSTATE '45000'
                            SET MESSAGE_TEXT = 'Room does not exist';
                        ELSEIF room_vacancy = 0 THEN
                            SIGNAL SQLSTATE '45000'
                            SET MESSAGE_TEXT = 'Cannot assign student: Room has no vacancy';
                        END IF;
                        
                        UPDATE RoomInfo
                        SET Vacancy = Vacancy - 1
                        WHERE RoomNo = NEW.RoomId;
                    END IF;
                END
            """)
            print("   ✓ trg_reduce_room_vacancy created (BEFORE INSERT with validation)")
            
            print("\n3. Creating trigger: trg_increase_room_vacancy...")
            cur.execute("""
                CREATE TRIGGER trg_increase_room_vacancy
                AFTER DELETE ON studentinfo
                FOR EACH ROW
                BEGIN
                    IF OLD.RoomId IS NOT NULL THEN
                        UPDATE RoomInfo
                        SET Vacancy = Vacancy + 1
                        WHERE RoomNo = OLD.RoomId;
                    END IF;
                END
            """)
            print("   ✓ trg_increase_room_vacancy created (AFTER DELETE)")
            
            print("\n4. Verifying installation...")
            cur.execute("SHOW TRIGGERS")
            triggers = cur.fetchall()
            print(f"   Found {len(triggers)} triggers:")
            for trigger in triggers:
                print(f"   - {trigger[0]} ({trigger[1]} on {trigger[2]})")
            
            print("\n" + "=" * 60)
            print("✓ Triggers successfully reinstalled!")
            print("✓ Vacancy validation is now active")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    reinstall_triggers()
