USE hostel_db;

-- Insert fees records for existing students
INSERT INTO FeesInfo (StudentId, Amount, Status) 
SELECT StudentId, 30000, 'Paid' 
FROM studentinfo 
WHERE StudentId NOT IN (SELECT StudentId FROM FeesInfo WHERE StudentId IS NOT NULL);