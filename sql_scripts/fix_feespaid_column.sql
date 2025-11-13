USE hostel_db;

-- Modify FeesPaid column to allow larger values
ALTER TABLE studentinfo MODIFY COLUMN FeesPaid INT DEFAULT 0;