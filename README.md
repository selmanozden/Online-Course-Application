# Online Course Application (Udemy-like Platform)

A comprehensive Django-based online learning platform with role-based authentication supporting Students, Teachers, and Admins.

## 🎯 Features

### Student Features
- Browse and search courses by category
- Enroll in free or paid courses
- Access course content (videos, documents, text)
- Track learning progress
- Take exams and quizzes
- View results and receive certificates
- Rate and review courses

### Teacher Features
- Create and manage courses
- Upload course materials (videos, documents)
- Create exams with multiple question types
- Track student progress and performance
- View analytics and reports

### Admin Features
- Manage users (students, teachers, admins)
- Manage all courses and content
- View platform-wide statistics and reports

## 🚀 Quick Start

1. **Create a virtualenv and install requirements:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Run migrations and create superuser:**

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

3. **Update superuser role to ADMIN:**

```powershell
python manage.py shell
>>> from models.user_model import User
>>> admin = User.objects.get(username='your_username')
>>> admin.role = 'ADMIN'
>>> admin.save()
>>> exit()
```

4. **Run development server:**

```powershell
python manage.py runserver
```

5. **Access:** http://127.0.0.1:8000/

## 📦 Key Dependencies

- **Django 4.2+** - Web framework
- **Pillow** - Image processing
- **djangorestframework** - REST API
- **reportlab** - PDF certificate generation
- **django-crispy-forms** - Form rendering
- **django-cors-headers** - CORS support

## 🗄️ Database Models

### Implemented Models:
- **User** - Role-based authentication (STUDENT, TEACHER, ADMIN)
- **Course & Category** - Course management with categories
- **Content, Video, Document** - Course materials
- **Exam, Question, Answer** - Assessment system
- **Enrollment & Certificate** - Student enrollment and certificates
- **Progress & ContentProgress** - Learning progress tracking

## 🔐 Authentication & Authorization

### User Roles:
1. **STUDENT**: Browse, enroll, learn, take exams
2. **TEACHER**: Create courses, manage content, track students
3. **ADMIN**: Full platform management

### Decorators:
- `@student_required` - Students only
- `@teacher_required` - Teachers only
- `@admin_required` - Admins only
- `@enrollment_required` - Must be enrolled in course
- `@course_owner_required` - Must own the course

## 📁 Project Structure

```
Online-Course-Application/
├── config/                 # Django configuration
├── models/                 # Data models (✓ Completed)
├── controllers/            # View controllers (In Progress)
├── utils/                  # Utilities (✓ Completed)
├── views/                  # Templates and static files (TODO)
├── manage.py
├── requirements.txt
└── README.md
```

## 🎓 Certificate Generation

When a student completes a course (100% content + passing required exams), a certificate is automatically generated with:
- Unique certificate number
- Verification code
- PDF generation using ReportLab
- Download and email delivery

## ⚙️ Configuration

Key settings in `config/settings.py`:
- `AUTH_USER_MODEL = 'models.User'` - Custom user model
- `CERTIFICATE_PASS_PERCENTAGE = 70` - Pass threshold
- `LOGIN_URL = 'auth:login'` - Login redirect
- REST Framework configuration
- CORS settings
- Crispy Forms Bootstrap 5

## 🚦 Next Implementation Steps

### 1. Complete Controllers (controllers/)
Implement class-based views for:
- `auth_controller.py` - Login, Register, Profile
- `home_controller.py` - Landing page, Dashboard router
- `student_controller.py` - Student features
- `teacher_controller.py` - Teacher features
- `admin_controller.py` - Admin panel
- `course_controller.py` - Course browsing
- `exam_controller.py` - Exam interface

### 2. Create Templates (views/templates/)
- Base template with navigation
- Authentication pages
- Role-specific dashboards
- Course management interfaces

### 3. Add Static Files (views/static/)
- CSS: base.css, auth.css, admin.css, teacher.css, student.css
- JS: main.js, course.js, exam.js
- Images and icons

### 4. Configure URLs (config/urls.py)
Set up routing for all views

## 📝 Usage

### For Students:
1. Register (defaults to STUDENT role)
2. Browse and enroll in courses
3. Complete content and pass exams
4. Receive certificate

### For Teachers:
1. Register and request teacher role
2. Create courses with content
3. Create exams
4. Monitor student progress

### For Admins:
1. Access admin dashboard
2. Manage users and courses
3. View platform statistics

## 🐛 Troubleshooting

**Migrations:**
```powershell
python manage.py migrate --run-syncdb
```

**Static Files:**
```powershell
python manage.py collectstatic
```

**Database Reset:**
```powershell
python manage.py flush
python manage.py migrate
```

## 📄 License

MIT License

## 👤 Author

Selman Özden - [@selmanozden](https://github.com/selmanozden)

---

**Status:** Models and Utils completed ✅ | Controllers and Templates in progress 🚧

