from django.urls import path 
from . import views 
 
urlpatterns = [ 
    path('departments/', views.DepartmentAPI.as_view(), name='api-departments'), 
    path('courses/', views.CourseAPI.as_view(), name='api-courses'), 
    path('students/', views.StudentAPI.as_view(), name='api-students'), 
    path('attendance/', views.AttendanceAPI.as_view(), name='api-attendance'), 
    path('bulk-attendance/', views.BulkAttendanceAPI.as_view(), name='api-bulk-attendance'), 
    path('dashboard-stats/', views.DashboardStatsAPI.as_view(), name='api-dashboard-stats'), 
] 
