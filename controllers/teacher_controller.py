"""Teacher controller placeholders."""
from django.shortcuts import render


def dashboard(request):
    return render(request, 'teacher/dashboard.html')
