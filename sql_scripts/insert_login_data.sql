USE hostel_db;

-- Insert dummy login data for students (assuming student_id 1, 2, 3 exist in studentinfo)
INSERT INTO login (id, username, password, role) VALUES
(1, 'student1', 'pass123', 'student'),
(2, 'student2', 'pass123', 'student'),
(3, 'student3', 'pass123', 'student');

-- Insert dummy login data for managers (assuming manager_id 1, 2 exist in hostelmanagerinfo)
INSERT INTO login (id, username, password, role) VALUES
(101, 'manager1', 'admin123', 'manager'),
(102, 'manager2', 'admin123', 'manager');
