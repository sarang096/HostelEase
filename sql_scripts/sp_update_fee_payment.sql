USE hostel_db;

DELIMITER $$

-- Stored procedure to update fee payment for a student
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

DELIMITER ;
