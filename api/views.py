from django.http import JsonResponse 
from django.views import View 
from django.views.decorators.csrf import csrf_exempt 
from django.utils.decorators import method_decorator 
import json 
from university.models import Department, Course, Student, Teacher, ClassSchedule, Attendance, Semester 
 
@method_decorator(csrf_exempt, name='dispatch') 
class DepartmentAPI(View): 
    def get(self, request): 
        departments = list(Department.objects.all().values()) 
        return JsonResponse({'departments': departments}) 
 
@method_decorator(csrf_exempt, name='dispatch') 
class CourseAPI(View): 
    def get(self, request): 
        courses = list(Course.objects.all().values()) 
        return JsonResponse({'courses': courses}) 
 
@method_decorator(csrf_exempt, name='dispatch') 
class StudentAPI(View): 
    def get(self, request): 
        students = list(Student.objects.all().values()) 
        return JsonResponse({'students': students}) 
 
@method_decorator(csrf_exempt, name='dispatch') 
class AttendanceAPI(View): 
    def get(self, request): 
        attendance = list(Attendance.objects.all().values()) 
        return JsonResponse({'attendance': attendance}) 
 
@method_decorator(csrf_exempt, name='dispatch') 
class BulkAttendanceAPI(View): 
    def post(self, request): 
        return JsonResponse({'message': 'Bulk attendance endpoint'}) 
 
class DashboardStatsAPI(View): 
    def get(self, request): 
        return JsonResponse({'message': 'Dashboard stats endpoint'}) 
