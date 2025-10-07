"""Course controller placeholders."""
from django.shortcuts import render


def list_courses(request):
    return render(request, 'courses/list.html')


def course_detail(request, course_id):
    return render(request, 'courses/detail.html', {'course_id': course_id})
