"""Authentication controller for user login, register, and profile management."""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.views import View
from django.utils.decorators import method_decorator
from models.user_model import User


class LoginView(View):
    """User login view."""
    template_name = 'auth/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect based on user role
            if user.is_admin:
                return redirect('admin_dashboard')
            elif user.is_teacher:
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, self.template_name)


class RegisterView(View):
    """User registration view."""
    template_name = 'auth/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        role = request.POST.get('role', 'STUDENT')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Validation
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, self.template_name)
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, self.template_name)
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, self.template_name)
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                first_name=first_name,
                last_name=last_name
            )
            
            login(request, user)
            messages.success(request, 'Registration successful!')
            
            # Redirect based on role
            if role == 'TEACHER':
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')
                
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, self.template_name)


class LogoutView(View):
    """User logout view."""
    
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('home')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """User profile view."""
    template_name = 'auth/profile.html'
    
    def get(self, request):
        return render(request, self.template_name, {'user': request.user})
    
    def post(self, request):
        user = request.user
        
        # Update basic info
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.bio = request.POST.get('bio', user.bio)
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        # Update role-specific fields
        if user.is_teacher:
            user.expertise = request.POST.get('expertise', user.expertise)
            user.qualification = request.POST.get('qualification', user.qualification)
        elif user.is_student:
            user.education_level = request.POST.get('education_level', user.education_level)
        
        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
        except Exception as e:
            messages.error(request, f'Update failed: {str(e)}')
        
        return redirect('profile')


class ForgotPasswordView(TemplateView):
    """Forgot password view."""
    template_name = 'auth/forgot_password.html'
