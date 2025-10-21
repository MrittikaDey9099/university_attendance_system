from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Attendance URLs
    path('take-attendance/', views.take_attendance, name='take_attendance'),
    path('bulk-attendance/', views.bulk_attendance, name='bulk_attendance'),
    path('attendance-list/', views.attendance_list, name='attendance_list'),
    path('attendance-report/', views.attendance_report, name='attendance_report'),
    
    # Management URLs
    path('students/', views.student_management, name='student_management'),
    path('courses/', views.course_management, name='course_management'),
    path('courses/add/', views.add_course, name='add_course'),
    
    # API URLs
    path('api/students-by-class/<int:class_schedule_id>/', views.get_students_by_class, name='students_by_class'),
    path('api/mark-attendance/', views.mark_attendance_api, name='mark_attendance_api'),
    path('api/attendance-stats/', views.get_attendance_stats, name='attendance_stats'),
]