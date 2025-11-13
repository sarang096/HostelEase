USE hostel_db;

-- Add FeesPaid column to studentinfo table if it doesn't exist
ALTER TABLE studentinfo ADD COLUMN IF NOT EXISTS FeesPaid DECIMAL(10,2) DEFAULT 0;

-- Update existing students to have 0 fees paid by default
UPDATE studentinfo SET FeesPaid = 0 WHERE FeesPaid IS NULL;