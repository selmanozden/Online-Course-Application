"""URL Configuration for Online Course Application."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import views
from controllers.home_controller import HomeView, AboutView, ContactView
from controllers.auth_controller import LoginView, RegisterView, LogoutView, ProfileView, ForgotPasswordView
from controllers.student_controller import (
    StudentDashboardView, BrowseCoursesView, EnrolledCoursesView, 
    CourseContentView, MyResultsView, TakeExamView, enroll_course
)
from controllers.teacher_controller import (
    TeacherDashboardView, MyCoursesView, CreateCourseView, EditCourseView,
    StudentsListView, CreateExamView, add_content, delete_course
)
from controllers.admin_controller import (
    AdminDashboardView, UsersManagementView, CoursesManagementView,
    ReportsView, toggle_user_status, approve_course, reject_course
)

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # Home pages
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    
    # Student routes
    path('student/dashboard/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('student/browse-courses/', BrowseCoursesView.as_view(), name='browse_courses'),
    path('student/enrolled-courses/', EnrolledCoursesView.as_view(), name='enrolled_courses'),
    path('student/course/<slug:course_slug>/', CourseContentView.as_view(), name='course_content'),
    path('student/enroll/<slug:course_slug>/', enroll_course, name='enroll_course'),
    path('student/results/', MyResultsView.as_view(), name='my_results'),
    path('student/exam/<int:exam_id>/', TakeExamView.as_view(), name='take_exam'),
    
    # Teacher routes
    path('teacher/dashboard/', TeacherDashboardView.as_view(), name='teacher_dashboard'),
    path('teacher/my-courses/', MyCoursesView.as_view(), name='my_courses'),
    path('teacher/create-course/', CreateCourseView.as_view(), name='create_course'),
    path('teacher/edit-course/<slug:course_slug>/', EditCourseView.as_view(), name='edit_course'),
    path('teacher/delete-course/<slug:course_slug>/', delete_course, name='delete_course'),
    path('teacher/add-content/<slug:course_slug>/', add_content, name='add_content'),
    path('teacher/students/', StudentsListView.as_view(), name='students_list'),
    path('teacher/students/<slug:course_slug>/', StudentsListView.as_view(), name='course_students'),
    path('teacher/create-exam/', CreateExamView.as_view(), name='create_exam'),
    
    # Admin Panel routes (custom admin interface)
    path('admin-panel/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-panel/users/', UsersManagementView.as_view(), name='users_management'),
    path('admin-panel/courses/', CoursesManagementView.as_view(), name='courses_management'),
    path('admin-panel/reports/', ReportsView.as_view(), name='reports'),
    path('admin-panel/users/<int:user_id>/toggle/', toggle_user_status, name='toggle_user_status'),
    path('admin-panel/courses/<int:course_id>/approve/', approve_course, name='approve_course'),
    path('admin-panel/courses/<int:course_id>/reject/', reject_course, name='reject_course'),
    
    # REST API endpoints
    path('api/', include('rest_framework.urls')),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

