# Database Procedures and Triggers Integration

This document describes the stored procedures and triggers used in the Hostel Management System.

## Overview

The application now uses **2 stored procedures** and **2 triggers** to handle database operations more efficiently and maintain data consistency.

---

## Stored Procedures

### 1. `sp_assign_room`
**Purpose:** Assigns a room to a student with automatic vacancy checking.

**Parameters:**
- `p_student_id` (INT): The student's ID
- `p_room_no` (INT): The room number to assign
- `p_hostel_id` (INT): The hostel/block ID

**Usage in Flask:**
```python
call_procedure('sp_assign_room', (student_id, room_no, hostel_id))
```

**SQL:**
```sql
CALL sp_assign_room(101, 205, 1);
```

**Logic:**
1. Checks if the room has vacancy
2. If yes, updates the student's `RoomId` and `StHostelId`
3. If no, raises an error
4. Room vacancy is automatically reduced by the `trg_reduce_room_vacancy` trigger

---

### 2. `sp_update_fee_payment`
**Purpose:** Updates or inserts fee payment records for a student.

**Parameters:**
- `p_student_id` (INT): The student's ID
- `p_fees_paid` (DECIMAL): Amount of fees paid

**Usage in Flask:**
```python
call_procedure('sp_update_fee_payment', (student_id, fees_amount))
```

**SQL:**
```sql
CALL sp_update_fee_payment(101, 25000.00);
```

**Logic:**
1. Checks if a fees record exists for the student
2. If yes, updates the `FeesPaid` amount
3. If no, creates a new record with the specified amount

---

## Triggers

### 1. `trg_reduce_room_vacancy`
**Event:** AFTER INSERT on `studentinfo`

**Purpose:** Automatically reduces room vacancy when a student is assigned to a room.

**Logic:**
- When a student record is inserted with a `RoomId`, the corresponding room's vacancy is reduced by 1
- Only reduces if vacancy is greater than 0

**Example:**
```sql
-- This INSERT will automatically reduce vacancy in RoomInfo
INSERT INTO studentinfo (StudentId, Firstname, Lastname, RoomId) 
VALUES (101, 'John', 'Doe', 205);
```

---

### 2. `trg_increase_room_vacancy`
**Event:** AFTER DELETE on `studentinfo`

**Purpose:** Automatically increases room vacancy when a student is removed.

**Logic:**
- When a student record is deleted and they had a `RoomId`, the corresponding room's vacancy is increased by 1

**Example:**
```sql
-- This DELETE will automatically increase vacancy in RoomInfo
DELETE FROM studentinfo WHERE StudentId = 101;
```

---

## Installation

To set up all procedures and triggers, run:

```bash
mysql -u root -p hostel_db < sql_scripts/setup_procedures_and_triggers.sql
```

Or from MySQL command line:
```sql
SOURCE sql_scripts/setup_procedures_and_triggers.sql;
```

---

## Flask Application Changes

### New Helper Function
```python
def call_procedure(proc_name, params=None):
    """Call a stored procedure"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.callproc(proc_name, params or ())
            conn.commit()
    finally:
        conn.close()
```

### Endpoints Modified

1. **`PUT /api/studentinfo/<id>/fees`** - Now uses `sp_update_fee_payment`
2. **`POST /api/studentinfo`** - Now uses `sp_update_fee_payment` for initial fees
3. **`POST /api/studentinfo/<id>/assign-room`** - New endpoint using `sp_assign_room`

### Automatic Behavior

- **Adding a student with RoomId:** Room vacancy automatically decreases (trigger)
- **Deleting a student with RoomId:** Room vacancy automatically increases (trigger)
- **Manual room vacancy updates removed:** No longer needed in Flask code

---

## Verification

To verify the procedures and triggers are installed:

```sql
-- Show procedures
SHOW PROCEDURE STATUS WHERE Db = 'hostel_db';

-- Show triggers
SHOW TRIGGERS;

-- Test procedure
CALL sp_update_fee_payment(1, 10000);

-- Test trigger (insert a student)
INSERT INTO studentinfo (StudentId, Firstname, Lastname, RoomId) 
VALUES (999, 'Test', 'User', 101);

-- Check room vacancy decreased
SELECT * FROM RoomInfo WHERE RoomNo = 101;

-- Cleanup
DELETE FROM studentinfo WHERE StudentId = 999;

-- Check room vacancy increased
SELECT * FROM RoomInfo WHERE RoomNo = 101;
```

---

## Summary

**Total Database Objects:**
- **Procedures:** 2 (`sp_assign_room`, `sp_update_fee_payment`)
- **Triggers:** 2 (`trg_reduce_room_vacancy`, `trg_increase_room_vacancy`)
- **Total:** 4 database objects

**Benefits:**
- ✅ Automatic vacancy management
- ✅ Consistent data updates
- ✅ Reduced application code complexity
- ✅ Better database encapsulation
- ✅ Easier maintenance and testing
