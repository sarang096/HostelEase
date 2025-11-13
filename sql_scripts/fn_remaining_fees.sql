USE hostel_db;

DELIMITER $$

-- Function to calculate remaining fees for a student
-- Returns the remaining fees amount (Total Fees - Fees Paid)
-- Note: This function assumes the column is named 'FeesPaid' or 'Amount'
CREATE FUNCTION fn_remaining_fees(p_student_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_fees DECIMAL(10,2) DEFAULT 50000.00;
    DECLARE fees_paid DECIMAL(10,2) DEFAULT 0.00;
    DECLARE remaining DECIMAL(10,2);
    DECLARE column_exists INT DEFAULT 0;
    
    -- Check if FeesPaid column exists, otherwise try Amount
    SELECT COUNT(*) INTO column_exists
    FROM information_schema.columns
    WHERE table_schema = 'hostel_db'
    AND table_name = 'FeesInfo'
    AND column_name = 'FeesPaid';
    
    IF column_exists > 0 THEN
        -- Get fees paid from FeesPaid column
        SELECT COALESCE(FeesPaid, 0) INTO fees_paid
        FROM FeesInfo
        WHERE StudentId = p_student_id;
    ELSE
        -- Try Amount column as fallback
        SELECT COALESCE(Amount, 0) INTO fees_paid
        FROM FeesInfo
        WHERE StudentId = p_student_id;
    END IF;
    
    -- Calculate remaining fees
    SET remaining = total_fees - fees_paid;
    
    -- Return remaining fees (cannot be negative)
    IF remaining < 0 THEN
        RETURN 0;
    ELSE
        RETURN remaining;
    END IF;
END$$

DELIMITER ;
