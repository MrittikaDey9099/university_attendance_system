from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import Attendance, Student, ClassSchedule, Course, Department, Teacher, Semester
from .forms import AttendanceForm, BulkAttendanceForm, DateRangeForm, StudentSearchForm, CourseForm

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    stats = {
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_teachers': Teacher.objects.filter(is_active=True).count(),
        'total_courses': Course.objects.filter(is_active=True).count(),
        'today_attendance': Attendance.objects.filter(date=timezone.now().date()).count(),
    }
    
    return render(request, 'university/home.html', {'stats': stats})

@login_required
def dashboard(request):
    today = timezone.now().date()
    context = {}
    
    if hasattr(request.user, 'student'):
        student = request.user.student
        attendances = Attendance.objects.filter(student=student)
        
        total_classes = attendances.count()
        present_classes = attendances.filter(status='P').count()
        
        if total_classes > 0:
            attendance_percentage = (present_classes / total_classes) * 100
        else:
            attendance_percentage = 0
        
        recent_attendances = attendances.select_related(
            'class_schedule__course', 'class_schedule__teacher__user'
        ).order_by('-date')[:10]
        
        context.update({
            'student': student,
            'total_classes': total_classes,
            'present_classes': present_classes,
            'attendance_percentage': round(attendance_percentage, 1),
            'recent_attendances': recent_attendances,
        })
    
    elif request.user.is_staff:
        total_students = Student.objects.filter(is_active=True).count()
        total_attendance_today = Attendance.objects.filter(date=today).count()
        
        recent_attendance = Attendance.objects.select_related(
            'student', 'class_schedule__course'
        ).order_by('-timestamp')[:10]
        
        context.update({
            'total_students': total_students,
            'total_attendance_today': total_attendance_today,
            'recent_attendance': recent_attendance,
        })
    
    return render(request, 'university/dashboard.html', context)

@staff_member_required
def take_attendance(request):
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            class_schedule_id = request.POST.get('class_schedule')
            date_str = request.POST.get('date')
            status = request.POST.get('status')
            notes = request.POST.get('notes', '')
            
            student = Student.objects.get(id=student_id)
            class_schedule = ClassSchedule.objects.get(id=class_schedule_id)
            
            attendance, created = Attendance.objects.update_or_create(
                student=student,
                class_schedule=class_schedule,
                date=date_str,
                defaults={
                    'status': status,
                    'notes': notes,
                    'marked_by': request.user
                }
            )
            
            messages.success(request, f'Attendance marked for {student.user.get_full_name()}!')
            return redirect('take_attendance')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    students = Student.objects.filter(is_active=True).select_related('user')
    class_schedules = ClassSchedule.objects.filter(is_active=True).select_related('course')
    
    return render(request, 'university/take_attendance.html', {
        'students': students,
        'class_schedules': class_schedules,
        'today': timezone.now().date()
    })

@staff_member_required
def bulk_attendance(request):
    if request.method == 'POST':
        form = BulkAttendanceForm(request.POST)
        if form.is_valid():
            class_schedule = form.cleaned_data['class_schedule']
            date = form.cleaned_data['date']
            
            students = Student.objects.filter(
                department=class_schedule.course.department,
                is_active=True
            )
            
            attendance_count = 0
            for student in students:
                status_key = f"student_{student.id}"
                status = request.POST.get(status_key, 'A')
                
                if status in ['P', 'A', 'L', 'E']:
                    Attendance.objects.update_or_create(
                        student=student,
                        class_schedule=class_schedule,
                        date=date,
                        defaults={
                            'status': status,
                            'marked_by': request.user
                        }
                    )
                    attendance_count += 1
            
            messages.success(request, f'Attendance recorded for {attendance_count} students!')
            return redirect('attendance_list')
    else:
        form = BulkAttendanceForm()
    
    return render(request, 'university/bulk_attendance.html', {
        'form': form,
    })

@login_required
def attendance_list(request):
    form = DateRangeForm(request.GET or None)
    attendances = Attendance.objects.all()
    
    if hasattr(request.user, 'student'):
        attendances = attendances.filter(student=request.user.student)
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        
        if start_date:
            attendances = attendances.filter(date__gte=start_date)
        if end_date:
            attendances = attendances.filter(date__lte=end_date)
    else:
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        attendances = attendances.filter(date__gte=thirty_days_ago)
    
    attendances = attendances.select_related(
        'student__user',
        'class_schedule__course',
        'class_schedule__teacher__user'
    ).order_by('-date', 'class_schedule__start_time')
    
    return render(request, 'university/attendance_list.html', {
        'attendances': attendances,
        'form': form
    })

@staff_member_required
def attendance_report(request):
    courses = Course.objects.filter(is_active=True)
    selected_course = None
    attendance_data = []
    
    course_id = request.GET.get('course_id')
    if course_id:
        selected_course = get_object_or_404(Course, id=course_id)
        students = Student.objects.filter(
            department=selected_course.department,
            is_active=True
        )
        
        for student in students:
            attendances = Attendance.objects.filter(
                student=student,
                class_schedule__course=selected_course
            )
            
            total_classes = attendances.count()
            present_classes = attendances.filter(status='P').count()
            
            if total_classes > 0:
                percentage = (present_classes / total_classes) * 100
            else:
                percentage = 0
                
            attendance_data.append({
                'student': student,
                'total_classes': total_classes,
                'present_classes': present_classes,
                'percentage': round(percentage, 2)
            })
    
    return render(request, 'university/attendance_report.html', {
        'courses': courses,
        'selected_course': selected_course,
        'attendance_data': attendance_data
    })

