from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Department, Course, Student, Teacher, Semester, ClassSchedule, Attendance, Notification

# REMOVE these inline classes - they cause the mixed form issue
# class StudentInline(admin.StackedInline):
#     model = Student
#     can_delete = False
#     verbose_name_plural = 'Student'
#
# class TeacherInline(admin.StackedInline):
#     model = Teacher
#     can_delete = False
#     verbose_name_plural = 'Teacher'

# REMOVE CustomUserAdmin - this shows both forms on user page
# class CustomUserAdmin(UserAdmin):
#     inlines = (StudentInline, TeacherInline)
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_student_id', 'get_teacher_id')
#     
#     def get_student_id(self, obj):
#         if hasattr(obj, 'student'):
#             return obj.student.student_id
#         return "-"
#     get_student_id.short_description = 'Student ID'
#     
#     def get_teacher_id(self, obj):
#         if hasattr(obj, 'teacher'):
#             return obj.teacher.teacher_id
#         return "-"
#     get_teacher_id.short_description = 'Teacher ID'

# KEEP User registered with default UserAdmin (no inlines)
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)  # REMOVE THIS LINE

# Your existing admin classes - KEEP THESE AS THEY ARE
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['created_at']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'credits', 'is_active']
    list_filter = ['department', 'is_active', 'created_at']
    search_fields = ['name', 'code']
    list_editable = ['is_active']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'department', 'enrollment_date', 'is_active']
    list_filter = ['department', 'is_active', 'enrollment_date']
    search_fields = ['student_id', 'user__first_name', 'user__last_name', 'user__email']
    list_editable = ['is_active']
    raw_id_fields = ['user']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['teacher_id', 'user', 'department', 'specialization', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['teacher_id', 'user__first_name', 'user__last_name']
    list_editable = ['is_active']

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'start_date', 'end_date', 'is_current']
    list_editable = ['is_current']

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['course', 'teacher', 'semester', 'day_of_week', 'start_time', 'end_time', 'room', 'is_active']
    list_filter = ['semester', 'day_of_week', 'is_active', 'course__department']
    list_editable = ['is_active']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_schedule', 'date', 'status', 'marked_by', 'timestamp']
    list_filter = ['date', 'status', 'class_schedule__course', 'class_schedule__semester']
    search_fields = ['student__student_id', 'student__user__first_name', 'student__user__last_name']
    date_hierarchy = 'date'
    raw_id_fields = ['student', 'class_schedule', 'marked_by']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'title']
    list_editable = ['is_read']