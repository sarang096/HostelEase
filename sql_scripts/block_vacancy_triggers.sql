USE hostel_db;

DELIMITER $$

-- Trigger to update block vacancy when room vacancy changes
CREATE TRIGGER trg_update_block_on_room_full
AFTER UPDATE ON roominfo
FOR EACH ROW
BEGIN
    IF OLD.Vacancy > 0 AND NEW.Vacancy = 0 THEN
        UPDATE blockinfo SET Vacancy = Vacancy - 1 WHERE BlockId = NEW.BlockId AND Vacancy > 0;
    END IF;
    
    IF OLD.Vacancy = 0 AND NEW.Vacancy > 0 THEN
        UPDATE blockinfo SET Vacancy = Vacancy + 1 WHERE BlockId = NEW.BlockId;
    END IF;
END$$

DELIMITER ;
