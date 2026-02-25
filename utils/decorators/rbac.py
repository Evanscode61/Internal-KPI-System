from functools import wraps
from services.utils.response_provider import ResponseProvider


def require_roles(*allowed_roles):
    """
    Decorator to restrict view access based on user role.
    Usage: @require_roles('admin', 'Business Line manager')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user or not request.user.is_authenticated:
                return ResponseProvider.unauthorized(message="Authentication required")

            # Check if user has a role assigned
            if not request.user.role:
                return ResponseProvider.forbidden(message="No role assigned to this user")

            # Check if user's role is in allowed roles
            if request.user.role.name not in allowed_roles:
                return ResponseProvider.forbidden(
                    message=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_permission(*permissions):
    """
    Decorator to restrict access based on role permissions (from Role.permissions JSONField).
    Usage: @require_permission('create_kpi', 'approve_result')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return ResponseProvider.unauthorized(message="Authentication required")

            if not request.user.role:
                return ResponseProvider.forbidden(message="No role assigned to this user")

            user_permissions = request.user.role.permissions or []

            # Check if user has at least one of the required permissions
            if not any(p in user_permissions for p in permissions):
                return ResponseProvider.forbidden(
                    message=f"Access denied. Missing required permissions."
                )


            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator