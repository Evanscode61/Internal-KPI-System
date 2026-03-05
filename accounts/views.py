from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model
from accounts.jwt_utils import generate_access_token, generate_refresh_token, decode_token
import json
from accounts.models import Role, RefreshToken
from services.services import UserService, RoleService, AuthService
from services.utils.response_provider import ResponseProvider
from utils.decorators.allowed_http_methods import allowed_http_methods
from utils.decorators.rbac import require_roles

User = get_user_model()
user_service = UserService()

# ─── AUTH VIEWS ───────────────────────────────────────────────────────────────

@csrf_exempt
def register_user_view(request):
    """Register a new user (POST)."""
    if request.method != "POST":
        return ResponseProvider.bad_request(error="POST method required")
    try:
        body = _parse_body(request)
        username = body.get("username")
        password = body.get("password")
        email    = body.get("email")

        if not username or not password or not email:
            return ResponseProvider.bad_request(error="username, email and password are required")

        user_service.register_user(username=username, email=email, password=password)
        return ResponseProvider.created(message="Successfully registered user")

    except ValueError as e:
        return ResponseProvider.bad_request(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
def user_login_view(request):
    """Log in and return access + refresh tokens (POST)."""
    if request.method != "POST":
        return ResponseProvider.bad_request(error="POST method required")
    try:
        body     = _parse_body(request)
        username = body.get("username")
        password = body.get("password")

        if not username or not password:
            return ResponseProvider.bad_request(error="username and password are required")

        user = authenticate(request, username=username, password=password)
        if user is None:
            return ResponseProvider.unauthorized(error="Invalid credentials")

        access_token  = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
        RefreshToken.objects.create(user=user, token=refresh_token)

        return ResponseProvider.success(
            message="Login successful",
            data={"access_token": access_token, "refresh_token": refresh_token}
        )

    except ValueError as e:
        return ResponseProvider.bad_request(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
def token_refresh_view(request):
    """Return a new access token given a valid refresh token (POST)."""
    if request.method != "POST":
        return ResponseProvider.bad_request(error="POST method required")
    try:
        body          = _parse_body(request)
        refresh_token = body.get("refresh_token")

        if not refresh_token:
            return ResponseProvider.bad_request(error="refresh_token is required")

        payload = decode_token(refresh_token)
        if "error" in payload:
            return ResponseProvider.unauthorized(error=payload["error"])

        if payload.get("type") != "refresh":
            return ResponseProvider.unauthorized(error="Invalid token type — refresh token required")
        if not RefreshToken.objects.filter(token=refresh_token).exists():
            return ResponseProvider.unauthorized(error="Token has been revoked")

        user = User.objects.get(pk=payload.get("user_id"))
        return ResponseProvider.success(
            message="Token refreshed",
            data={"access_token": generate_access_token(user)}
        )

    except User.DoesNotExist:
        return ResponseProvider.not_found(error="User not found")
    except ValueError as e:
        return ResponseProvider.bad_request(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
def user_logout_view(request):
    """Invalidate the refresh token (POST)."""
    if request.method != "POST":
        return ResponseProvider.bad_request(error="POST method required")
    try:
        body          = _parse_body(request)
        refresh_token = body.get("refresh_token")

        if not refresh_token:
            return ResponseProvider.bad_request(error="refresh_token is required")

        AuthService.logout(refresh_token)
        return ResponseProvider.success(message="Successfully logged out")

    except LookupError:
        return ResponseProvider.not_found(error="Token not found")
    except ValueError as e:
        return ResponseProvider.bad_request(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
def reset_password_view(request):
    """
    OTP-based password reset which has two steps on the same endpoint (POST).
    Step 1 has no otp in the body generate and email OTP.
    Step has the otp in the body to verify OTP and set new password.
    """
    if request.method != "POST":
        return ResponseProvider.bad_request(error="POST method required")
    try:
        body             = _parse_body(request)
        username         = body.get("username")
        otp_code         = body.get("otp")
        new_password     = body.get("new_password")
        confirm_password = body.get("confirm_password")

        if not username:
            return ResponseProvider.bad_request(error="username is required")

        from services.services import OTPService, TransactionLogService
        from django.conf import settings

        # no OTP provided → generate and send
        if not otp_code:
            otp           = OTPService.create_otp(username=username, purpose="password_reset")
            response_data = {}
            if settings.DEBUG:
                response_data["dev_otp"] = otp.code
                response_data["note"]    = "dev_otp shown in DEBUG mode only"
            return ResponseProvider.success(
                message=f"OTP sent to the email registered to {username}. Valid for 10 minutes.",
                data=response_data
            )

        #  OTP provided → verify and reset
        if not new_password or not confirm_password:
            return ResponseProvider.bad_request(error="new_password and confirm_password are required")
        if new_password != confirm_password:
            return ResponseProvider.bad_request(error="Passwords do not match")
        if len(new_password) < 8:
            return ResponseProvider.bad_request(error="Password must be at least 8 characters")

        user = OTPService.verify_otp(username=username, code=otp_code, purpose="password_reset")
        user.set_password(new_password)
        user.save()

        try:
            TransactionLogService.log(
                event_code="password_reset_otp", triggered_by=user, entity=user,
                status_code="ACT",
                message=f'Password reset via OTP for user "{user.username}"',
                ip_address=request.META.get("REMOTE_ADDR"),
                metadata={"username": user.username, "user_uuid": str(user.uuid)},
            )
        except Exception as log_err:
            print(f"[TransactionLog ERROR] {log_err}")

        return ResponseProvider.success(message="Password reset successfully. You can now log in.")

    except LookupError as e:
        return ResponseProvider.not_found(error=str(e))
    except (ValueError, PermissionError) as e:
        return ResponseProvider.bad_request(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
@allowed_http_methods(["POST"])
def request_otp_view(request):
    """
    Standalone OTP request (POST).
    Body: { "username": "...", "purpose": "password_reset" | "first_login" }
    """
    try:
        body     = _parse_body(request)
        username = body.get("username")
        purpose  = body.get("purpose", "password_reset")

        if not username:
            return ResponseProvider.bad_request(error="username is required")
        if purpose not in ("password_reset", "first_login"):
            return ResponseProvider.bad_request(error="purpose must be 'password_reset' or 'first_login'")

        from django.conf import settings
        from services.services import OTPService

        otp           = OTPService.create_otp(username=username, purpose=purpose)
        response_data = {}
        if settings.DEBUG:
            response_data["dev_otp"] = otp.code
            response_data["note"]    = "dev_otp shown in DEBUG mode only"

        return ResponseProvider.success(
            message=f"OTP sent to the email address registered to {username}. Valid for 10 minutes.",
            data=response_data
        )

    except LookupError as e:
        return ResponseProvider.not_found(error=str(e))
    except ValueError as e:
        return ResponseProvider.bad_request(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


# ─── USER VIEWS ───────────────────────────────────────────────────────────────

@csrf_exempt
@require_roles('admin')
def create_user_view(request):
    """Create a user directly (POST). Admin use."""
    if request.method != "POST":
        return ResponseProvider.bad_request(error="POST method required")
    try:
        body     = _parse_body(request)
        username = body.get("username")
        password = body.get("password")
        email    = body.get("email")

        if not username or not password or not email:
            return ResponseProvider.bad_request(error="username, email and password are required")
        if User.objects.filter(email=email).exists():
            return ResponseProvider.bad_request(error="Email address already in use")

        user = User.objects.create_user(username=username, email=email, password=password)
        return ResponseProvider.created(
            message="User created successfully",
            data={"username": user.username, "email": user.email}
        )

    except ValueError as e:
        return ResponseProvider.bad_request(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
@require_roles("hr","admin")
def list_users_view(request):
    """Return all users (GET). Admin only."""
    if request.method != "GET":
        return ResponseProvider.bad_request(error="GET method required")
    try:
        return UserService.list_users(request)
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
@require_roles('admin')
def delete_user_view(request, user_uuid):
    """Delete a user by UUID (DELETE). Admin only."""
    if request.method != "DELETE":
        return ResponseProvider.bad_request(error="DELETE method required")
    try:
        return UserService.delete_user(user_uuid)
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
@require_roles('admin')
def update_user_view(request, user_uuid):
    """Update a user's fields (PUT / PATCH). Admin only."""
    if request.method not in ("PUT", "PATCH"):
        return ResponseProvider.bad_request(error="PUT or PATCH method required")
    try:
        # Validate body is parseable before handing off to the service
        _parse_body(request)
        return UserService.update_user(request, user_uuid)
    except ValueError as e:
        return ResponseProvider.bad_request(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
@require_roles('admin','hr','Business Line_Manager','Tech_Line_Manager','employee')
def view_user_profile(request, user_uuid):
    """Return a single user's profile (GET)."""
    if request.method != "GET":
        return ResponseProvider.bad_request(error="GET method required")
    if request.user.role.name == 'employee' and str(request.user.uuid) != user_uuid:
        return ResponseProvider.forbidden(error ="user not in employee")

    try:
        user = User.objects.select_related("role", "department", "team", "status").get(uuid=user_uuid)
        return ResponseProvider.success(data={
            "uuid":         str(user.uuid),
            "username":     user.username,
            "email":        user.email,
            "phone_number": user.phone_number,
            "role":         user.role.name       if user.role       else None,
            "department":   user.department.name if user.department else None,
            "team":         user.team.team_name  if user.team       else None,
            "status":       user.status.name     if user.status     else None,
        })
    except User.DoesNotExist:
        return ResponseProvider.not_found(error="User not found")
    except Exception as e:
        return ResponseProvider.handle_exception(e)


# ─── ROLE VIEWS ───────────────────────────────────────────────────────────────

@csrf_exempt
@require_roles('admin', 'hr')
def create_role(request):
    """Create a new role (POST)."""
    if request.method != "POST":
        return ResponseProvider.bad_request(error="POST method required")
    try:
        body        = _parse_body(request)
        name        = body.get("name", "").strip()
        description = body.get("description", "")

        if not name:
            return ResponseProvider.bad_request(error="Role name is required")
        if Role.objects.filter(name=name).exists():
            return ResponseProvider.bad_request(error=f"Role '{name}' already exists")

        role = Role.objects.create(name=name, description=description)
        return ResponseProvider.created(
            message="Role created",
            data={"name": role.name, "description": role.description}
        )

    except ValueError as e:
        return ResponseProvider.bad_request(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
@require_roles("admin","hr")
def delete_role_view(request, name: str):
    """Delete a role by name (DELETE)."""
    if request.method != "DELETE":
        return ResponseProvider.bad_request(error="DELETE method required")
    try:
        RoleService().delete_role_by_name(name)
        return ResponseProvider.success(message=f"Role '{name}' deleted successfully")
    except LookupError as e:
        return ResponseProvider.not_found(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
@require_roles("admin","hr")
def update_role_view(request, name: str):
    """Assign a new role to a user identified by username (PUT)."""
    if request.method != "PUT":
        return ResponseProvider.bad_request(error="PUT method required")
    try:
        body     = _parse_body(request)
        new_role = body.get("role", "").strip()

        if not new_role:
            return ResponseProvider.bad_request(error="'role' field is required")

        return RoleService.update_user_role(request, username=name, new_role=new_role)

    except ValueError as e:
        return ResponseProvider.bad_request(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
@require_roles("admin","hr")
def list_roles_view(request):
    """Return all role names (GET)."""
    if request.method != "GET":
        return ResponseProvider.bad_request(error="GET method required")
    try:
        roles = RoleService().get_all_roles()
        return ResponseProvider.success(data=[r.name for r in roles])
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
@allowed_http_methods(["POST"])
@require_roles("admin","hr")
def assign_role_view(request):
    """Assign a role to a user by username (POST)."""
    try:
        body      = _parse_body(request)
        username  = body.get("username")
        role_name = body.get("role_name")

        if not username or not role_name:
            return ResponseProvider.bad_request(error="username and role_name are required")

        user = User.objects.get(username=username)
        UserService.assign_role(user, role_name)

        return ResponseProvider.success(
            message=f"Role '{role_name}' assigned to '{username}' successfully",
            data={"username": user.username, "email": user.email,
                  "role": user.role.name if user.role else None}
        )

    except User.DoesNotExist:
        return ResponseProvider.not_found(error=f"User not found")
    except ValueError as e:
        return ResponseProvider.not_found(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)

def _parse_body(request) -> dict:
    """
    Safely parse the JSON request body.
    Raises ValueError with a clear message if the body is missing or malformed,
    so every caller gets a consistent 400 JSON response instead of an HTML crash.
    """
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        raise ValueError("Request body must be valid JSON and Content-Type must be application/json")