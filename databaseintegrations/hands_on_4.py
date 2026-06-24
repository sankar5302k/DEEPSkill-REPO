import psycopg2
import time


DB_CONFIG = {
    "dbname": "college_db",
    "user": "postgres",
    "password": "varadharaja",  
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        print(f"[Error] Could not connect to the database: {e}")
        print("Please verify that PostgreSQL is running and connection details in DB_CONFIG are correct.\n")
        return None

def run_n_plus_1_simulation():
    print()
    print("Executing Approach 1: Simulating the N+1 Query Problem")
    print()
    
    conn = get_connection()
    if not conn:
        return None, 0, 0
    
    cursor = conn.cursor()
    query_count = 0
    start_time = time.time()
    
    try:
        cursor.execute("SELECT enrollment_id, student_id, course_id, grade FROM enrollments;")
        enrollments = cursor.fetchall()
        query_count += 1
        
        results = []
        for enrollment in enrollments:
            enrollment_id, student_id, course_id, grade = enrollment
            
            cursor.execute("SELECT first_name, last_name FROM students WHERE student_id = %s;", (student_id,))
            student = cursor.fetchone()
            query_count += 1
            
            student_name = f"{student[0]} {student[1]}" if student else "Unknown"
            results.append({
                "enrollment_id": enrollment_id,
                "student_name": student_name,
                "course_id": course_id,
                "grade": grade
            })
            
        execution_time = time.time() - start_time
        print(f"Sample Row: {results[0] if results else 'No data'}")
        print(f"Queries Executed: {query_count}")
        print(f"Execution Time: {execution_time:.6f} seconds")
        return results, query_count, execution_time
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, 0, 0
    finally:
        cursor.close()
        conn.close()

def run_optimized_join():
    print()
    print("Executing Approach 2: Optimised JOIN Query")
    print()
    
    conn = get_connection()
    if not conn:
        return None, 0, 0
    
    cursor = conn.cursor()
    query_count = 0
    start_time = time.time()
    
    try:
        join_query = """
            SELECT e.enrollment_id, (s.first_name || ' ' || s.last_name) AS student_name, e.course_id, e.grade
            FROM enrollments e
            INNER JOIN students s ON e.student_id = s.student_id;
        """
        cursor.execute(join_query)
        enrollments_with_names = cursor.fetchall()
        query_count += 1
        
        results = []
        for row in enrollments_with_names:
            enrollment_id, student_name, course_id, grade = row
            results.append({
                "enrollment_id": enrollment_id,
                "student_name": student_name,
                "course_id": course_id,
                "grade": grade
            })
            
        execution_time = time.time() - start_time
        print(f"Sample Row: {results[0] if results else 'No data'}")
        print(f"Queries Executed: {query_count}")
        print(f"Execution Time: {execution_time:.6f} seconds")
        return results, query_count, execution_time
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, 0, 0
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("N+1 Query Problem Demonstration and Comparison")
    
    n1_results, n1_queries, n1_time = run_n_plus_1_simulation()
    
    opt_results, opt_queries, opt_time = run_optimized_join()
    
    if n1_results and opt_results:
        print()
        print("PERFORMANCE COMPARISON SUMMARY")
        print()
        print(f"N+1 Approach Queries  : {n1_queries}")
        print(f"Optimised JOIN Queries: {opt_queries}")
        print(f"Query Reduction       : {n1_queries - opt_queries} queries saved ({(n1_queries - opt_queries) / n1_queries * 100:.1f}%)")
        print()
        print(f"N+1 Execution Time    : {n1_time:.6f} seconds")
        print(f"Optimised JOIN Time   : {opt_time:.6f} seconds")
        time_saved = n1_time - opt_time
        if time_saved > 0:
            print(f"Speedup Factor        : {n1_time / opt_time:.2f}x faster using JOIN")
        print()
        
    if n1_results and opt_results and len(n1_results) == len(opt_results):
        print("Data Verification: PASSED (Both approaches returned identical row counts)")
    else:
        print("Data Verification: FAILED or Database Connection Unavailable")


# Step 59: Documentation

# Question: In a real application with 10,000 enrollments, how many extra 
#           queries would the N+1 version issue?
#
# Answer:
# In the N+1 query version, the application first executes 1 query to fetch 
# all 10,000 enrollment records. Then, it loops through each enrollment row 
# and fires 1 separate query to fetch the related student name for each record.
#
# - N+1 Queries: 1 (initial query) + 10,000 (individual student queries) 
#                = 10,001 total queries.
# - JOIN Query : 1 query total.
#
# - Extra Queries Issued: 10,000 extra queries.
#
# Impact:
# 10,000 extra queries create significant network latency overhead, transaction 
# initialization load on the database engine, and connection pool saturation. 
# Using a single JOIN reduces the database round-trips from 10,001 to 1.