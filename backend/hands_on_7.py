"""
HANDS-ON 7: FastAPI — Dependency Injection, CRUD & OpenAPI Documentation
This file provides a complete, runnable FastAPI application with full CRUD for
Courses, Students, and Enrollments, customized OpenAPI documentation (tags,
descriptions, summary, metadata), and BackgroundTasks support.
"""

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

# =====================================================================
# PART 1: Pydantic Schemas & OpenAPI Customization Configuration
# =====================================================================

class CourseBase(BaseModel):
    name: str
    code: str
    credits: int
    department_id: int

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    department_id: int
    enrollment_year: int

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    class Config:
        from_attributes = True

class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int
    grade: Optional[str] = None

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentResponse(EnrollmentBase):
    id: int
    enrollment_date: date
    class Config:
        from_attributes = True

# =====================================================================
# PART 2: Database Store & CRUD Helpers
# =====================================================================

# In-memory database lists
DB_COURSES = [
    {"id": 1, "name": "Software Engineering", "code": "CS-301", "credits": 4, "department_id": 1}
]
DB_STUDENTS = [
    {"id": 1, "first_name": "John", "last_name": "Doe", "email": "john@college.edu", "department_id": 1, "enrollment_year": 2025}
]
DB_ENROLLMENTS = []

course_id_gen = 2
student_id_gen = 2
enrollment_id_gen = 1

# Background task function
def send_confirmation_email(student_email: str):
    # Simulated background task (Step 73)
    print(f"\n[BACKGROUND TASK] Sending confirmation to {student_email}...")

# =====================================================================
# PART 3: FastAPI Application Setup with OpenAPI Metadata
# =====================================================================

# Step 75: Customise OpenAPI metadata in FastAPI() constructor
app = FastAPI(
    title="College Management API",
    description="A RESTful API to manage course registrations, students records, and enrollments with background email notifications.",
    version="2.0.0",
    contact={
        "name": "API Support Team",
        "email": "support@college.edu"
    }
)

# --- Courses Endpoints (Tag: Courses) ---

@app.get('/api/courses/', response_model=List[CourseResponse], tags=['Courses'])
async def list_courses():
    return DB_COURSES

@app.post('/api/courses/', 
          response_model=CourseResponse, 
          status_code=status.HTTP_201_CREATED, 
          tags=['Courses'],
          summary="Create a new course",
          response_description="The course has been successfully created.")
async def create_course(course: CourseCreate):
    global course_id_gen
    for existing in DB_COURSES:
        if existing["code"] == course.code:
            raise HTTPException(status_code=400, detail="Course code already exists")
    
    new_course = {"id": course_id_gen, **course.model_dump()}
    DB_COURSES.append(new_course)
    course_id_gen += 1
    return new_course

