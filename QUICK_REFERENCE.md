# Quick Reference - Procedures & Triggers

## Database Objects Summary

| Type      | Name                        | Purpose                          |
|-----------|----------------------------|----------------------------------|
| Procedure | `sp_assign_room`           | Assign room to student           |
| Procedure | `sp_update_fee_payment`    | Update/insert fee payment        |
| Trigger   | `trg_reduce_room_vacancy`  | Auto-reduce vacancy on INSERT    |
| Trigger   | `trg_increase_room_vacancy`| Auto-increase vacancy on DELETE  |

**Total: 2 Procedures + 2 Triggers = 4 Database Objects**

---

## Quick Installation

```powershell
# Install all at once
mysql -u root -p hostel_db < sql_scripts/setup_procedures_and_triggers.sql

# Verify installation
python tests/test_procedures_triggers.py
```

---

## Usage Examples

### In MySQL
```sql
-- Update fees
CALL sp_update_fee_payment(1, 25000.00);

-- Assign room
CALL sp_assign_room(1, 101, 1);

-- Check procedures
SHOW PROCEDURE STATUS WHERE Db = 'hostel_db';

-- Check triggers
SHOW TRIGGERS;
```

### In Flask (Automatic)
```python
# Fee payment - uses sp_update_fee_payment
PUT /api/studentinfo/1/fees
Body: {"FeesPaid": 25000}

# Room assignment - uses sp_assign_room
POST /api/studentinfo/1/assign-room
Body: {"RoomNo": 101, "HostelId": 1}

# Add student - triggers handle room vacancy automatically
POST /api/studentinfo
Body: {..., "RoomId": 101, ...}
# trg_reduce_room_vacancy automatically reduces room vacancy

# Delete student - triggers handle room vacancy automatically
DELETE /api/studentinfo/1
# trg_increase_room_vacancy automatically increases room vacancy
```

---

## Trigger Behavior

### INSERT Student with RoomId
```
User Action: Add new student with RoomId=101
↓
studentinfo: INSERT new row
↓
Trigger: trg_reduce_room_vacancy fires
↓
RoomInfo: Vacancy decreased by 1 (for RoomNo=101)
```

### DELETE Student with RoomId
```
User Action: Delete student with RoomId=101
↓
studentinfo: DELETE row
↓
Trigger: trg_increase_room_vacancy fires
↓
RoomInfo: Vacancy increased by 1 (for RoomNo=101)
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `sql_scripts/setup_procedures_and_triggers.sql` | Complete installation |
| `sql_scripts/sp_assign_room.sql` | Room assignment procedure only |
| `sql_scripts/sp_update_fee_payment.sql` | Fee payment procedure only |
| `sql_scripts/room_vacancy_triggers.sql` | Room vacancy triggers only |
| `tests/test_procedures_triggers.py` | Verification script |
| `PROCEDURES_AND_TRIGGERS.md` | Full documentation |
| `INTEGRATION_SUMMARY.md` | Integration details |

---

## Key Points

✅ **Procedures handle:**
- Room assignment with validation
- Fee payment updates/inserts

✅ **Triggers handle:**
- Room vacancy on student INSERT/DELETE
- Automatic and transparent

✅ **Flask application:**
- Uses `call_procedure()` for procedures
- Triggers work automatically
- No manual room vacancy updates needed

✅ **All existing functionality preserved**
