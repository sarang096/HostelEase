USE hostel_db;

DELIMITER $$

-- Stored procedure to assign a room to a student
-- This procedure should handle room assignment logic
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
        -- when studentinfo is updated
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Room has no vacancy';
    END IF;
END$$

DELIMITER ;
