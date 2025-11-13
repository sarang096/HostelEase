-- ===================================================================
-- Complete Database Setup for Procedures and Triggers
-- Hostel Management System
-- ===================================================================

USE hostel_db;

-- Drop existing procedures and triggers if they exist
DROP PROCEDURE IF EXISTS sp_assign_room;
DROP PROCEDURE IF EXISTS sp_update_fee_payment;
DROP TRIGGER IF EXISTS trg_reduce_room_vacancy;
DROP TRIGGER IF EXISTS trg_increase_room_vacancy;

DELIMITER $$

-- ===================================================================
-- STORED PROCEDURES
-- ===================================================================

-- Procedure 1: Assign Room to Student
-- This procedure assigns a room to a student and checks for vacancy
CREATE PROCEDURE sp_assign_room(
    IN p_student_id INT,
    IN p_room_no INT,
    IN p_hostel_id INT
)
BEGIN
    DECLARE room_vacancy INT;
    
    -- Check if room has vacancy
    SELECT Vacancy INTO room_vacancy
    FROM RoomInfo
    WHERE RoomNo = p_room_no;
    
    IF room_vacancy > 0 THEN
        -- Update student info with room and hostel
        UPDATE studentinfo
        SET RoomId = p_room_no,
            StHostelId = p_hostel_id
        WHERE StudentId = p_student_id;
        
        -- Note: Room vacancy will be automatically reduced by trg_reduce_room_vacancy trigger
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Room has no vacancy';
    END IF;
END$$

-- Procedure 2: Update Fee Payment
-- This procedure updates or inserts fee payment records
CREATE PROCEDURE sp_update_fee_payment(
    IN p_student_id INT,
    IN p_fees_paid DECIMAL(10,2)
)
BEGIN
    DECLARE fee_exists INT;
    
    -- Check if fees record exists
    SELECT COUNT(*) INTO fee_exists
    FROM FeesInfo
    WHERE StudentId = p_student_id;
    
    IF fee_exists > 0 THEN
        -- Update existing fees record
        UPDATE FeesInfo
        SET FeesPaid = p_fees_paid
        WHERE StudentId = p_student_id;
    ELSE
        -- Insert new fees record
        INSERT INTO FeesInfo (StudentId, FeesPaid)
        VALUES (p_student_id, p_fees_paid);
    END IF;
END$$

-- ===================================================================
-- TRIGGERS
-- ===================================================================

-- Trigger 1: Reduce Room Vacancy on Student Insert
-- Automatically reduces room vacancy when a student is assigned a room
-- Raises an error if room has no vacancy
CREATE TRIGGER trg_reduce_room_vacancy
BEFORE INSERT ON studentinfo
FOR EACH ROW
BEGIN
    DECLARE room_vacancy INT;
    
    -- Check if RoomId is assigned
    IF NEW.RoomId IS NOT NULL THEN
        -- Get the current vacancy of the room
        SELECT Vacancy INTO room_vacancy
        FROM RoomInfo
        WHERE RoomNo = NEW.RoomId;
        
        -- Raise error if no vacancy
        IF room_vacancy IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Room does not exist';
        ELSEIF room_vacancy = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot assign student: Room has no vacancy';
        END IF;
        
        -- Reduce vacancy
        UPDATE RoomInfo
        SET Vacancy = Vacancy - 1
        WHERE RoomNo = NEW.RoomId;
    END IF;
END$$

-- Trigger 2: Increase Room Vacancy on Student Delete
-- Automatically increases room vacancy when a student is removed
CREATE TRIGGER trg_increase_room_vacancy
AFTER DELETE ON studentinfo
FOR EACH ROW
BEGIN
    IF OLD.RoomId IS NOT NULL THEN
        UPDATE RoomInfo
        SET Vacancy = Vacancy + 1
        WHERE RoomNo = OLD.RoomId;
    END IF;
END$$

DELIMITER ;

-- ===================================================================
-- Verification Queries
-- ===================================================================

-- Show all procedures
SHOW PROCEDURE STATUS WHERE Db = 'hostel_db';

-- Show all triggers
SHOW TRIGGERS;

-- Success message
SELECT 'All procedures and triggers have been successfully created!' AS Status;
