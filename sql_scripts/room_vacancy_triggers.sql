USE hostel_db;

DELIMITER $$

-- Trigger to reduce room vacancy when a student is inserted into studentinfo
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

-- Trigger to increase room vacancy when a student is deleted from studentinfo
CREATE TRIGGER trg_increase_room_vacancy
AFTER DELETE ON studentinfo
FOR EACH ROW
BEGIN
    UPDATE RoomInfo
    SET Vacancy = Vacancy + 1
    WHERE RoomNo = OLD.RoomId;
END$$

DELIMITER ;
