from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String)
    submitted_name = Column(String)
    submitted_by = Column(Integer)
    updated_at = Column(DateTime)

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))
    semester = Column(String)
    class_ = Column(String)
    lecture_hours = Column(String)
    submitted_by = Column(Integer)
    updated_at = Column(DateTime)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    full_name = Column(String)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    submitted_by = Column(Integer)
    updated_at = Column(DateTime)

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))
    class_ = Column(String)
    submitted_by = Column(Integer)
    updated_at = Column(DateTime)

class AttendanceLog(Base):
    __tablename__ = 'attendance_log'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    present = Column(String)
    submitted_by = Column(Integer)
    updated_at = Column(DateTime)
