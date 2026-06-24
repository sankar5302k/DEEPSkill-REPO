DROP TABLE IF EXISTS professors CASCADE;
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS departments CASCADE;


CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    hod_name VARCHAR(100),
    budget DECIMAL(12, 2)
);


CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    date_of_birth DATE,
    department_id INT,
    enrollment_year INT,
    CONSTRAINT fk_student_department FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
);


CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    course_code VARCHAR(20) UNIQUE,
    credits INT,
    department_id INT,
    CONSTRAINT fk_course_department FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE
);


CREATE TABLE enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrollment_date DATE,
    grade CHAR(2),
    CONSTRAINT fk_enrollment_student FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_enrollment_course FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);


CREATE TABLE professors (
    professor_id SERIAL PRIMARY KEY,
    prof_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    department_id INT,
    salary DECIMAL(10, 2),
    CONSTRAINT fk_professor_department FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
);

ALTER TABLE students ADD COLUMN phone_number VARCHAR(15);

ALTER TABLE courses ADD COLUMN max_seats INT DEFAULT 60;

ALTER TABLE enrollments ADD CONSTRAINT chk_enrollment_grade CHECK (grade IN ('A', 'B', 'C', 'D', 'F') OR grade IS NULL);

ALTER TABLE departments RENAME COLUMN hod_name TO head_of_dept;

ALTER TABLE students DROP COLUMN phone_number;