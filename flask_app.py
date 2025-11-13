from flask import Flask, request, session, jsonify, send_from_directory
from flask_session import Session
from flask_cors import CORS
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET', 'hostel-secret')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_FILE_DIR'] = os.path.join(BASE_DIR, 'flask_session')
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
Session(app)
CORS(app, supports_credentials=True, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

# DB connection settings - prefer environment variables
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '@AMS2trps'),
    'database': os.environ.get('DB_NAME', 'hostel_db'),
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': True,
}


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


def query(sql, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()


def detect_fees_column():
    # return the column name to use for fees in FeesInfo (prefer FeesPaid, fall back to Amount)
    try:
        cols = query("SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema = %s AND table_name = %s AND COLUMN_NAME IN ('FeesPaid','Amount')", (DB_CONFIG['database'], 'FeesInfo'))
        if cols:
            return cols[0].get('COLUMN_NAME')
    except Exception:
        pass
    return None


def execute(sql, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.lastrowid
    finally:
        conn.close()


def call_procedure(proc_name, params=None):
    """Call a stored procedure"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.callproc(proc_name, params or ())
            conn.commit()
    finally:
        conn.close()


@app.route('/')
def index():
    return send_from_directory(PUBLIC_DIR, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    # Serve frontend static files
    if os.path.exists(os.path.join(PUBLIC_DIR, path)):
        return send_from_directory(PUBLIC_DIR, path)
    return send_from_directory(PUBLIC_DIR, 'index.html')


# Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    print(f"[LOGIN] Attempt with username: {username}")
    
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    rows = query('SELECT * FROM login WHERE username = %s AND password = %s', (username, password))
    if not rows:
        print(f"[LOGIN] Invalid credentials for: {username}")
        return jsonify({'error': 'Invalid credentials'}), 401

    user = rows[0]
    session['user'] = {'id': user.get('id'), 'username': user.get('username'), 'role': user.get('role')}
    session.modified = True  # Force session save
    print(f"[LOGIN] Success! User: {username}, Role: {user.get('role')}, Session ID: {session.get('_id', 'unknown')}")
    print(f"[LOGIN] Session data: {session.get('user')}")
    
    response = jsonify({'role': user.get('role'), 'id': user.get('id')})
    return response


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})


@app.route('/api/current-user')
def current_user():
    print(f"[CURRENT-USER] Checking session...")
    print(f"[CURRENT-USER] Session keys: {list(session.keys())}")
    print(f"[CURRENT-USER] Session user: {session.get('user', 'NOT FOUND')}")
    print(f"[CURRENT-USER] Cookie: {request.cookies.get(app.config.get('SESSION_COOKIE_NAME', 'session'))}")
    
    if 'user' not in session:
        print(f"[CURRENT-USER] No user in session - returning 401")
        return jsonify({'error': 'Not logged in'}), 401
    
    print(f"[CURRENT-USER] User found: {session['user']}")
    return jsonify(session['user'])


@app.route('/api/student-profile')
def student_profile():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if session['user'].get('role') != 'student':
        return jsonify({'error': 'Forbidden'}), 403
    student_id = session['user'].get('id')
    
    # Get student info
    rows = query('SELECT * FROM studentinfo WHERE StudentId = %s', (student_id,))
    
    if not rows:
        return jsonify({'error': 'Profile not found'}), 404
    
    student_data = rows[0]
    print(f"[PROFILE] Student data: RoomId={student_data.get('RoomId')}, StHostelId={student_data.get('StHostelId')}")
    
    # Get block name/type if hostel is assigned
    if student_data.get('StHostelId'):
        try:
            block_rows = query('SELECT * FROM blockinfo WHERE HostelId = %s', (student_data.get('StHostelId'),))
            print(f"[PROFILE] Block rows: {block_rows}")
            if block_rows:
                block_data = block_rows[0]
                print(f"[PROFILE] Block data keys: {list(block_data.keys())}")
                # Use 'Type' column as block name if BlockName doesn't exist
                block_name = (block_data.get('BlockName') or block_data.get('Block_Name') or 
                             block_data.get('Blockname') or block_data.get('block_name') or 
                             block_data.get('Type'))
                print(f"[PROFILE] Block name found: {block_name}")
                student_data['BlockName'] = block_name if block_name else 'Not assigned'
            else:
                student_data['BlockName'] = 'Not assigned'
        except Exception as e:
            print(f"[PROFILE] Block error: {e}")
            student_data['BlockName'] = 'Not assigned'
    else:
        student_data['BlockName'] = 'Not assigned'
    
    # Get room number if room is assigned
    if student_data.get('RoomId'):
        try:
            # First, get the column name used for room identifier in roominfo
            room_rows = query('SELECT * FROM roominfo LIMIT 1')
            if room_rows:
                room_columns = list(room_rows[0].keys())
                print(f"[PROFILE] Room table columns: {room_columns}")
                
                # Find the correct column name for room ID
                room_id_col = None
                for col in ['Room_id', 'room_id', 'Roomid', 'roomid', 'RoomID']:
                    if col in room_columns:
                        room_id_col = col
                        break
                
                if room_id_col:
                    room_rows = query(f'SELECT * FROM roominfo WHERE {room_id_col} = %s', (student_data.get('RoomId'),))
                else:
                    # If no match, try with the student's RoomId value as room number
                    room_rows = query('SELECT * FROM roominfo WHERE RoomNo = %s', (student_data.get('RoomId'),))
                
                print(f"[PROFILE] Room rows: {room_rows}")
                if room_rows:
                    room_data = room_rows[0]
                    print(f"[PROFILE] Room data keys: {list(room_data.keys())}")
                    room_no = (room_data.get('RoomNo') or room_data.get('Room_No') or 
                              room_data.get('Roomno') or room_data.get('room_no') or 
                              str(student_data.get('RoomId')))
                    print(f"[PROFILE] Room number found: {room_no}")
                    student_data['RoomNo'] = room_no if room_no else 'Not assigned'
                else:
                    # Use RoomId value directly as room number
                    student_data['RoomNo'] = str(student_data.get('RoomId'))
            else:
                student_data['RoomNo'] = str(student_data.get('RoomId'))
        except Exception as e:
            print(f"[PROFILE] Room error: {e}")
            # Fallback: use RoomId value as room number
            student_data['RoomNo'] = str(student_data.get('RoomId'))
    else:
        student_data['RoomNo'] = 'Not assigned'
    
    print(f"[PROFILE] Final data - RoomNo: {student_data.get('RoomNo')}, BlockName: {student_data.get('BlockName')}")
    return jsonify(student_data)


@app.route('/api/student-fees')
def student_fees():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if session['user'].get('role') != 'student':
        return jsonify({'error': 'Forbidden'}), 403
    student_id = session['user'].get('id')
    
    # Get student info
    student_info = query('SELECT * FROM studentinfo WHERE StudentId = %s', (student_id,))
    if not student_info:
        return jsonify({'error': 'Student not found'}), 404
    
    student = student_info[0]
        
    # Get fees info using the database function fn_remaining_fees
    fees_col = detect_fees_column()
    if not fees_col:
        feesPaid = 0
        feesRemaining = 50000
    else:
        rows = query(f'SELECT {fees_col}, fn_remaining_fees(%s) as FeesRemaining FROM FeesInfo WHERE StudentId = %s', (student_id, student_id))
        if rows:
            feesPaid = rows[0].get(fees_col, 0)
            feesRemaining = rows[0].get('FeesRemaining', 50000)
        else:
            feesPaid = 0
            feesRemaining = 50000
    try:
        feesPaid = float(feesPaid) if feesPaid is not None else 0
        feesRemaining = float(feesRemaining) if feesRemaining is not None else 50000
    except Exception:
        feesPaid = 0
        feesRemaining = 50000

    # Get room info - use same logic as student_profile
    room_no = None
    if student.get('RoomId'):
        try:
            # Try to get room info, but if column doesn't exist, use RoomId directly
            room_rows = query('SELECT * FROM roominfo LIMIT 1')
            if room_rows:
                room_columns = list(room_rows[0].keys())
                room_id_col = None
                for col in ['Room_id', 'room_id', 'Roomid', 'roomid', 'RoomID']:
                    if col in room_columns:
                        room_id_col = col
                        break
                
                if room_id_col:
                    room_info = query(f'SELECT * FROM roominfo WHERE {room_id_col} = %s', (student.get('RoomId'),))
                else:
                    room_info = query('SELECT * FROM roominfo WHERE RoomNo = %s', (student.get('RoomId'),))
                
                if room_info:
                    room_data = room_info[0]
                    room_no = (room_data.get('RoomNo') or room_data.get('Room_No') or 
                              room_data.get('Roomno') or str(student.get('RoomId')))
                else:
                    room_no = str(student.get('RoomId'))
            else:
                room_no = str(student.get('RoomId'))
        except:
            room_no = str(student.get('RoomId'))
    
    # Get block name - use Type column if BlockName doesn't exist
    block_name = None
    if student.get('StHostelId'):
        try:
            block_info = query('SELECT * FROM blockinfo WHERE HostelId = %s', (student.get('StHostelId'),))
            if block_info:
                block_data = block_info[0]
                block_name = (block_data.get('BlockName') or block_data.get('Block_Name') or 
                             block_data.get('Blockname') or block_data.get('Type'))
        except:
            pass

    return jsonify({
        'FeesPaid': feesPaid,
        'FeesRemaining': feesRemaining,  # Using fn_remaining_fees function result
        'RoomNo': room_no,
        'BlockName': block_name
    })


@app.route('/api/FeesInfo')
def api_feesinfo():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if session['user'].get('role') != 'manager':
        return jsonify({'error': 'Forbidden'}), 403
    fees_col = detect_fees_column() or 'FeesPaid'
    rows = query(f'''
        SELECT f.StudentId, COALESCE(f.{fees_col}, 0) AS FeesPaid, s.Firstname, s.Lastname
        FROM FeesInfo f
        LEFT JOIN studentinfo s ON f.StudentId = s.StudentId
    ''')
    return jsonify(rows)


@app.route('/api/student-password', methods=['PUT', 'POST'])
def student_password():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if session['user'].get('role') != 'student':
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json() or {}
    new_password = data.get('newPassword')
    if not new_password:
        return jsonify({'error': 'New password required'}), 400
    user_id = session['user'].get('id')
    execute('UPDATE login SET password = %s WHERE id = %s', (new_password, user_id))
    execute('UPDATE studentinfo SET Password = %s WHERE StudentId = %s', (new_password, user_id))
    return jsonify({'message': 'Password updated successfully'})


@app.route('/api/studentinfo', methods=['GET'])
def get_studentinfo():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if session['user'].get('role') != 'manager':
        return jsonify({'error': 'Forbidden'}), 403
    fees_col = detect_fees_column() or 'FeesPaid'
    rows = query(f'''
        SELECT s.*, f.{fees_col} as FeesPaid
        FROM studentinfo s
        LEFT JOIN FeesInfo f ON s.StudentId = f.StudentId
    ''')
    return jsonify(rows)


@app.route('/api/studentinfo/<int:student_id>', methods=['PUT'])
def update_studentinfo(student_id):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if session['user'].get('role') != 'manager':
        return jsonify({'error': 'Forbidden'}), 403
    updates = request.get_json() or {}
    if not updates:
        return jsonify({'message': 'No updates provided'}), 400
    
    try:
        # If updating RoomId, check for room vacancy
        if 'RoomId' in updates and updates['RoomId'] is not None:
            # Get current room
            current = query('SELECT RoomId FROM studentinfo WHERE StudentId = %s', (student_id,))
            if current and current[0].get('RoomId') != updates['RoomId']:
                # Check new room vacancy
                room_check = query('SELECT Vacancy FROM RoomInfo WHERE RoomNo = %s', (updates['RoomId'],))
                if not room_check:
                    return jsonify({'error': 'Room does not exist'}), 400
                if room_check[0].get('Vacancy', 0) <= 0:
                    return jsonify({'error': 'Cannot assign student: Room has no vacancy'}), 400
        
        fields = ', '.join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [student_id]
        sql = f'UPDATE studentinfo SET {fields} WHERE StudentId = %s'
        execute(sql, tuple(values))
        return jsonify({'message': 'Updated'})
    except pymysql.err.OperationalError as e:
        if 'Room has no vacancy' in str(e) or 'Room does not exist' in str(e):
            return jsonify({'error': str(e).split(': ')[-1] if ': ' in str(e) else str(e)}), 400
        raise


@app.route('/api/studentinfo/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if session['user'].get('role') != 'manager':
        return jsonify({'error': 'Forbidden'}), 403

    rows = query('SELECT MessId, StHostelId FROM studentinfo WHERE StudentId = %s', (student_id,))
    if not rows:
        return jsonify({'error': 'Student not found'}), 404
    student = rows[0]
    
    # Use fn_remaining_fees function to check if fees are paid
    remaining_rows = query('SELECT fn_remaining_fees(%s) as Remaining', (student_id,))
    remaining = float(remaining_rows[0].get('Remaining', 50000)) if remaining_rows else 50000
    
    if remaining > 0:
        return jsonify({'error': f'Cannot delete student with unpaid fees. Remaining: ₹{remaining}'}), 400

    # Update mess and block vacancy manually (no triggers for these)
    if student.get('MessId'):
        execute('UPDATE messinfo SET Vacancy = Vacancy + 1 WHERE MessId = %s', (student.get('MessId'),))
    if student.get('StHostelId'):
        execute('UPDATE blockinfo SET Vacancy = Vacancy + 1 WHERE HostelId = %s', (student.get('StHostelId'),))

    # Delete student records
    # Note: Room vacancy will be automatically increased by trg_increase_room_vacancy trigger
    execute('DELETE FROM FeesInfo WHERE StudentId = %s', (student_id,))
    execute('DELETE FROM login WHERE id = %s', (student_id,))
    execute('DELETE FROM studentinfo WHERE StudentId = %s', (student_id,))
    return jsonify({'message': 'Student deleted'})


@app.route('/api/studentinfo', methods=['POST'])
def add_student():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if session['user'].get('role') != 'manager':
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json() or {}
    username = data.pop('username', None)
    
    try:
        # Insert into studentinfo
        # Note: trg_reduce_room_vacancy trigger will validate room vacancy and raise error if room is full
        fields = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = tuple(data.values())
        sql = f'INSERT INTO studentinfo ({fields}) VALUES ({placeholders})'
        student_id = execute(sql, values)

        # Add FeesInfo using stored procedure
        call_procedure('sp_update_fee_payment', (student_id, 0))

        # Update mess and block vacancy manually (no triggers for these)
        if data.get('MessId'):
            execute('UPDATE messinfo SET Vacancy = Vacancy - 1 WHERE MessId = %s AND Vacancy > 0', (data.get('MessId'),))
        if data.get('StHostelId'):
            execute('UPDATE blockinfo SET Vacancy = Vacancy - 1 WHERE HostelId = %s AND Vacancy > 0', (data.get('StHostelId'),))

        loginData = {
            'id': student_id,
            'username': username or f'student{student_id}',
            'password': data.get('Password') or 'pass123',
            'role': 'student'
        }
        execute('INSERT INTO login (id, username, password, role) VALUES (%s, %s, %s, %s)', (loginData['id'], loginData['username'], loginData['password'], loginData['role']))
        return jsonify({'id': student_id, 'message': 'Student added'})
    except pymysql.err.OperationalError as e:
        # Catch trigger errors (SQLSTATE 45000)
        if 'Room has no vacancy' in str(e) or 'Room does not exist' in str(e):
            return jsonify({'error': str(e).split(': ')[-1] if ': ' in str(e) else str(e)}), 400
        raise


@app.route('/api/<table>')
def get_table(table):
    allowedTables = ['blockinfo','roominfo','messinfo','feesinfo','studentinfo','login','hostelmanagerinfo','roomapplication']
    if table.lower() not in allowedTables:
        return jsonify({'error': 'Not found'}), 404

    publicTables = ['blockinfo','roominfo','messinfo','feesinfo']
    if table.lower() not in publicTables:
        if 'user' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        if session['user'].get('role') != 'manager':
            return jsonify({'error': 'Forbidden'}), 403

    rows = query(f'SELECT * FROM {table}')
    return jsonify(rows)


@app.route('/api/studentinfo/<int:student_id>/fees', methods=['PUT'])
def update_fees(student_id):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if session['user'].get('role') != 'manager':
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json() or {}
    fees = data.get('FeesPaid')
    if fees is None:
        return jsonify({'error': 'FeesPaid required'}), 400
    
    # Use stored procedure to update fees
    call_procedure('sp_update_fee_payment', (student_id, fees))
    return jsonify({'message': 'Fees updated successfully'})


@app.route('/api/studentinfo/<int:student_id>/assign-room', methods=['POST'])
def assign_room(student_id):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if session['user'].get('role') != 'manager':
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json() or {}
    room_no = data.get('RoomNo')
    hostel_id = data.get('HostelId')
    
    if not room_no or not hostel_id:
        return jsonify({'error': 'RoomNo and HostelId required'}), 400
    
    try:
        # Use stored procedure to assign room
        call_procedure('sp_assign_room', (student_id, room_no, hostel_id))
        return jsonify({'message': 'Room assigned successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
