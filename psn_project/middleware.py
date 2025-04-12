'''from django.shortcuts import redirect

class EngineerAccessRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the user's role from the session
        role = request.session.get('role', None)

        # If the user is an engineer, restrict access to specific URLs
        if role == 'Engineer':
            allowed_paths = [
                '/menu/',
                '/menu/psn_form/',
                '/mapping_process/form/',
                '/direct_calls/form/',
            ]
            if not any(request.path.startswith(path) for path in allowed_paths):
                return redirect('/menu/')  # Redirect to the menu page if access is restricted

        response = self.get_response(request)
        return response'''