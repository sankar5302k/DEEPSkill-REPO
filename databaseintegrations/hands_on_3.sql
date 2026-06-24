SELECT s.student_id, (s.first_name || ' ' || s.last_name) AS student_name, COUNT(e.enrollment_id) AS course_count
FROM students s
INNER JOIN enrollments e ON s.student_id = e.student_id
GROUP BY s.student_id, s.first_name, s.last_name
HAVING COUNT(e.enrollment_id) > (
    SELECT AVG(student_enrollments)
    FROM (
        SELECT COUNT(enrollment_id) AS student_enrollments
        FROM enrollments
        GROUP BY student_id
    ) avg_subquery
)
ORDER BY course_count DESC;


SELECT c.course_id, c.course_name
FROM courses c
WHERE EXISTS (
    SELECT 1 FROM enrollments e WHERE e.course_id = c.course_id
) AND NOT EXISTS (
    SELECT 1 
    FROM enrollments e 
    WHERE e.course_id = c.course_id AND (e.grade <> 'A' OR e.grade IS NULL)
)
ORDER BY c.course_id;


SELECT p.professor_id, p.prof_name, p.department_id, p.salary
FROM professors p
WHERE p.salary = (
    SELECT MAX(sub.salary)
    FROM professors sub
    WHERE sub.department_id = p.department_id
)
ORDER BY p.department_id;


SELECT dept_avg.dept_name, dept_avg.average_salary
FROM (
    SELECT d.dept_name, ROUND(AVG(p.salary), 2) AS average_salary
    FROM departments d
    INNER JOIN professors p ON d.department_id = p.department_id
    GROUP BY d.department_id, d.dept_name
) dept_avg
WHERE dept_avg.average_salary > 85000
ORDER BY dept_avg.average_salary DESC;


CREATE OR REPLACE VIEW vw_student_enrollment_summary AS
SELECT 
    (s.first_name || ' ' || s.last_name) AS student_full_name,
    d.dept_name AS department_name,
    COUNT(e.enrollment_id) AS courses_enrolled,
    ROUND(AVG(
        CASE e.grade
            WHEN 'A' THEN 4
            WHEN 'B' THEN 3
            WHEN 'C' THEN 2
            WHEN 'D' THEN 1
            WHEN 'F' THEN 0
            ELSE NULL
        END
    ), 2) AS gpa
FROM students s
LEFT JOIN departments d ON s.department_id = d.department_id
LEFT JOIN enrollments e ON s.student_id = e.student_id
GROUP BY s.student_id, s.first_name, s.last_name, d.dept_name;


CREATE OR REPLACE VIEW vw_course_stats AS
SELECT 
    c.course_name,
    c.course_code,
    COUNT(e.enrollment_id) AS total_enrollments,
    ROUND(AVG(
        CASE e.grade
            WHEN 'A' THEN 4
            WHEN 'B' THEN 3
            WHEN 'C' THEN 2
            WHEN 'D' THEN 1
            WHEN 'F' THEN 0
            ELSE NULL
        END
    ), 2) AS avg_gpa
FROM courses c
LEFT JOIN enrollments e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_name, c.course_code;


SELECT student_full_name, department_name, courses_enrolled, gpa
FROM vw_student_enrollment_summary
WHERE gpa > 3.0
ORDER BY gpa DESC;

-- Step 42 Documentation: Attempt to UPDATE a row through vw_student_enrollment_summary and note what happens.
-- (This command is commented out because it will raise an error in PostgreSQL. See explanation below.)
-- UPDATE vw_student_enrollment_summary SET department_name = 'Civil Engineering' WHERE student_full_name = 'Arjun Mehta';

/*

EXPLANATION: Why Multi-Table Views are Generally Not Updatable

1. Ambiguity in underlying data updates: A multi-table join view like 'vw_student_enrollment_summary'
   represents data aggregated and joined from three tables: students, departments, and enrollments.
   If an update is performed (e.g., modifying 'department_name'), the database engine cannot determine
   which physical rows and columns should change (does it change the department's name in 'departments',
   or reassign the student's department_id in 'students'?).
2. Loss of Key Preservation: Because the view uses aggregation functions (COUNT, AVG) and GROUP BY,
   multiple underlying table rows are merged into a single view row. A modification to an aggregated
   column (like 'gpa' or 'courses_enrolled') has no direct 1-to-1 physical mapping to a single row in the
   source tables.
3. Database Enforcement: PostgreSQL enforces that automatically updatable views must select from a single
   table or subquery and must not contain WITH, DISTINCT, GROUP BY, HAVING, LIMIT, OFFSET, or set operations.
   Otherwise, updating raises: "ERROR: cannot update view ..."

*/


