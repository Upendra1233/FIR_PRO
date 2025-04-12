from django.shortcuts import redirect

'''def engineer_only(view_func):
    def wrapper(request, *args, **kwargs):
        role = request.session.get('role', None)
        if role == 'Engineer':
            allowed_paths = [
                '/menu/',
                '/menu/psn_form/',
                '/mapping_process/form/',
                '/direct_calls/form/',
            ]
            if not any(request.path.startswith(path) for path in allowed_paths):
                return redirect('/menu/')  # Redirect to the menu page if access is restricted
        return view_func(request, *args, **kwargs)
    return wrapper'''