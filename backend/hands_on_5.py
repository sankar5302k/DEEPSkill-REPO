"""
HANDS-ON 5: Flask with SQLAlchemy ORM & Database Integration
This file provides a fully functional, runnable Flask application integrated with
SQLAlchemy using an in-memory SQLite database. It implements the database models,
relationships, to_dict() helpers, database queries, and custom endpoints.
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date

# Initialize extension (usually done globally and imported)
db = SQLAlchemy()

# =====================================================================
# PART 1: Database Models Definition
# =====================================================================

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    head_of_dept = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False)

    # Relationships
    courses = db.relationship('Course', back_populates='department', cascade='all, delete-orphan')
    students = db.relationship('Student', back_populates='department', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "head_of_dept": self.head_of_dept,
            "budget": self.budget
        }

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)

    # Relationships
    department = db.relationship('Department', back_populates='courses')
    enrollments = db.relationship('Enrollment', back_populates='course', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "credits": self.credits,
            "department_id": self.department_id
        }

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    enrollment_year = db.Column(db.Integer, nullable=False)

    # Relationships
    department = db.relationship('Department', back_populates='students')
    enrollments = db.relationship('Enrollment', back_populates='student', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "department_id": self.department_id,
            "enrollment_year": self.enrollment_year
        }

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False, default=date.today)
    grade = db.Column(db.String(2), nullable=True)

    # Relationships
    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

    # Unique constraint
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='_student_course_uc'),)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "enrollment_date": self.enrollment_date.isoformat(),
            "grade": self.grade
        }

# =====================================================================
# PART 2: Application Factory and Route Handlers
# =====================================================================

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extension
    db.init_app(app)

    # Custom responses envelope helper
    def make_response_json(data, status_code=200):
        return jsonify({
            "status": "success",
            "data": data
        }), status_code

    # --- API Routes ---

    @app.route('/api/courses/', methods=['GET'])
    def get_courses():
        # Step 52: Query course records and serialize
        courses = Course.query.all()
        return jsonify([c.to_dict() for c in courses])

    @app.route('/api/courses/', methods=['POST'])
    def create_course():
        # Step 54: Parse data, create object, add and commit
        data = request.get_json()
        if not data or not all(k in data for k in ('name', 'code', 'credits', 'department_id')):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
            
        course = Course(
            name=data['name'],
            code=data['code'],
            credits=data['credits'],
            department_id=data['department_id']
        )
        db.session.add(course)
        db.session.commit()
        return make_response_json(course.to_dict(), 201)

    @app.route('/api/courses/<int:id>/', methods=['GET'])
    def get_course_detail(id):
        # Step 55: Query using get_or_404
        course = Course.query.get_or_404(id)
        return make_response_json(course.to_dict())

    @app.route('/api/courses/<int:id>/', methods=['PUT'])
    def update_course(id):
        course = Course.query.get_or_404(id)
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Missing payload"}), 400

        course.name = data.get('name', course.name)
        course.code = data.get('code', course.code)
        course.credits = data.get('credits', course.credits)
        course.department_id = data.get('department_id', course.department_id)
        
        db.session.commit()
        return make_response_json(course.to_dict())

    @app.route('/api/courses/<int:id>/', methods=['DELETE'])
    def delete_course(id):
        course = Course.query.get_or_404(id)
        db.session.delete(course)
        db.session.commit()
        return make_response_json({"deleted_id": id})

    @app.route('/api/courses/<int:id>/students/', methods=['GET'])
    def get_course_students(id):
        # Step 56: Query enrolled students using a JOIN query
        # Fetch all students joined with enrollments for the given course
        students = db.session.query(Student).join(Enrollment).filter(Enrollment.course_id == id).all()
        return make_response_json([s.to_dict() for s in students])

    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    return app

# =====================================================================
# PART 3: Seeding and Testing Runner
# =====================================================================

def run_db_tests():
    app = create_app()
    
    with app.app_context():
        # Initialize tables
        db.create_all()

        # Step 51: Seed 2 departments and 3 courses
        print("=====================================================================")
        print("HANDS-ON 5: Flask SQLAlchemy Database Integration Tests")
        print("=====================================================================")
        print("Seeding SQLite database...")
        
        dept1 = Department(name="Computer Science", head_of_dept="Dr. Turing", budget=120000.0)
        dept2 = Department(name="Physics", head_of_dept="Dr. Feynman", budget=90000.0)
        db.session.add_all([dept1, dept2])
        db.session.commit() # Save to generate IDs

        c1 = Course(name="Data Structures", code="CS-201", credits=4, department_id=dept1.id)
        c2 = Course(name="Algorithms", code="CS-301", credits=4, department_id=dept1.id)
        c3 = Course(name="Quantum Mechanics", code="PHYS-101", credits=3, department_id=dept2.id)
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        # Seed students and enrollments to test JOIN route
        student1 = Student(first_name="Alice", last_name="Wonderland", email="alice@test.com", department_id=dept1.id, enrollment_year=2025)
        student2 = Student(first_name="Bob", last_name="Builder", email="bob@test.com", department_id=dept1.id, enrollment_year=2025)
        db.session.add_all([student1, student2])
        db.session.commit()

        enrollment1 = Enrollment(student_id=student1.id, course_id=c1.id, grade="A")
        enrollment2 = Enrollment(student_id=student2.id, course_id=c1.id, grade="B")
        db.session.add_all([enrollment1, enrollment2])
        db.session.commit()

        print("Database seeded with departments, courses, students, and enrollments.")

        # Test utilizing Flask Test Client
        client = app.test_client()

        # Get all courses
        print("\n[GET /api/courses/]")
        res = client.get('/api/courses/')
        print(f"Body: {res.get_data(as_text=True)}")

        # Create a new course
        print("\n[POST /api/courses/ - Create New Course]")
        res = client.post('/api/courses/', json={"name": "Compiler Design", "code": "CS-401", "credits": 4, "department_id": dept1.id})
        print(f"Status: {res.status_code} | Body: {res.get_data(as_text=True)}")

        # Get course detail
        print("\n[GET /api/courses/1/]")
        res = client.get('/api/courses/1/')
        print(f"Body: {res.get_data(as_text=True)}")

        # Get enrolled students via JOIN route
        print("\n[GET /api/courses/1/students/ - Testing JOIN]")
        res = client.get('/api/courses/1/students/')
        print(f"Body: {res.get_data(as_text=True)}")

        print("\n=====================================================================")

if __name__ == "__main__":
    run_db_tests()