# STUDENT MANAGEMENT
@staff_member_required
def student_management(request):
    students = Student.objects.filter(is_active=True).select_related('user', 'department')
    return render(request, 'university/student_management.html', {
        'students': students
    })

# COURSE MANAGEMENT
@staff_member_required
def course_management(request):
    courses = Course.objects.all().select_related('department')
    return render(request, 'university/course_management.html', {'courses': courses})

@staff_member_required
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully!')
            return redirect('course_management')
    else:
        form = CourseForm()
    
    return render(request, 'university/add_course.html', {'form': form})

# API VIEWS
@staff_member_required
def get_students_by_class(request, class_schedule_id):
    class_schedule = get_object_or_404(ClassSchedule, id=class_schedule_id)
    students = Student.objects.filter(
        department=class_schedule.course.department,
        is_active=True
    ).select_related('user')
    
    student_data = []
    for student in students:
        student_data.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': student.user.get_full_name(),
            'email': student.user.email,
        })
    
    return JsonResponse({'students': student_data})

@staff_member_required
def get_students_for_attendance(request):
    class_schedule_id = request.GET.get('class_schedule_id')
    date = request.GET.get('date', timezone.now().date())
    
    if not class_schedule_id:
        return JsonResponse({'error': 'Class schedule ID required'}, status=400)
    
    try:
        class_schedule = ClassSchedule.objects.get(id=class_schedule_id)
        students = Student.objects.filter(
            department=class_schedule.course.department,
            is_active=True
        ).select_related('user')
        
        student_data = []
        for student in students:
            existing_attendance = Attendance.objects.filter(
                student=student,
                class_schedule=class_schedule,
                date=date
            ).first()
            
            student_data.append({
                'id': student.id,
                'student_id': student.student_id,
                'name': student.user.get_full_name(),
                'email': student.user.email,
                'department': student.department.name,
                'existing_status': existing_attendance.status if existing_attendance else None,
            })
        
        return JsonResponse({
            'students': student_data,
            'class_info': {
                'course_name': class_schedule.course.name,
                'teacher_name': class_schedule.teacher.user.get_full_name(),
                'time': f"{class_schedule.start_time} - {class_schedule.end_time}"
            }
        })
        
    except ClassSchedule.DoesNotExist:
        return JsonResponse({'error': 'Class schedule not found'}, status=404)

@login_required
def mark_attendance_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            class_schedule_id = data.get('class_schedule_id')
            status = data.get('status')
            date_str = data.get('date')
            
            student = get_object_or_404(Student, id=student_id)
            class_schedule = get_object_or_404(ClassSchedule, id=class_schedule_id)
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            attendance, created = Attendance.objects.update_or_create(
                student=student,
                class_schedule=class_schedule,
                date=date,
                defaults={
                    'status': status,
                    'marked_by': request.user
                }
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Attendance marked successfully',
                'attendance_id': str(attendance.id)
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# SIMPLE ATTENDANCE
@staff_member_required
def simple_attendance(request):
    courses = Course.objects.all()
    students = Student.objects.filter(is_active=True)
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        course_id = request.POST.get('course')
        status = request.POST.get('status')
        date = request.POST.get('date')
        
        try:
            student = Student.objects.get(id=student_id)
            course = Course.objects.get(id=course_id)
            
            class_schedule, created = ClassSchedule.objects.get_or_create(
                course=course,
                defaults={
                    'teacher': Teacher.objects.first(),
                    'day_of_week': 1,
                    'start_time': '09:00',
                    'end_time': '10:00'
                }
            )
            
            Attendance.objects.create(
                student=student,
                class_schedule=class_schedule,
                date=date,
                status=status,
                marked_by=request.user
            )
            
            messages.success(request, 'Attendance recorded!')
            return redirect('attendance_list')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'university/simple_attendance.html', {
        'courses': courses,
        'students': students
    })

# ADDITIONAL MISSING VIEWS
@staff_member_required
def qr_attendance(request):
    class_schedules = ClassSchedule.objects.filter(
        is_active=True,
        day_of_week=timezone.now().isoweekday()
    ).select_related('course', 'teacher__user')
    
    return render(request, 'university/qr_attendance.html', {
        'class_schedules': class_schedules
    })

@login_required
def student_qr_scan(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Only students can scan QR codes for attendance.')
        return redirect('dashboard')
    
    return render(request, 'university/student_qr_scan.html')

@staff_member_required
def mobile_attendance(request):
    today_classes = ClassSchedule.objects.filter(
        day_of_week=timezone.now().isoweekday(),
        is_active=True
    ).select_related('course', 'teacher__user')
    
    class_data = []
    for class_schedule in today_classes:
        total_students = Student.objects.filter(
            department=class_schedule.course.department,
            is_active=True
        ).count()
        
        marked_attendance = Attendance.objects.filter(
            class_schedule=class_schedule,
            date=timezone.now().date()
        ).count()
        
        class_data.append({
            'schedule': class_schedule,
            'total_students': total_students,
            'marked_attendance': marked_attendance,
            'completion_percentage': round((marked_attendance / total_students * 100) if total_students > 0 else 0, 1)
        })
    
    return render(request, 'university/mobile_attendance.html', {
        'class_data': class_data,
        'today': timezone.now().date()
    })

@login_required
def get_attendance_stats(request):
    if hasattr(request.user, 'student'):
        student = request.user.student
        attendances = Attendance.objects.filter(student=student)
        
        total = attendances.count()
        present = attendances.filter(status='P').count()
        absent = attendances.filter(status='A').count()
        late = attendances.filter(status='L').count()
        
        return JsonResponse({
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'percentage': round((present / total * 100) if total > 0 else 0, 1)
        })
    
    return JsonResponse({'error': 'Not a student'}, status=400)