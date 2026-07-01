"""
HANDS-ON 8: RESTful API Design Best Practices
This file contains a fully functional FastAPI app demonstrating correct RESTful resource naming,
URL versioning (/api/v1/), HTTP status conventions, Location headers, partial updates via PATCH,
standardized offset pagination, case-insensitive query searching, and standardized JSON error structures.
"""

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional, List, Dict, Any



app = FastAPI(title="RESTful Best Practices API", version="1.0.0")

# =====================================================================
# Standardised Error Response Format (Step 85)
# =====================================================================
# Format: {'error': {'code': 'NOT_FOUND', 'message': 'Course with id 99 does not exist', 'field': null}}

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # Map status codes to standard error codes
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR"
    }
    error_code = code_map.get(exc.status_code, "INTERNAL_ERROR")
    
    # Handle fields for validation errors or defaults
    field = exc.headers.get("X-Error-Field", None) if exc.headers else None
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": error_code,
                "message": exc.detail,
                "field": field
            }
        }
    )

# =====================================================================
# Pydantic Schemas
# =====================================================================

class CourseBase(BaseModel):
    name: str
    code: str
    credits: int
    department_id: int

class CourseCreate(CourseBase):
    pass

class CoursePatch(BaseModel):
    # Step 79: All fields optional for PATCH partial update
    name: Optional[str] = None
    code: Optional[str] = None
    credits: Optional[int] = None
    department_id: Optional[int] = None

class CourseResponse(CourseBase):
    id: int

# =====================================================================
# Database Mock & REST API Endpoints
# =====================================================================

MOCK_COURSES = [
    {"id": 1, "name": "Introduction to Python", "code": "CS-101", "credits": 4, "department_id": 1},
    {"id": 2, "name": "Web Frameworks in Django", "code": "CS-202", "credits": 3, "department_id": 1},
    {"id": 3, "name": "Linear Algebra Foundations", "code": "MATH-201", "credits": 3, "department_id": 2},
    {"id": 4, "name": "Advanced Physics", "code": "PHYS-301", "credits": 4, "department_id": 3},
    {"id": 5, "name": "Quantum Mechanics", "code": "PHYS-302", "credits": 4, "department_id": 3}
]
id_counter = 6

# Step 82: Standard Plural Naming & URL Versioning (/api/v1/courses/)
@app.get('/api/v1/courses/')
async def get_courses_v1(
    request: Request,
    page: int = 1,
    page_size: int = 2,
    search: Optional[str] = None
):
    # Step 84: Case-insensitive search on name and code
    filtered_courses = MOCK_COURSES
    if search:
        search_lower = search.lower()
        filtered_courses = [
            c for c in MOCK_COURSES 
            if search_lower in c["name"].lower() or search_lower in c["code"].lower()
        ]

    total = len(filtered_courses)
    
    # Calculate offset
    start = (page - 1) * page_size
    end = start + page_size
    paginated_results = filtered_courses[start:end]

    # Generate next and previous page URLs
    base_url = str(request.base_url).rstrip('/') + request.scope.get('path', '')
    query_params = []
    if search:
        query_params.append(f"search={search}")
    
    next_url = None
    if end < total:
        next_params = query_params + [f"page={page + 1}", f"page_size={page_size}"]
        next_url = f"{base_url}?{'&'.join(next_params)}"
        
    prev_url = None
    if page > 1 and start <= total:
        prev_params = query_params + [f"page={page - 1}", f"page_size={page_size}"]
        prev_url = f"{base_url}?{'&'.join(prev_params)}"

    # Step 83: Return DRF standard offset pagination envelope
    return {
        "count": total,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results
    }

@app.post('/api/v1/courses/', status_code=status.HTTP_201_CREATED)
async def create_course_v1(course: CourseCreate, response: Response):
    global id_counter
    # Check duplicate
    for existing in MOCK_COURSES:
        if existing["code"] == course.code:
            raise HTTPException(status_code=400, detail="Course code already exists")
            
    new_course = {"id": id_counter, **course.model_dump()}
    MOCK_COURSES.append(new_course)
    id_counter += 1
    
    # Step 81: Add Location response header pointing to the new resource
    response.headers['Location'] = f'/api/v1/courses/{new_course["id"]}/'
    return new_course

@app.get('/api/v1/courses/{id}')
async def get_course_detail_v1(id: int):
    course = next((c for c in MOCK_COURSES if c["id"] == id), None)
    if not course:
        # Step 85: Triggers custom standardised error response
        raise HTTPException(status_code=404, detail=f"Course with id {id} does not exist")
    return course

@app.put('/api/v1/courses/{id}')
async def replace_course_v1(id: int, course: CourseCreate):
    # PUT does a full replacement of the entity
    target = next((c for c in MOCK_COURSES if c["id"] == id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"Course with id {id} does not exist")
    target.update(course.model_dump())
    return target

# Step 79: PATCH endpoint for partial updates
@app.patch('/api/v1/courses/{id}')
async def update_course_partial_v1(id: int, patch_data: CoursePatch):
    target = next((c for c in MOCK_COURSES if c["id"] == id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"Course with id {id} does not exist")
        
    # Update only provided fields
    update_dict = patch_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            target[key] = value
            
    return target

@app.delete('/api/v1/courses/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_course_v1(id: int):
    global MOCK_COURSES
    course = next((c for c in MOCK_COURSES if c["id"] == id), None)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course with id {id} does not exist")
        
    MOCK_COURSES = [c for c in MOCK_COURSES if c["id"] != id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# =====================================================================
# Test Client Verifier
# =====================================================================

def verify_rest_compliance():
    client = TestClient(app)
    print("=====================================================================")
    print("HANDS-ON 8: REST compliance and API verification")
    print("=====================================================================")

    # 1. Test POST creation & Location header
    print("[POST /api/v1/courses/ - Verifying 201 and Location Header]")
    res = client.post('/api/v1/courses/', json={"name": "Compiler Design", "code": "CS-401", "credits": 4, "department_id": 1})
    print(f"Status: {res.status_code}")
    print(f"Location Header: {res.headers.get('Location')}")
    print(f"Body: {res.json()}")

    # 2. Test PATCH partial update
    print("\n[PATCH /api/v1/courses/1/ - Partial update name and credits]")
    res = client.patch('/api/v1/courses/1', json={"name": "Intro to Python v2", "credits": 5})
    print(f"Status: {res.status_code} | Body: {res.json()}")

    # 3. Test Paginated GET response
    print("\n[GET /api/v1/courses/?page=1&page_size=2 - Pagination envelope]")
    res = client.get('/api/v1/courses/?page=1&page_size=2')
    print(f"Status: {res.status_code} | Body: {res.json()}")

    # 4. Test Search GET parameter (case-insensitive LIKE search)
    print("\n[GET /api/v1/courses/?search=djan - Query search filtering]")
    res = client.get('/api/v1/courses/?search=djan')
    print(f"Status: {res.status_code} | Body: {res.json()}")

    # 5. Test 404 Standard Error Response
    print("\n[GET /api/v1/courses/99 - Standardized Error format]")
    res = client.get('/api/v1/courses/99')
    print(f"Status: {res.status_code} | Body: {res.json()}")

    print("\n=====================================================================")

if __name__ == "__main__":
    verify_rest_compliance()
