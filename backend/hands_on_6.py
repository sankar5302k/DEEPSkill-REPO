"""
HANDS-ON 6: FastAPI — Path Parameters, Pydantic & Async Endpoints
This file provides a complete, runnable FastAPI application implementing
Pydantic validation schemas, nested schemas, async routes, query parameter
filtering/pagination, and simulated async database dependency injection.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import List, Optional
import asyncio

# =====================================================================
# PART 1: Pydantic Schemas (schemas.py equivalent)
# =====================================================================

class CourseBase(BaseModel):
    name: str
    code: str
    credits: int
    department_id: int

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    # Step 58: CourseUpdate (all fields optional)
    name: Optional[str] = None
    code: Optional[str] = None
    credits: Optional[int] = None
    department_id: Optional[int] = None

class CourseResponse(CourseBase):
    id: int

    class Config:
        from_attributes = True  # Allows mapping ORM attributes to Pydantic

class DepartmentResponse(BaseModel):
    id: int
    name: str
    head_of_dept: str
    budget: float
    # Step 59: Nested Pydantic schemas list
    courses: List[CourseResponse] = []

    class Config:
        from_attributes = True

# =====================================================================
# PART 2: Database Setup & Async Dependency (database.py equivalent)
# =====================================================================

# Mock async database store
MOCK_COURSES = [
    {"id": 1, "name": "Introduction to Computer Science", "code": "CS-101", "credits": 4, "department_id": 1},
    {"id": 2, "name": "Data Structures & Algorithms", "code": "CS-201", "credits": 4, "department_id": 1},
    {"id": 3, "name": "Linear Algebra", "code": "MATH-201", "credits": 3, "department_id": 2}
]
course_counter = 4

# Simulate an Async Database Session
class MockAsyncSession:
    async def execute_select_all(self, skip: int, limit: int, dept_id: Optional[int]):
        await asyncio.sleep(0.01) # Simulate async I/O latency
        results = MOCK_COURSES
        if dept_id is not None:
            results = [c for c in results if c["department_id"] == dept_id]
        return results[skip : skip + limit]

    async def execute_select_by_id(self, course_id: int):
        await asyncio.sleep(0.01)
        return next((c for c in MOCK_COURSES if c["id"] == course_id), None)

    async def execute_insert(self, course_data: CourseCreate):
        global course_counter
        await asyncio.sleep(0.01)
        new_course = {
            "id": course_counter,
            **course_data.model_dump()
        }
        MOCK_COURSES.append(new_course)
        course_counter += 1
        return new_course

# Step 64 & 65: Dependency function yielding an async session
async def get_db():
    db = MockAsyncSession()
    try:
        yield db
    finally:
        pass  # Close/cleanup session if needed

# =====================================================================
# PART 3: FastAPI Application Definitions
# =====================================================================

# Step 57: Initialize FastAPI App
app = FastAPI(title="Course Management API", version="1.0")

@app.get('/')
async def root():
    return {"message": "API running"}

# Step 60: POST /api/courses/
@app.post('/api/courses/', response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(course: CourseCreate, db: MockAsyncSession = Depends(get_db)):
    # Pydantic validates input schemas automatically
    # Check for duplicate code
    for existing in MOCK_COURSES:
        if existing["code"] == course.code:
            raise HTTPException(status_code=400, detail="Course code already exists")
    
    new_course = await db.execute_insert(course)
    return new_course

# Step 63: GET /api/courses/ with skip, limit, and department_id query params
@app.get('/api/courses/', response_model=List[CourseResponse])
async def get_courses(
    skip: int = 0,
    limit: int = 10,
    department_id: Optional[int] = None,
    db: MockAsyncSession = Depends(get_db)
):
    courses = await db.execute_select_all(skip=skip, limit=limit, dept_id=department_id)
    return courses

# Step 62: GET /api/courses/{course_id}
@app.get('/api/courses/{course_id}', response_model=CourseResponse)
async def get_course(course_id: int, db: MockAsyncSession = Depends(get_db)):
    course = await db.execute_select_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# =====================================================================
# PART 4: FastAPI Test Suite / Execution
# =====================================================================

def run_fastapi_tests():
    client = TestClient(app)
    print("=====================================================================")
    print("HANDS-ON 6: FastAPI Route Validation & Query Parameters Tests")
    print("=====================================================================")
    
    # 1. Test Root
    res = client.get('/')
    print(f"Root: {res.json()}")

    # 2. Test Get All Courses
    print("\n[GET /api/courses/ - All]")
    res = client.get('/api/courses/')
    print(f"Status: {res.status_code} | Body: {res.json()}")

    # 3. Test Query Filtering & Pagination: skip=1, limit=2
    print("\n[GET /api/courses/?skip=1&limit=2 - Pagination]")
    res = client.get('/api/courses/?skip=1&limit=2')
    print(f"Status: {res.status_code} | Body: {res.json()}")

    # 4. Test Query Filtering: department_id=2
    print("\n[GET /api/courses/?department_id=2 - Filtering]")
    res = client.get('/api/courses/?department_id=2')
    print(f"Status: {res.status_code} | Body: {res.json()}")

    # 5. Test Get Course Detail
    print("\n[GET /api/courses/2]")
    res = client.get('/api/courses/2')
    print(f"Status: {res.status_code} | Body: {res.json()}")

    # 6. Test Create Course
    print("\n[POST /api/courses/ - Success]")
    payload = {"name": "Operating Systems", "code": "CS-302", "credits": 4, "department_id": 1}
    res = client.post('/api/courses/', json=payload)
    print(f"Status: {res.status_code} | Body: {res.json()}")

    # 7. Test Pydantic Validation Error (Missing Field)
    print("\n[POST /api/courses/ - Missing field (Should fail with 422)]")
    res = client.post('/api/courses/', json={"name": "Faulty Course"})
    print(f"Status: {res.status_code} | Body: {res.json()}")

    print("\n=====================================================================")

if __name__ == "__main__":
    run_fastapi_tests()
