
from datetime import datetime
from datetime import datetime
from chalice import Chalice, Response, AuthResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Department, Student, Course, AttendanceLog
from auth import authenticate_user, create_access_token
import logging

app = Chalice(app_name='attendance-api')
Base.metadata.create_all(bind=engine)
logging.basicConfig(filename='app.log', level=logging.INFO)

#--------------------------------------------------------------------------------------
def setup():
    """
    Function to set up the initial state of the application,
    such as creating a default user if no users exist in the database.
    """
    with SessionLocal() as session:
        # Check if any users exist in the database
        existing_user = session.query(User).first()
        if not existing_user:
            # Create a default admin user
            default_user = User(
                username='admin',
                password='admin',  # You should replace this with a hashed password
                type='admin',
                full_name='Admin User',
                email='admin@example.com'
            )
            session.add(default_user)
            session.commit()

setup()
#------------------------------------------------------------------------------------------



def require_auth(func):
    """
    Decorator to enforce authentication for API endpoints.
    """
    def wrapper(event, context):
        try:
            access_token = event['headers']['Authorization']
            user = authenticate_user(access_token)
            if not user:
                return Response(body='Unauthorized', status_code=401)
            return func(event, context, user)
        except KeyError:
            return Response(body='Unauthorized', status_code=401)
    return wrapper

@app.route('/login', methods=['POST'])
def login():
    """
    Endpoint to authenticate users and generate access tokens.
    """
    data = app.current_request.json_body
    username = data.get('username')
    password = data.get('password')
    with SessionLocal() as session:
        user = session.query(User).filter(User.username == username).first()
        if user and user.password == password:
            access_token = create_access_token({'username': user.username})
            return {'access_token': access_token}
        else:
            return Response(body='Invalid username or password', status_code=401)

@app.route('/attendance', methods=['GET'])
@require_auth
def get_attendance(event, context, user):
    """
    Endpoint to retrieve attendance records.
    """
    with SessionLocal() as session:
        # Assuming user is a teacher or admin who can access all attendance records
        if user.type == 'teacher' or user.type == 'admin':
            attendance_logs = session.query(AttendanceLog).all()
            attendance_records = [{
                'id': log.id,
                'student_id': log.student_id,
                'course_id': log.course_id,
                'present': log.present,
                'submitted_by': log.submitted_by,
                'updated_at': log.updated_at
            } for log in attendance_logs]
            return {'attendance_records': attendance_records}
        # If user is a student, retrieve only their own attendance records
        elif user.type == 'student':
            student = session.query(Student).filter(Student.username == user.username).first()
            attendance_logs = session.query(AttendanceLog).filter(AttendanceLog.student_id == student.id).all()
            attendance_records = [{
                'id': log.id,
                'student_id': log.student_id,
                'course_id': log.course_id,
                'present': log.present,
                'submitted_by': log.submitted_by,
                'updated_at': log.updated_at
            } for log in attendance_logs]
            return {'attendance_records': attendance_records}
        else:
            return Response(body='Unauthorized', status_code=403)


@app.route('/attendance', methods=['POST'])
@require_auth
def mark_attendance(event, context, user):
    """
    Endpoint to mark attendance.
    """
    data = app.current_request.json_body
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    present = data.get('present')

    if not all([student_id, course_id, present]):
        return Response(body='Missing required fields', status_code=400)

    with SessionLocal() as session:
        # Check if the user is authorized to mark attendance for the given course
        if user.type == 'teacher' or user.type == 'admin':
            # Check if the student and course exist
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return Response(body='Student not found', status_code=404)
            course = session.query(Course).filter(Course.id == course_id).first()
            if not course:
                return Response(body='Course not found', status_code=404)
            
            # Create a new AttendanceLog entry
            attendance_log = AttendanceLog(
                student_id=student_id,
                course_id=course_id,
                present=present,
                submitted_by=user.id,
                updated_at=datetime.now()
            )
            session.add(attendance_log)
            session.commit()
            return {'message': 'Attendance marked successfully'}
        else:
            return Response(body='Unauthorized', status_code=403)

@app.route('/departments', methods=['GET'])
@require_auth
def get_departments(event, context, user):
    """
    Endpoint to retrieve departments.
    """
    with SessionLocal() as session:
        departments = session.query(Department).all()
        department_list = [{
            'id': department.id,
            'department_name': department.department_name,
            'submitted_name': department.submitted_name,
            'submitted_by': department.submitted_by,
            'updated_at': department.updated_at
        } for department in departments]
        return {'departments': department_list}


@app.route('/departments', methods=['POST'])
@require_auth
def create_department(event, context, user):
    """
    Endpoint to create departments.
    """
    if user.type != 'admin':
        return Response(body='Unauthorized', status_code=403)
    data = app.current_request.json_body
    department_name = data.get('department_name')
    submitted_name = data.get('submitted_name')
    submitted_by = user.id  # Assuming user is authenticated and its ID is used as submitted_by
    department = Department(department_name=department_name, submitted_name=submitted_name, submitted_by=submitted_by)
    with SessionLocal() as session:
        session.add(department)
        session.commit()
        return Response(body='Department created successfully', status_code=201)

@app.route('/students', methods=['POST'])
@require_auth
def create_students(event, context, user):
    """
    Endpoint to create departments.
    """
    if user.type != 'admin':
        return Response(body='Unauthorized', status_code=403)
    data = app.current_request.json_body
    department_id = data.get('department_id')
    submitted_name = data.get('submitted_name')
    submitted_by = user.id  # Assuming user is authenticated and its ID is used as submitted_by
    student = Student(department_id=department_id, submitted_name=submitted_name, submitted_by=submitted_by)
    with SessionLocal() as session:
        session.add(student)
        session.commit()
        return Response(body='Student record created successfully', status_code=201)
