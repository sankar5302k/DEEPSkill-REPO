"""
HANDS-ON 2: Django Models, ORM & Admin Interface
This file contains the complete Django models.py and admin.py declarations,
and includes a fully runnable simulation of the Django ORM queries using SQLite.
"""

import sqlite3

# =====================================================================
# PART 1: Django Code Declarations (models.py & admin.py)
# =====================================================================

DJANGO_MODELS_PY = """
# courses/models.py
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    head_of_dept = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return f"{self.code} - {self.name}"

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    enrollment_year = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField()
    grade = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        unique_together = [['student', 'course']]

    def __str__(self):
        return f"{self.student} enrolled in {self.course.name}"
"""

DJANGO_ADMIN_PY = """
# courses/admin.py
from django.contrib import admin
from .models import Department, Course, Student, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'credits', 'department']
    search_fields = ['name', 'code']
    list_filter = ['department']

admin.site.register(Department)
admin.site.register(Student)
admin.site.register(Enrollment)
"""

# =====================================================================
# PART 2: Django ORM Simulation (SQLite)
# =====================================================================

def setup_simulated_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Create tables mirroring Django schema
    cursor.execute("""
    CREATE TABLE department (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        head_of_dept TEXT NOT NULL,
        budget REAL NOT NULL
    );
    """)
    cursor.execute("""
    CREATE TABLE course (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        credits INTEGER NOT NULL,
        department_id INTEGER NOT NULL,
        FOREIGN KEY (department_id) REFERENCES department (id) ON DELETE CASCADE
    );
    """)
    cursor.execute("""
    CREATE TABLE student (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        department_id INTEGER NOT NULL,
        enrollment_year INTEGER NOT NULL,
        FOREIGN KEY (department_id) REFERENCES department (id) ON DELETE CASCADE
    );
    """)
    cursor.execute("""
    CREATE TABLE enrollment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        enrollment_date TEXT NOT NULL,
        grade TEXT,
        FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES course (id) ON DELETE CASCADE,
        UNIQUE (student_id, course_id)
    );
    """)
    return conn

def run_orm_simulation():
    print("=====================================================================")
    print("HANDS-ON 2: Django ORM Simulation")
    print("=====================================================================")
    
    conn = setup_simulated_db()
    cursor = conn.cursor()
    
    # Step 16: Create at least 2 Department, 4 Course, and 5 Student objects
    print("\n[Step 16] Seeding simulated database...")
    cursor.execute("INSERT INTO department (name, head_of_dept, budget) VALUES ('Computer Science', 'Dr. Smith', 100000.0);")
    cursor.execute("INSERT INTO department (name, head_of_dept, budget) VALUES ('Mathematics', 'Dr. Euler', 80000.0);")
    
    cursor.execute("INSERT INTO course (name, code, credits, department_id) VALUES ('Introduction to CS', 'CS101', 4, 1);")
    cursor.execute("INSERT INTO course (name, code, credits, department_id) VALUES ('Data Structures', 'CS201', 4, 1);")
    cursor.execute("INSERT INTO course (name, code, credits, department_id) VALUES ('Calculus I', 'MATH101', 3, 2);")
    cursor.execute("INSERT INTO course (name, code, credits, department_id) VALUES ('Linear Algebra', 'MATH201', 3, 2);")
    
    cursor.execute("INSERT INTO student (first_name, last_name, email, department_id, enrollment_year) VALUES ('Alice', 'Smith', 'alice@college.edu', 1, 2025);")
    cursor.execute("INSERT INTO student (first_name, last_name, email, department_id, enrollment_year) VALUES ('Bob', 'Jones', 'bob@college.edu', 1, 2025);")
    cursor.execute("INSERT INTO student (first_name, last_name, email, department_id, enrollment_year) VALUES ('Charlie', 'Brown', 'charlie@college.edu', 2, 2026);")
    cursor.execute("INSERT INTO student (first_name, last_name, email, department_id, enrollment_year) VALUES ('David', 'Miller', 'david@college.edu', 2, 2026);")
    cursor.execute("INSERT INTO student (first_name, last_name, email, department_id, enrollment_year) VALUES ('Eva', 'Green', 'eva@college.edu', 1, 2025);")
    
    print("Database seeded successfully.")

    # Step 17: Query all courses in department_name='Computer Science'
    print("\n[Step 17] Django ORM: Course.objects.filter(department__name='Computer Science')")
    sql_query_17 = """
        SELECT course.code, course.name FROM course 
        JOIN department ON course.department_id = department.id 
        WHERE department.name = 'Computer Science';
    """
    cursor.execute(sql_query_17)
    results_17 = cursor.fetchall()
    print("Simulated Result:")
    for row in results_17:
        print(f" - {row[0]}: {row[1]}")

    # Step 18: Department.objects.annotate(course_count=Count('course'))
    print("\n[Step 18] Django ORM: Department.objects.annotate(course_count=Count('course'))")
    sql_query_18 = """
        SELECT department.name, COUNT(course.id) AS course_count 
        FROM department 
        LEFT JOIN course ON department.id = course.department_id 
        GROUP BY department.id;
    """
    cursor.execute(sql_query_18)
    results_18 = cursor.fetchall()
    print("Simulated Result:")
    for row in results_18:
        print(f" - Department: {row[0]}, Course Count: {row[1]}")

    # Step 19: Student.objects.select_related('department')
    print("\n[Step 19] Django ORM: Student.objects.select_related('department')")
    sql_query_19 = """
        SELECT student.first_name, student.last_name, department.name 
        FROM student 
        JOIN department ON student.department_id = department.id;
    """
    cursor.execute(sql_query_19)
    results_19 = cursor.fetchall()
    print("Simulated Result (single query fetching related department):")
    for row in results_19:
        print(f" - Student: {row[0]} {row[1]} | Department: {row[2]}")

    # Step 20: Department.objects.update(budget=F('budget') * 1.1)
    print("\n[Step 20] Django ORM: Department.objects.update(budget=F('budget') * 1.1)")
    cursor.execute("SELECT name, budget FROM department;")
    print("Budgets Before: ", cursor.fetchall())
    
    # Run the F() update equivalent in SQL
    cursor.execute("UPDATE department SET budget = budget * 1.1;")
    conn.commit()
    
    cursor.execute("SELECT name, budget FROM department;")
    print("Budgets After : ", cursor.fetchall())
    print("\n=====================================================================")

if __name__ == "__main__":
    run_orm_simulation()