DROP VIEW IF EXISTS vw_course_stats CASCADE;
DROP VIEW IF EXISTS vw_student_enrollment_summary CASCADE;


CREATE VIEW vw_student_enrollment_summary AS
SELECT student_id, first_name, last_name, email, department_id, enrollment_year
FROM students
WHERE enrollment_year = 2022
WITH CHECK OPTION;

-- Writing in comments because it will stop the execution of the sql script.
-- Testing WITH CHECK OPTION:
-- 1. This insert will succeed because enrollment_year matches the view's WHERE condition:
-- INSERT INTO vw_student_enrollment_summary (first_name, last_name, email, department_id, enrollment_year)
-- VALUES ('Rahul', 'Kumar', 'rahul.k@college.edu', 1, 2022);

-- 2. This insert will fail because enrollment_year is 2023, violating the view constraint:
-- INSERT INTO vw_student_enrollment_summary (first_name, last_name, email, department_id, enrollment_year)
-- VALUES ('Simran', 'Kaur', 'simran.k@college.edu', 1, 2023);
-- -> PostgreSQL raises: "ERROR: new row violates check option for view..."



CREATE OR REPLACE FUNCTION fn_enroll_student(
    p_student_id INT,
    p_course_id INT,
    p_enrollment_date DATE
) RETURNS VOID AS $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM enrollments 
        WHERE student_id = p_student_id AND course_id = p_course_id
    ) THEN
        RAISE EXCEPTION 'Duplicate enrollment error: Student % is already enrolled in course %.', p_student_id, p_course_id;
    END IF;

    INSERT INTO enrollments (student_id, course_id, enrollment_date, grade)
    VALUES (p_student_id, p_course_id, p_enrollment_date, NULL);
END;
$$ LANGUAGE plpgsql;


CREATE TABLE IF NOT EXISTS department_transfer_log (
    log_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    old_department_id INT,
    new_department_id INT,
    transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL
);


CREATE OR REPLACE PROCEDURE sp_transfer_student(
    p_student_id INT,
    p_new_department_id INT
) AS $$
DECLARE
    v_old_department_id INT;
BEGIN
    SELECT department_id INTO v_old_department_id
    FROM students
    WHERE student_id = p_student_id;

    IF v_old_department_id IS NULL THEN
        RAISE EXCEPTION 'Student with ID % does not exist.', p_student_id;
    END IF;
    
    UPDATE students
    SET department_id = p_new_department_id
    WHERE student_id = p_student_id;

    INSERT INTO department_transfer_log (student_id, old_department_id, new_department_id, status)
    VALUES (p_student_id, v_old_department_id, p_new_department_id, 'SUCCESS');

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Transfer failed for Student ID %. Rolling back changes.', p_student_id;
        RAISE;
END;
$$ LANGUAGE plpgsql;


SELECT student_id, first_name, department_id FROM students WHERE student_id = 1;

-- Programmed as comments because it will return errors when we run the whole sql script at once
-- BEGIN;
-- CALL sp_transfer_student(1, 999); -- This call will fail due to Foreign Key constraint violation
-- ROLLBACK; -- Rollback explicitly (PostgreSQL aborts the transaction state automatically on failure)

SELECT student_id, first_name, department_id FROM students WHERE student_id = 1;


BEGIN;

INSERT INTO enrollments (student_id, course_id, enrollment_date, grade)
VALUES (1, 3, '2023-09-01', 'A');

SAVEPOINT first_enrollment_saved;

-- 3. Deliberately fail the second insert (using invalid student_id 9999 to trigger Foreign Key violation)
-- INSERT INTO enrollments (student_id, course_id, enrollment_date, grade)
-- VALUES (9999, 1, '2023-09-01', 'B');

-- 4. Rollback to checkpoint (undoes the failed insert and restores transaction state to active)
-- ROLLBACK TO SAVEPOINT first_enrollment_saved;

COMMIT;

SELECT * FROM enrollments WHERE student_id = 1 AND course_id = 3;