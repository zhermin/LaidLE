'''Custom decorator to check if user is logged in and is the correct role.'''

from django.shortcuts import redirect
from django.contrib import messages

def check_permissions(role: str):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if 'role' not in request.session:
                messages.add_message(request, messages.ERROR, 'Please login to continue.')
                return redirect('login')
            if request.session['role'] != role:
                messages.add_message(request, messages.ERROR, 'You do not have permission to access the page.')
                return redirect(f"/{request.session['role']}")
            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator