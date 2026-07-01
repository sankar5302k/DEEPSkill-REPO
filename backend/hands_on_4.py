"""
HANDS-ON 4: Flask — App Structure, Routing, Jinja2 & Blueprints
This is a fully functional, self-contained Flask application implementing
the application factory pattern, custom configuration, blueprints, JSON response formatting,
and custom error handling.
"""

from flask import Flask, Blueprint, request, jsonify

# =====================================================================
# PART 1: Config Definition (config.py equivalent)
# =====================================================================

class Config:
    SECRET_KEY = 'super-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
    TESTING = True

# =====================================================================
# PART 2: Blueprints & Routes Definition (courses/routes.py equivalent)
# =====================================================================

courses_bp = Blueprint('courses', __name__, url_prefix='/api/courses')

# In-memory mock database for courses
mock_courses_db = [
    {"id": 1, "name": "Introduction to Python", "code": "PY101", "credits": 4},
    {"id": 2, "name": "Web Development with Flask", "code": "FLK201", "credits": 3}
]
course_id_counter = 3

# JSON response helper
def make_response_json(data, status_code=200):
    return jsonify({
        "status": "success",
        "data": data
    }), status_code

@courses_bp.route('/', methods=['GET'])
def get_courses():
    # Returns empty or populated course list (Step 41)
    return jsonify(mock_courses_db)

@courses_bp.route('/', methods=['POST'])
def create_course():
    global course_id_counter
    # Step 42: Parse & validate request body
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON request payload"}), 400
        
    required_fields = ['name', 'code', 'credits']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "status": "error", 
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    new_course = {
        "id": course_id_counter,
        "name": data["name"],
        "code": data["code"],
        "credits": data["credits"]
    }
    mock_courses_db.append(new_course)
    course_id_counter += 1
    
    return make_response_json(new_course, 201)

@courses_bp.route('/<int:course_id>/', methods=['GET'])
def get_course_detail(course_id):
    course = next((c for c in mock_courses_db if c["id"] == course_id), None)
    if not course:
        return jsonify({"status": "error", "message": "Course not found"}), 404
    return make_response_json(course)

@courses_bp.route('/<int:course_id>/', methods=['PUT'])
def update_course(course_id):
    course = next((c for c in mock_courses_db if c["id"] == course_id), None)
    if not course:
        return jsonify({"status": "error", "message": "Course not found"}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON request payload"}), 400

    course["name"] = data.get("name", course["name"])
    course["code"] = data.get("code", course["code"])
    course["credits"] = data.get("credits", course["credits"])
    
    return make_response_json(course)

@courses_bp.route('/<int:course_id>/', methods=['DELETE'])
def delete_course(course_id):
    global mock_courses_db
    course = next((c for c in mock_courses_db if c["id"] == course_id), None)
    if not course:
        return jsonify({"status": "error", "message": "Course not found"}), 404
        
    mock_courses_db = [c for c in mock_courses_db if c["id"] != course_id]
    return make_response_json({"deleted_id": course_id})

# =====================================================================
# PART 3: Application Factory Pattern (app.py equivalent)
# =====================================================================

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register blueprint
    app.register_blueprint(courses_bp)

    # Step 45: Custom JSON Error Handlers
    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify({
            "status": "error",
            "message": "The requested resource could not be found."
        }), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred."
        }), 500

    return app

def run_flask_tests():
    app = create_app()
    client = app.test_client()

    print("=====================================================================")
    print("HANDS-ON 4: Flask App Simulation & Testing")
    print("=====================================================================")
    
    # Test GET /api/courses/
    print("\n[GET /api/courses/]")
    res = client.get('/api/courses/')
    print(f"Status: {res.status_code} | Body: {res.get_data(as_text=True)}")

    # Test POST /api/courses/ with missing fields
    print("\n[POST /api/courses/ - Missing Fields]")
    res = client.post('/api/courses/', json={"name": "Software Engineering"})
    print(f"Status: {res.status_code} | Body: {res.get_data(as_text=True)}")

    # Test POST /api/courses/ success
    print("\n[POST /api/courses/ - Success]")
    res = client.post('/api/courses/', json={"name": "Database Systems", "code": "DB301", "credits": 4})
    print(f"Status: {res.status_code} | Body: {res.get_data(as_text=True)}")

    # Test GET /api/courses/<id>/
    print("\n[GET /api/courses/3/]")
    res = client.get('/api/courses/3/')
    print(f"Status: {res.status_code} | Body: {res.get_data(as_text=True)}")

    # Test GET non-existent course
    print("\n[GET /api/courses/99/ (404 Error handler)]")
    res = client.get('/api/courses/99/')
    print(f"Status: {res.status_code} | Body: {res.get_data(as_text=True)}")

    print("\n=====================================================================")

if __name__ == "__main__":
    run_flask_tests()
