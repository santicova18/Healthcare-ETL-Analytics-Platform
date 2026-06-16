from functools import wraps

from django.http import HttpResponseForbidden


def role_required(*allowed_roles):
    """Decorador simple para proteger vistas por rol.

    Requiere que exista `request.user.role` (User custom).

    Uso:
        @role_required('Administrador')
        def view(...):
            ...
    """

    allowed = set(allowed_roles)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = getattr(request, "user", None)
            role = getattr(user, "role", None)

            # Si no hay usuario o rol, denegar
            if user is None or not getattr(user, "is_authenticated", False) or role not in allowed:
                return HttpResponseForbidden("No autorizado para este recurso.")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