@app.get('/api/courses/{id}', response_model=CourseResponse, tags=['Courses'])
async def get_course(id: int):
    course = next((c for c in DB_COURSES if c["id"] == id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.put('/api/courses/{id}', response_model=CourseResponse, tags=['Courses'])
async def update_course(id: int, course: CourseCreate):
    target = next((c for c in DB_COURSES if c["id"] == id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Course not found")
    
    target.update(course.model_dump())
    return target

@app.delete('/api/courses/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Courses'])
async def delete_course(id: int):
    global DB_COURSES
    course = next((c for c in DB_COURSES if c["id"] == id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    DB_COURSES = [c for c in DB_COURSES if c["id"] != id]
    return None

# Step 71: GET /api/courses/{id}/students/ using JOIN logic
@app.get('/api/courses/{id}/students/', response_model=List[StudentResponse], tags=['Courses'])
async def get_course_students(id: int):
    # Verify course exists
    course = next((c for c in DB_COURSES if c["id"] == id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Get student IDs from enrollments
    student_ids = [e["student_id"] for e in DB_ENROLLMENTS if e["course_id"] == id]
    enrolled_students = [s for s in DB_STUDENTS if s["id"] in student_ids]
    return enrolled_students

# --- Students Endpoints (Tag: Students) ---

@app.get('/api/students/', response_model=List[StudentResponse], tags=['Students'])
async def list_students():
    return DB_STUDENTS

@app.post('/api/students/', response_model=StudentResponse, status_code=status.HTTP_201_CREATED, tags=['Students'])
async def create_student(student: StudentCreate):
    global student_id_gen
    for existing in DB_STUDENTS:
        if existing["email"] == student.email:
            raise HTTPException(status_code=400, detail="Student email already exists")
            
    new_student = {"id": student_id_gen, **student.model_dump()}
    DB_STUDENTS.append(new_student)
    student_id_gen += 1
    return new_student

@app.get('/api/students/{id}', response_model=StudentResponse, tags=['Students'])
async def get_student(id: int):
    student = next((s for s in DB_STUDENTS if s["id"] == id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put('/api/students/{id}', response_model=StudentResponse, tags=['Students'])
async def update_student(id: int, student: StudentCreate):
    target = next((s for s in DB_STUDENTS if s["id"] == id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Student not found")
    target.update(student.model_dump())
    return target

@app.delete('/api/students/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Students'])
async def delete_student(id: int):
    global DB_STUDENTS
    student = next((s for s in DB_STUDENTS if s["id"] == id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    DB_STUDENTS = [s for s in DB_STUDENTS if s["id"] != id]
    return None

# --- Enrollments Endpoints (Tag: Enrollments) ---

@app.post('/api/enrollments/', response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED, tags=['Enrollments'])
async def create_enrollment(enrollment: EnrollmentCreate, background_tasks: BackgroundTasks):
    global enrollment_id_gen
    # Check if student exists
    student = next((s for s in DB_STUDENTS if s["id"] == enrollment.student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Check if course exists
    course = next((c for c in DB_COURSES if c["id"] == enrollment.course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Check for duplicate enrollment
    for existing in DB_ENROLLMENTS:
        if existing["student_id"] == enrollment.student_id and existing["course_id"] == enrollment.course_id:
            raise HTTPException(status_code=400, detail="Student is already enrolled in this course")

    new_enrollment = {
        "id": enrollment_id_gen,
        "student_id": enrollment.student_id,
        "course_id": enrollment.course_id,
        "enrollment_date": date.today(),
        "grade": enrollment.grade
    }
    DB_ENROLLMENTS.append(new_enrollment)
    enrollment_id_gen += 1
    
    # Step 73: Add background task to simulate confirmation email
    background_tasks.add_task(send_confirmation_email, student["email"])
    
    return new_enrollment

# =====================================================================
# PART 4: FastAPI Test Suite / Execution
# =====================================================================

def run_fastapi_tests():
    client = TestClient(app)
    print("=====================================================================")
    print("HANDS-ON 7: FastAPI CRUD & BackgroundTasks Verification")
    print("=====================================================================")

    # Test GET Courses
    print("[GET /api/courses/]")
    print(client.get('/api/courses/').json())

    # Test POST Courses
    print("\n[POST /api/courses/]")
    print(client.post('/api/courses/', json={"name": "Compiler Design", "code": "CS-401", "credits": 4, "department_id": 1}).json())

    # Test GET Enrolled Students (Should be empty initially)
    print("\n[GET /api/courses/1/students/ - Enrolled students (Empty)]")
    print(client.get('/api/courses/1/students/').json())

    # Test POST Enrollments with BackgroundTasks triggering
    print("\n[POST /api/enrollments/ - Create enrollment (Triggers Background Email)]")
    res = client.post('/api/enrollments/', json={"student_id": 1, "course_id": 1, "grade": "A"})
    print(f"Status: {res.status_code} | Body: {res.json()}")

    # Test GET Enrolled Students (Should show John Doe now)
    print("\n[GET /api/courses/1/students/ - Enrolled students (Should show John Doe)]")
    print(client.get('/api/courses/1/students/').json())

    # Test DELETE Course with 204 status code check
    print("\n[DELETE /api/courses/2 - Delete course 2]")
    res = client.delete('/api/courses/2')
    print(f"Status (Expect 204): {res.status_code}")

    print("\n=====================================================================")

if __name__ == "__main__":
    run_fastapi_tests()
