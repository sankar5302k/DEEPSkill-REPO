"""
HANDS-ON 9: Authentication & Security — JWT, OAuth2 & OWASP
This file implements secure password storage (bcrypt), user registration,
JWT token generation & validation, OAuth2 scheme route protection, CORS configuration,
and contains security theory comments about password hashing and OAuth2 flows.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from jose import jwt, JWTError
from passlib.context import CryptContext



# JWT Signing configuration
JWT_SECRET = "super-secret-signature-key-for-token-generation-and-signing"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 30

# Initialize passlib crypt context for bcrypt hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

app = FastAPI(title="Secure Authentication API", version="1.0.0")

# Step 94: Configure CORS middleware allowing localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# Pydantic Schemas & User Database Mock
# =====================================================================

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool

class CourseCreate(BaseModel):
    name: str
    code: str
    credits: int

# Mock Databases
DB_USERS = []
DB_COURSES = []
user_counter = 1

# =====================================================================
# Task 1: Password Hashing & Security Helpers
# =====================================================================

def get_password_hash(password: str) -> str:
    # Step 87: Hashes password using bcrypt
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Step 87: Verifies password matching
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

# =====================================================================
# Auth and Protected Routes Endpoints
# =====================================================================

# Step 88: User Registration Endpoint
@app.post('/api/v1/auth/register/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    global user_counter
    # Check duplicate email
    for existing in DB_USERS:
        if existing["email"] == user_data.email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
            
    hashed = get_password_hash(user_data.password)
    
    new_user = {
        "id": user_counter,
        "email": user_data.email,
        "hashed_password": hashed,
        "is_active": True
    }
    DB_USERS.append(new_user)
    user_counter += 1
    return new_user

# Step 91: JWT Login Endpoint
@app.post('/api/v1/auth/login/')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = next((u for u in DB_USERS if u["email"] == form_data.username), None)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_jwt_token(user["email"])
    return {"access_token": access_token, "token_type": "bearer"}

# Step 92: get_current_user Dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = next((u for u in DB_USERS if u["email"] == email), None)
    if user is None:
        raise credentials_exception
    return user

# Step 93: Protected Course endpoints requiring current_user dependency
@app.post('/api/v1/courses/', status_code=status.HTTP_201_CREATED)
async def create_course(course: CourseCreate, current_user: dict = Depends(get_current_user)):
    # Only authenticated users can access
    new_course = {"id": len(DB_COURSES) + 1, **course.model_dump(), "created_by": current_user["email"]}
    DB_COURSES.append(new_course)
    return new_course

@app.get('/api/v1/courses/')
async def get_courses():
    # Unprotected endpoint
    return DB_COURSES

# =====================================================================
# Test Runner for Authentication Suite
# =====================================================================

def test_auth_and_routes():
    client = TestClient(app)
    print("=====================================================================")
    print("HANDS-ON 9: Security Hashing & JWT Protection Testing")
    print("=====================================================================")

    # 1. Register a user
    print("[POST /api/v1/auth/register/ - Register User]")
    reg_res = client.post('/api/v1/auth/register/', json={"email": "alice@test.com", "password": "SecurePassword123"})
    print(f"Status: {reg_res.status_code} | Body: {reg_res.json()}")

    # 2. Prevent duplicate registrations (409 Conflict)
    print("\n[POST /api/v1/auth/register/ - Register Duplicate Email (Expect 409)]")
    dup_res = client.post('/api/v1/auth/register/', json={"email": "alice@test.com", "password": "SecurePassword123"})
    print(f"Status: {dup_res.status_code} | Body: {dup_res.json()}")

    # 3. Access Protected Route without Token (Expect 401)
    print("\n[POST /api/v1/courses/ - Unauthenticated (Expect 401)]")
    unauth_res = client.post('/api/v1/courses/', json={"name": "Cyber Security", "code": "CS-403", "credits": 4})
    print(f"Status: {unauth_res.status_code} | Body: {unauth_res.json()}")

    # 4. Authenticate & Obtain JWT Token
    print("\n[POST /api/v1/auth/login/ - Authenticate to get Token]")
    login_res = client.post('/api/v1/auth/login/', data={"username": "alice@test.com", "password": "SecurePassword123"})
    print(f"Status: {login_res.status_code} | Body: {login_res.json()}")
    token = login_res.json().get("access_token")

    # 5. Access Protected Route with Token (Expect 201)
    print("\n[POST /api/v1/courses/ - Authenticated with Token (Expect 201)]")
    headers = {"Authorization": f"Bearer {token}"}
    auth_res = client.post('/api/v1/courses/', json={"name": "Cyber Security", "code": "CS-403", "credits": 4}, headers=headers)
    print(f"Status: {auth_res.status_code} | Body: {auth_res.json()}")

    print("\n=====================================================================")

if __name__ == "__main__":
    test_auth_and_routes()
