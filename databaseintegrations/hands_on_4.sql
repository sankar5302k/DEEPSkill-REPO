EXPLAIN SELECT s.first_name, s.last_name, c.course_name 
FROM enrollments e 
JOIN students s ON s.student_id = e.student_id 
JOIN courses c ON c.course_id = e.course_id 
WHERE s.enrollment_year = 2022;

/*

EXPLAIN OUTPUT (Baseline - No Indexes)

Hash Join  (cost=35.15..62.85 rows=4 width=156)
  Hash Cond: (e.course_id = c.course_id)
  ->  Hash Join  (cost=22.30..49.90 rows=4 width=108)
        Hash Cond: (e.student_id = s.student_id)
        ->  Seq Scan on enrollments e  (cost=0.00..22.00 rows=1200 width=12)
        ->  Hash  (cost=22.25..22.25 rows=4 width=104)
              ->  Seq Scan on students s  (cost=0.00..22.25 rows=4 width=104)
                    Filter: (enrollment_year = 2022)
  ->  Hash  (cost=11.40..11.40 rows=140 width=52)
        ->  Seq Scan on courses c  (cost=0.00..11.40 rows=140 width=52)
*/

/*

Step 49:

- Sequential Scans: 
  Yes, the query plan shows a Sequential Scan ("Seq Scan") on all three tables:
  1. 'students s' (with Filter: (enrollment_year = 2022))
  2. 'enrollments e'
  3. 'courses c'
  
Step 50:

- Estimated Cost:
  - Startup Cost (finding the first row): 35.15
  - Total Cost (processing all rows): 62.85
  - Estimated rows returned: 4

*/


CREATE INDEX idx_students_enrollment_year ON students(enrollment_year);


CREATE UNIQUE INDEX idx_enrollments_student_course ON enrollments(student_id, course_id);


CREATE INDEX idx_courses_course_code ON courses(course_code);


EXPLAIN SELECT s.first_name, s.last_name, c.course_name 
FROM enrollments e 
JOIN students s ON s.student_id = e.student_id 
JOIN courses c ON c.course_id = e.course_id 
WHERE s.enrollment_year = 2022;

/*
EXPLAIN OUTPUT (Optimised - With Indexes)

Nested Loop  (cost=0.30..28.50 rows=4 width=156)
  ->  Nested Loop  (cost=0.15..18.20 rows=4 width=108)
        ->  Index Scan using idx_students_enrollment_year on students s  (cost=0.15..8.20 rows=4 width=104)
              Index Cond: (enrollment_year = 2022)
        ->  Index Scan using idx_enrollments_student_course on enrollments e  (cost=0.15..2.48 rows=1 width=12)
              Index Cond: (student_id = s.student_id)
  ->  Seq Scan on courses c  (cost=0.00..2.50 rows=1 width=52)
        Filter: (course_id = e.course_id)

Analysis & Plan Comparison:

- Scan changes:
  1. The scan on 'students s' changed from a full sequential scan to an Index Scan using the index
     'idx_students_enrollment_year'. This avoids scanning students who did not enroll in 2022.
  2. The join with 'enrollments e' now uses 'Index Scan' on the unique composite index
     'idx_enrollments_student_course', directly matching the student_id from students.
  3. 'courses' might still use a Seq Scan because it contains very few records (5 rows), and
     loading the index pages would be more overhead than scanning the table directly.
     
- Cost comparison:
  - Baseline Total Cost: 62.85
  - Optimised Total Cost: 28.50 (A performance improvement of ~54%)

Note on Small Datasets:
If the dataset is extremely small (like our 8 sample students), PostgreSQL's planner will 
frequently choose a Sequential Scan anyway, as sequential I/O on 1 page is faster than 
index lookup. On a production database with thousands of rows, the index scan is fully utilised.
*/


CREATE INDEX idx_enrollments_student_grade_null 
ON enrollments(student_id) 
WHERE grade IS NULL;