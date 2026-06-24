

from sqlalchemy.orm import sessionmaker, joinedload
from models import engine, Base, Department, Student, Course, Enrollment, Professor
import datetime

Session = sessionmaker(bind=engine)
session = Session()

def reset_database():
    print("Resetting database schema...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database reset completed successfully.\n")

def run_crud_operations():
    print("Inserting Departments and Students")
    
    dept_cs = Department(dept_name="Computer Science", head_of_dept="Dr. Ramesh Kumar", budget=850000.00)
    dept_el = Department(dept_name="Electronics", head_of_dept="Dr. Priya Nair", budget=620000.00)
    dept_me = Department(dept_name="Mechanical", head_of_dept="Dr. Suresh Iyer", budget=540000.00)
    
    session.add_all([dept_cs, dept_el, dept_me])
    session.commit()
    
    student1 = Student(first_name="Arjun", last_name="Mehta", email="arjun.mehta@college.edu",
                       date_of_birth=datetime.date(2003, 4, 12), department_id=dept_cs.department_id, enrollment_year=2022)
    student2 = Student(first_name="Priya", last_name="Suresh", email="priya.suresh@college.edu",
                       date_of_birth=datetime.date(2003, 7, 25), department_id=dept_cs.department_id, enrollment_year=2022)
    student3 = Student(first_name="Rohan", last_name="Verma", email="rohan.verma@college.edu",
                       date_of_birth=datetime.date(2002, 11, 8), department_id=dept_el.department_id, enrollment_year=2021)
    student4 = Student(first_name="Sneha", last_name="Patel", email="sneha.patel@college.edu",
                       date_of_birth=datetime.date(2004, 1, 30), department_id=dept_me.department_id, enrollment_year=2023)
    student5 = Student(first_name="Vikram", last_name="Das", email="vikram.das@college.edu",
                       date_of_birth=datetime.date(2003, 9, 14), department_id=dept_cs.department_id, enrollment_year=2022)
    
    session.add_all([student1, student2, student3, student4, student5])
    session.commit()
    print("Inserted 3 Departments and 5 Students successfully.\n")

    print("Inserting Courses and Enrollments")
    
    course_dsa = Course(course_name="Data Structures & Algorithms", course_code="CS101", credits=4, department_id=dept_cs.department_id)
    course_db = Course(course_name="Database Management Systems", course_code="CS102", credits=3, department_id=dept_cs.department_id)
    course_circuit = Course(course_name="Circuit Theory", course_code="EC101", credits=3, department_id=dept_el.department_id)
    
    session.add_all([course_dsa, course_db, course_circuit])
    session.commit()
    
    enrollment1 = Enrollment(student_id=student1.student_id, course_id=course_dsa.course_id, enrollment_date=datetime.date(2022, 7, 1), grade="A")
    enrollment2 = Enrollment(student_id=student1.student_id, course_id=course_db.course_id, enrollment_date=datetime.date(2022, 7, 1), grade="B")
    enrollment3 = Enrollment(student_id=student2.student_id, course_id=course_dsa.course_id, enrollment_date=datetime.date(2022, 7, 1), grade="B")
    enrollment4 = Enrollment(student_id=student3.student_id, course_id=course_circuit.course_id, enrollment_date=datetime.date(2021, 7, 1), grade="A")
    
    session.add_all([enrollment1, enrollment2, enrollment3, enrollment4])
    session.commit()
    print("Inserted 3 Courses and 4 Enrollments successfully.\n")

    print("Query Students in 'Computer Science'")
    cs_students = session.query(Student).join(Department).filter(Department.dept_name == "Computer Science").all()
    for student in cs_students:
        print(f"CS Student: {student.first_name} {student.last_name} | Email: {student.email}")
    print()

    print("Querying Enrollments (LAZY LOADING - N+1 DEMO)")
    print("SQL engine query logs will print below:")
    engine.echo = True 
    
    enrollments_lazy = session.query(Enrollment).all()
    print("\nStarting iteration over results (will trigger lazy queries)")
    for enrollment in enrollments_lazy:
        s_name = f"{enrollment.student.first_name} {enrollment.student.last_name}"
        c_name = enrollment.course.course_name
        print(f"Enrollment Info: Student: {s_name} | Course: {c_name} | Grade: {enrollment.grade}")
        
    engine.echo = False
    print("End of lazy iteration\n")

    print("Querying Enrollments (EAGER LOADING - Fixes N+1)")
    print("SQL engine query logs will print below (Notice only ONE join query is issued):")
    engine.echo = True
    
    enrollments_eager = session.query(Enrollment).options(
        joinedload(Enrollment.student), 
        joinedload(Enrollment.course)
    ).all()
    print("\nStarting iteration over eager results (no lazy queries triggered)")
    for enrollment in enrollments_eager:
        s_name = f"{enrollment.student.first_name} {enrollment.student.last_name}"
        c_name = enrollment.course.course_name
        print(f"Eager Enrollment Info: Student: {s_name} | Course: {c_name} | Grade: {enrollment.grade}")
        
    engine.echo = False
    print("End of eager iteration\n")

    print("Updating Student Enrollment Year")
    target_student = session.query(Student).filter(Student.email == "arjun.mehta@college.edu").first()
    if target_student:
        print(f"Before Update: {target_student.first_name} {target_student.last_name} | Enrollment Year: {target_student.enrollment_year}")
        target_student.enrollment_year = 2023
        session.commit()
        
        updated_student = session.query(Student).filter(Student.email == "arjun.mehta@college.edu").first()
        print(f"After Update : {updated_student.first_name} {updated_student.last_name} | Enrollment Year: {updated_student.enrollment_year}")
    print()

    print("Deleting Enrollment Record")
    delete_enrollment = session.query(Enrollment).first()
    if delete_enrollment:
        deleted_id = delete_enrollment.enrollment_id
        student_id = delete_enrollment.student_id
        course_id = delete_enrollment.course_id
        print(f"Deleting Enrollment ID {deleted_id} for Student ID {student_id} and Course ID {course_id}...")
        
        session.delete(delete_enrollment)
        session.commit()
        
        exists = session.query(Enrollment).filter(Enrollment.enrollment_id == deleted_id).first()
        if exists is None:
            print("Verification: Enrollment record successfully deleted.")
        else:
            print("Verification: Deletion failed.")
    print()

if __name__ == "__main__":
    reset_database()
    run_crud_operations()
