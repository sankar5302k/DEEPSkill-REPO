from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric, Boolean, Time, create_engine
from sqlalchemy.orm import declarative_base, relationship
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_USER = "postgres"
DB_PASSWORD = "varadharaja"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "college_db_orm"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)

Base = declarative_base()


class Department(Base):
    __tablename__ = 'departments'
    
    department_id = Column(Integer, primary_key=True, autoincrement=True)
    dept_name = Column(String(100), nullable=False)
    head_of_dept = Column(String(100))  
    budget = Column(Numeric(12, 2))
    
    students = relationship("Student", back_populates="department")
    courses = relationship("Course", back_populates="department")
    professors = relationship("Professor", back_populates="department")

class Student(Base):
    __tablename__ = 'students'
    
    student_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    date_of_birth = Column(Date)
    department_id = Column(Integer, ForeignKey('departments.department_id', ondelete='SET NULL'))
    enrollment_year = Column(Integer)
    
    is_active = Column(Boolean, default=True, server_default='true')
    
    department = relationship("Department", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = 'courses'
    
    course_id = Column(Integer, primary_key=True, autoincrement=True)
    course_name = Column(String(150), nullable=False)
    course_code = Column(String(20), unique=True)
    credits = Column(Integer)
    department_id = Column(Integer, ForeignKey('departments.department_id', ondelete='CASCADE'))
    max_seats = Column(Integer, default=60)  
    
    department = relationship("Department", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    schedules = relationship("CourseSchedule", back_populates="course", cascade="all, delete-orphan")

class Enrollment(Base):
    __tablename__ = 'enrollments'
    
    enrollment_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    enrollment_date = Column(Date)
    grade = Column(String(2))
    
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Professor(Base):
    __tablename__ = 'professors'
    
    professor_id = Column(Integer, primary_key=True, autoincrement=True)
    prof_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    department_id = Column(Integer, ForeignKey('departments.department_id', ondelete='SET NULL'))
    salary = Column(Numeric(10, 2))
    
    department = relationship("Department", back_populates="professors")

class CourseSchedule(Base):
    __tablename__ = 'course_schedules'
    
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.course_id', ondelete='CASCADE'), nullable=False)
    day_of_week = Column(String(20), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    course = relationship("Course", back_populates="schedules")


def create_database_if_not_exists():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Database '{DB_NAME}' does not exist. Creating database in PostgreSQL...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database '{DB_NAME}' created successfully.")
        else:
            print(f"Database '{DB_NAME}' already exists.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database verification warning: {e}")
        print("Continuing model generation; connection will verify database structure directly.")

if __name__ == "__main__":
    create_database_if_not_exists()
    
    print("Creating tables in database college_db_orm...")
    Base.metadata.create_all(engine)
    print("All tables created successfully.")
