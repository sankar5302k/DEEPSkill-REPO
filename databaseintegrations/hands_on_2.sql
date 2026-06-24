INSERT INTO departments (dept_name, head_of_dept, budget) VALUES
('Computer Science', 'Dr. Ramesh Kumar', 850000.00),
('Electronics', 'Dr. Priya Nair', 620000.00),
('Mechanical', 'Dr. Suresh Iyer', 540000.00),
('Civil', 'Dr. Ananya Sharma', 430000.00);


INSERT INTO students (first_name, last_name, email, date_of_birth, department_id, enrollment_year) VALUES
('Arjun', 'Mehta', 'arjun.mehta@college.edu', '2003-04-12', 1, 2022),
('Priya', 'Suresh', 'priya.suresh@college.edu', '2003-07-25', 1, 2022),
('Rohan', 'Verma', 'rohan.verma@college.edu', '2002-11-08', 2, 2021),
('Sneha', 'Patel', 'sneha.patel@college.edu', '2004-01-30', 3, 2023),
('Vikram', 'Das', 'vikram.das@college.edu', '2003-09-14', 1, 2022),
('Kavya', 'Menon', 'kavya.menon@college.edu', '2002-05-17', 2, 2021),
('Aditya', 'Singh', 'aditya.singh@college.edu', '2004-03-22', 4, 2023),
('Deepika', 'Rao', 'deepika.rao@college.edu', '2003-08-09', 1, 2022);


INSERT INTO courses (course_name, course_code, credits, department_id) VALUES
('Data Structures & Algorithms', 'CS101', 4, 1),
('Database Management Systems', 'CS102', 3, 1),
('Object Oriented Programming', 'CS103', 4, 1),
('Circuit Theory', 'EC101', 3, 2),
('Thermodynamics', 'ME101', 3, 3);


INSERT INTO enrollments (student_id, course_id, enrollment_date, grade) VALUES
(1, 1, '2022-07-01', 'A'), (1, 2, '2022-07-01', 'B'),
(2, 1, '2022-07-01', 'B'), (2, 3, '2022-07-01', 'A'),
(3, 4, '2021-07-01', 'A'), (4, 5, '2023-07-01', NULL),
(5, 1, '2022-07-01', 'C'), (5, 2, '2022-07-01', 'A'),
(6, 4, '2021-07-01', 'B'), (7, 5, '2023-07-01', NULL),
(8, 1, '2022-07-01', 'A'), (8, 3, '2022-07-01', 'B');


INSERT INTO professors (prof_name, email, department_id, salary) VALUES
('Dr. Anand Krishnan', 'anand.k@college.edu', 1, 95000.00),
('Dr. Meena Pillai', 'meena.p@college.edu', 1, 88000.00),
('Dr. Sunil Rajan', 'sunil.r@college.edu', 2, 82000.00),
('Dr. Latha Gopal', 'latha.g@college.edu', 3, 79000.00),
('Dr. Kartik Bose', 'kartik.b@college.edu', 4, 76000.00);


INSERT INTO students (first_name, last_name, email, date_of_birth, department_id, enrollment_year) VALUES
('Trivikraman', 'TS', 'trivikraman.ts@college.edu', '2001-05-15', 1, 2022),
('Neha', 'Sharma', 'neha.sharma@college.edu', '2003-12-10', 2, 2023);


SELECT COUNT(*) AS total_students_after_insert FROM students;


UPDATE enrollments
SET grade = 'B'
WHERE student_id = 5 AND course_id = 1;


SELECT * FROM enrollments WHERE student_id = 5 AND course_id = 1;


DELETE FROM enrollments
WHERE grade IS NULL;


SELECT COUNT(*) AS total_departments FROM departments;
SELECT COUNT(*) AS total_students FROM students;
SELECT COUNT(*) AS total_courses FROM courses;
SELECT COUNT(*) AS total_enrollments FROM enrollments;
SELECT COUNT(*) AS total_professors FROM professors;


SELECT student_id, first_name, last_name, email, enrollment_year
FROM students
WHERE enrollment_year = 2022
ORDER BY last_name ASC;


SELECT course_id, course_name, course_code, credits
FROM courses
WHERE credits > 3
ORDER BY credits DESC;


SELECT professor_id, prof_name, email, salary
FROM professors
WHERE salary BETWEEN 80000 AND 95000;


SELECT student_id, first_name, last_name, email
FROM students
WHERE email LIKE '%@college.edu';


SELECT enrollment_year, COUNT(*) AS student_count
FROM students
GROUP BY enrollment_year
ORDER BY enrollment_year;


SELECT (s.first_name || ' ' || s.last_name) AS student_full_name, d.dept_name AS department_name
FROM students s
INNER JOIN departments d ON s.department_id = d.department_id
ORDER BY student_full_name;


SELECT e.enrollment_id, (s.first_name || ' ' || s.last_name) AS student_name, c.course_name, e.enrollment_date, e.grade
FROM enrollments e
INNER JOIN students s ON e.student_id = s.student_id
INNER JOIN courses c ON e.course_id = c.course_id
ORDER BY e.enrollment_id;


SELECT s.student_id, (s.first_name || ' ' || s.last_name) AS student_name, s.email
FROM students s
LEFT JOIN enrollments e ON s.student_id = e.student_id
WHERE e.enrollment_id IS NULL
ORDER BY s.student_id;


SELECT c.course_code, c.course_name, COUNT(e.enrollment_id) AS enrollment_count
FROM courses c
LEFT JOIN enrollments e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_code, c.course_name
ORDER BY enrollment_count DESC, c.course_code;


SELECT d.dept_name, p.prof_name, COALESCE(p.salary, 0.00) AS salary
FROM departments d
LEFT JOIN professors p ON d.department_id = p.department_id
ORDER BY d.dept_name, p.prof_name;



SELECT c.course_name, COUNT(e.enrollment_id) AS enrollment_count
FROM courses c
LEFT JOIN enrollments e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_name
ORDER BY enrollment_count DESC;


SELECT d.dept_name, ROUND(AVG(p.salary), 2) AS average_professor_salary
FROM departments d
INNER JOIN professors p ON d.department_id = p.department_id
GROUP BY d.department_id, d.dept_name
ORDER BY average_professor_salary DESC;


SELECT dept_name, budget
FROM departments
WHERE budget > 600000
ORDER BY budget DESC;


SELECT e.grade, COUNT(*) AS grade_count
FROM enrollments e
INNER JOIN courses c ON e.course_id = c.course_id
WHERE c.course_code = 'CS101'
GROUP BY e.grade
ORDER BY e.grade;


SELECT d.dept_name, COUNT(DISTINCT e.student_id) AS enrolled_students_count
FROM departments d
INNER JOIN courses c ON d.department_id = c.department_id
INNER JOIN enrollments e ON c.course_id = e.course_id
GROUP BY d.department_id, d.dept_name
HAVING COUNT(DISTINCT e.student_id) > 2
ORDER BY enrolled_students_count DESC;