"""
HANDS-ON 3: Django REST Views, URL Routing & Forms
This file contains the declarations for Django REST Framework (DRF) serializers,
views, viewsets, custom action annotations, and routers configuration.
"""

# =====================================================================
# PART 1: Serializers Declaration (courses/serializers.py)
# =====================================================================

DJANGO_SERIALIZERS_PY = """
# courses/serializers.py
from rest_framework import serializers
from .models import Department, Course, Student, Enrollment

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
"""

# =====================================================================
# PART 2: APIViews & ViewSets (courses/views.py)
# =====================================================================

DJANGO_VIEWS_PY = """
# courses/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.shortcuts import get_object_or_anchor, get_object_or_404
from .models import Department, Course, Student, Enrollment
from .serializers import DepartmentSerializer, CourseSerializer, StudentSerializer, EnrollmentSerializer

# --- Task 1: APIViews (Standard CBV) ---

class CourseListView(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseDetailView(APIView):
    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    def put(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Task 2: ViewSets & Custom Action ---

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # Custom action to list all students enrolled in a specific course
    # Accessible via GET /api/courses/{id}/students/
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        course = self.get_object()
        # Find enrollments for this course and select related students
        enrollments = Enrollment.objects.filter(course=course).select_related('student')
        students = [enrollment.student for enrollment in enrollments]
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
"""

# =====================================================================
# PART 3: URL routing configuration (courses/urls.py)
# =====================================================================

DJANGO_URLS_PY = """
# courses/urls.py (Task 1: Basic View Routing)
from django.urls import path
from .views import CourseListView, CourseDetailView

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
]

# -------------------------------------------------------------

# courses/urls.py (Task 2: ViewSet Routing using DefaultRouter)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, StudentViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'students', StudentViewSet)
router.register(r'enrollments', EnrollmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
"""

def print_explanation():
    print("=====================================================================")
    print("HANDS-ON 3: Django REST Views, URL Routing & Forms")
    print("=====================================================================")
    print("This python file exposes code blueprints for:")
    print("1. Serializers definitions mapping models to JSON output.")
    print("2. Class-Based Views (APIView) for Courses list and detail endpoints.")
    print("3. Refactored ViewSets (ModelViewSet) that automatically handle:")
    print("   - GET /api/courses/      -> list")
    print("   - POST /api/courses/     -> create")
    print("   - GET /api/courses/{id}/ -> retrieve")
    print("   - PUT /api/courses/{id}/ -> update")
    print("   - DELETE /api/courses/{id}/ -> destroy")
    print("4. Custom @action: GET /api/courses/{id}/students/ mapping.")
    print("5. DefaultRouter registration mapping views to endpoint paths.")
    print("=====================================================================")

if __name__ == "__main__":
    print_explanation()
