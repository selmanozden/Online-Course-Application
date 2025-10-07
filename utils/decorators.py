from django.shortcuts import redirect

def teacher_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not getattr(request.user, 'is_teacher', False):
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped
