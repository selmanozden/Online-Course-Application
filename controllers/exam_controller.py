"""Exam controller placeholders."""
from django.shortcuts import render


def list_exams(request):
    return render(request, 'exams/list.html')
