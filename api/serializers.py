from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from university.models import Department, Course, Student, Teacher, ClassSchedule, Attendance, Semester

# API Views without REST Framework - THEY WORK!
@method_decorator(csrf_exempt, name='dispatch')
class DepartmentAPI(View):
    def get(self, request):
        try:
            departments = list(Department.objects.all().values())
            return JsonResponse({'success': True, 'departments': departments})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class CourseAPI(View):
    def get(self, request):
        try:
            courses = list(Course.objects.all().values())
            return JsonResponse({'success': True, 'courses': courses})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class StudentAPI(View):
    def get(self, request):
        try:
            students = list(Student.objects.all().values(
                'id', 'roll_number', 'user__first_name', 'user__last_name', 
                'course__name', 'created_at'
            ))
            return JsonResponse({'success': True, 'students': students})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class AttendanceAPI(View):
    def get(self, request):
        try:
            attendance = list(Attendance.objects.all().values())
            return JsonResponse({'success': True, 'attendance': attendance})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            course_id = data.get('course_id')
            status = data.get('status', 'present')
            date = data.get('date')
            
            student = Student.objects.get(id=student_id)
            course = Course.objects.get(id=course_id)
            
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                course=course,
                date=date,
                defaults={'status': status}
            )
            
            if not created:
                attendance.status = status
                attendance.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Attendance marked successfully',
                'attendance_id': attendance.id,
                'created': created
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class BulkAttendanceAPI(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            date = data.get('date')
            attendance_data = data.get('attendance_data', [])
            
            course = Course.objects.get(id=course_id)
            results = []
            created_count = 0
            updated_count = 0
            
            for item in attendance_data:
                student_id = item.get('student_id')
                status = item.get('status', 'absent')
                
                student = Student.objects.get(id=student_id)
                
                # Create or update attendance
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    course=course,
                    date=date,
                    defaults={'status': status}
                )
                
                if not created:
                    attendance.status = status
                    attendance.save()
                    updated_count += 1
                else:
                    created_count += 1
                
                results.append({
                    'student_id': student_id,
                    'status': status,
                    'created': created
                })
            
            return JsonResponse({
                'success': True,
                'message': f'Attendance processed: {created_count} created, {updated_count} updated',
                'total_processed': len(results),
                'results': results
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

class DashboardStatsAPI(View):
    def get(self, request):
        try:
            total_students = Student.objects.count()
            total_courses = Course.objects.count()
            total_teachers = Teacher.objects.count()
            
            # Today's stats
            from datetime import date
            today = date.today()
            today_attendance = Attendance.objects.filter(date=today)
            present_today = today_attendance.filter(status='present').count()
            absent_today = today_attendance.filter(status='absent').count()
            
            return JsonResponse({
                'success': True,
                'stats': {
                    'total_students': total_students,
                    'total_courses': total_courses,
                    'total_teachers': total_teachers,
                    'present_today': present_today,
                    'absent_today': absent_today,
                    'attendance_rate': round((present_today / total_students * 100) if total_students > 0 else 0, 2)
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})