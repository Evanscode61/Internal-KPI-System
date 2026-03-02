from functools import wraps
from services.utils.response_provider import ResponseProvider

from functools import wraps


def require_roles(*allowed_roles):
    """
    Decorator to restrict view access based on user role.
    Automatically injects department scoping and role flags into request.
    Injects into request:
        request.is_line_manager   → True if Business_Line_Manager or Tech_Line_Manager
        request.is_employee       → True if employee
        request.is_admin_or_hr    → True if admin or hr
        request.department_scope  → department instance for line managers, None for others
    Usage:
        @require_roles('admin', 'hr')
        @require_roles('admin', 'Business_Line_Manager', 'Tech_Line_Manager')
        @require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager', 'employee')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # 1. authentication check
            if not request.user or not request.user.is_authenticated:
                return ResponseProvider.unauthorized(
                    message="Authentication required"
                )

            # 2. role assignment check
            if not request.user.role:
                return ResponseProvider.forbidden(
                    message="No role assigned to this user"
                )

            # 3. active role check
            if not request.user.role.is_active:
                return ResponseProvider.forbidden(
                    message="Your role has been deactivated. Contact your administrator"
                )

            # 4. role access check
            if request.user.role.name not in allowed_roles:
                return ResponseProvider.forbidden(
                    message=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )

            # 5. inject role flags into request
            user_role = request.user.role.name.lower()

            request.is_line_manager = user_role in (
                'business_line_manager',
                'tech_line_manager'
            )
            request.is_employee    = user_role == 'employee'
            request.is_admin_or_hr = user_role in ('admin', 'hr')

            # 6. inject department scope for line managers
            if request.is_line_manager:
                if not request.user.department:
                    return ResponseProvider.forbidden(
                        message="Your account has no department assigned. Contact your administrator"
                    )
                request.department_scope = request.user.department
            else:
                request.department_scope = None

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_permission(*permissions):
    """
    Decorator to restrict access based on role permissions.
    Checks the Permission table linked to the user's role.
    Usage:
        @require_permission('create_kpi')
        @require_permission('create_kpi', 'update_kpi')  # needs at least one
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # 1. Authentication check
            if not request.user or not request.user.is_authenticated:
                return ResponseProvider.unauthorized(
                    message='Authentication required'
                )

            # 2. Role check
            if not request.user.role:
                return ResponseProvider.forbidden(
                    message='No role assigned to this user'
                )

            # 3. Permission check against DB
            has_permission = request.user.role.permissions.filter(
                codename__in=permissions
            ).exists()

            if not has_permission:
                return ResponseProvider.forbidden(
                    message=f'Access denied. Required permission: {", ".join(permissions)}'
                )

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator