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

User = get_user_model()
user_service = UserService()


@csrf_exempt
def register_user_view(request):
    """Function to register a new user"""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    username = body.get("username")
    password = body.get("password")
    email = body.get("email")
    if not username or not password or not email:
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    try:
        user_service.register_user(
            username=username,
            email=email,
            password=password,
        )

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"message": "Successfully registered user"}, status=201)


@csrf_exempt
def user_login_view(request):
    """Function to log in a user"""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        body = json.loads(request.body)
        username = body.get("username")
        password = body.get("password")
        email = body.get("email")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    RefreshToken.objects.create(user=user, token=refresh_token)

    return JsonResponse({
        "access_token": access_token,
        "refresh_token": refresh_token
    })


@csrf_exempt
def token_refresh_view(request):
    """Function to refresh a user"""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    body = json.loads(request.body)
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        return JsonResponse({"error": "Refresh token required"}, status=400)
    payload = decode_token(refresh_token)

    if "error" in payload:
        return JsonResponse(payload, status=401)

    if payload.get("type") != "refresh":
        return JsonResponse({"error": "Invalid token type"}, status=401)

    try:
        user = User.objects.get(pk = payload.get("user_id"))
        #user=  authenticate(request, refresh_token=payload["refresh_token"])

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=401)

    new_access_token = generate_access_token(user)

    return JsonResponse({
        "access_token": new_access_token
    })

@csrf_exempt
def reset_password_view(request):
    """
    OTP-based password reset — 2 steps on the same endpoint.
    No Authorization header required for either step.
    System generates a 6-digit OTP, saves it to the database with a
    10-minute expiry, and emails it to the user's registered address.
    System verifies the OTP (checks it exists, is unused, has not expired),
    then sets the new password and logs the event.
    """
    if request.method != "POST":
        return ResponseProvider.bad_request(error="POST method required")

    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return ResponseProvider.bad_request(error="Invalid JSON")

    username = body.get("username")
    otp_code = body.get("otp")
    new_password = body.get("new_password")
    confirm_password = body.get("confirm_password")

    if not username:
        return ResponseProvider.bad_request(error="username is required")

    from services.services import OTPService, TransactionLogService

    # ── STEP 1: otp not in body → generate and send OTP ──────────────────────
    if not otp_code:
        try:
            from django.conf import settings
            otp = OTPService.create_otp(username=username, purpose="password_reset")

            response_data = {}
            if settings.DEBUG:
                # This block is automatically skipped when DEBUG=False in production.
                response_data["dev_otp"] = otp.code
                response_data["note"] = "dev_otp is shown in DEBUG mode only — remove in production"

            return ResponseProvider.success(
                message=f"OTP sent to the email registered to {username}. Valid for 10 minutes.",
                data=response_data
            )
        except LookupError as e:
            return ResponseProvider.not_found(error=str(e))
        except Exception as e:
            return ResponseProvider.handle_exception(e)

    # ── STEP 2: otp in body → verify OTP and reset password ──────────────────
    if not new_password or not confirm_password:
        return ResponseProvider.bad_request(
            error="new_password and confirm_password are required"
        )

    if new_password != confirm_password:
        return ResponseProvider.bad_request(error="Passwords do not match")

    if len(new_password) < 8:
        return ResponseProvider.bad_request(error="Password must be at least 8 characters")

    try:
        user = OTPService.verify_otp(
            username=username,
            code=otp_code,
            purpose="password_reset",
        )
        user.set_password(new_password)
        user.save()

        # Log the password reset event
        try:
            TransactionLogService.log(
                event_code="password_reset_otp",
                triggered_by=user,
                entity=user,
                status_code="ACT",
                message=f"Password reset via OTP for user \"{user.username}\"",
                ip_address=request.META.get("REMOTE_ADDR"),
                metadata={"username": user.username, "user_uuid": str(user.uuid)},
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return ResponseProvider.success(
            message="Password reset successfully. You can now log in with your new password."
        )

    except (LookupError, ValueError) as e:
        return ResponseProvider.bad_request(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)


@csrf_exempt
@allowed_http_methods(['POST'])
def request_otp_view(request):
    """
    Standalone OTP request endpoint.
    Used when you want to trigger an OTP without going through
    the reset_password endpoint — for example during first login.
    Body:
        {
            "username": "emp1",
            "purpose":  "password_reset"   ← or "first_login"
        }
    purpose is optional — defaults to "password_reset" if not provided.


    """
    try:
        body = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return ResponseProvider.bad_request(error='Invalid JSON')

    username = body.get('username')
    purpose  = body.get('purpose', 'password_reset')

    if not username:
        return ResponseProvider.bad_request(error='username is required')

    if purpose not in ['password_reset', 'first_login']:
        return ResponseProvider.bad_request(
            error='purpose must be password_reset or first_login'
        )

    try:
        from django.conf import settings
        from services.services import OTPService

        otp = OTPService.create_otp(username=username, purpose=purpose)

        response_data = {}
        if settings.DEBUG:
            # Show OTP in response during development so it is visible in Postman.
            # Automatically hidden when DEBUG=False in production.
            response_data['dev_otp'] = otp.code
            response_data['note']    = 'dev_otp is shown in DEBUG mode only — remove in production'

        return ResponseProvider.success(
            message=f'OTP sent to the email address registered to {username}. Valid for 10 minutes.',
            data=response_data
        )

    except LookupError as e:
        return ResponseProvider.not_found(error=str(e))
    except Exception as e:
        return ResponseProvider.handle_exception(e)

@csrf_exempt
def user_logout_view(request):
    if request.method != "POST":
        return ResponseProvider.bad_request(error="POST method required")

    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return ResponseProvider.bad_request(error="Invalid JSON")

    refresh_token = body.get("refresh_token")

    if not refresh_token:
        return ResponseProvider.bad_request(error="Refresh token required")

    try:
        AuthService.logout(refresh_token)
        return ResponseProvider.success(message="Successfully logged out")
    except LookupError as e:
        return ResponseProvider.not_found(error="token not found")



@csrf_exempt
def create_user_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        body = json.loads(request.body)
        username = body.get("username")
        password = body.get("password")
        email = body.get("email")
        if not username or not password or not email:
            return JsonResponse({"error": "Username, email and password are required"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email address already exists"}, status=400)
        user = User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({
            "username": user.username,
            "email": user.email,
            "message": "Successfully created user"
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred while creating user: {str(e)}"}, status=500)


@csrf_exempt
def list_users_view(request):
    if request.method not in ["GET"]:
        return ResponseProvider.bad_request(error="GET")

    try:
        json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return ResponseProvider.bad_request(error="Invalid JSON data")

    return UserService.list_users(request)

@csrf_exempt


def delete_user_view(request, uuid):
    """
    View to delete a user by username, It expects a delete request
            - Success response if the user is deleted
            - Bad request if HTTP method is not DELETE or JSON is invalid
            - Not found if the user does not exist
    """
    if request.method != "DELETE":
        return ResponseProvider.bad_request(error="DELETE method required")

    try:
        # Optional: parse JSON if you expect additional data
        json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return ResponseProvider.bad_request(error="Invalid JSON data")

    return UserService.delete_user(uuid)


@csrf_exempt
def update_user_view(request, uuid):
    if request.method not in ["PUT", "PATCH"]:
        return ResponseProvider.bad_request(error="PUT or PATCH required")

    try:
        json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return ResponseProvider.bad_request(error="Invalid JSON data")

    return UserService.update_user(request, uuid)
#--------------------------------------------------------------------------
 #         ROLE VIEWS
#--------------------------------------------------------------------------


@csrf_exempt
def create_role(request):
    if request.method != "POST":
        return ResponseProvider.bad_request(error="POST required")
    body = json.loads(request.body)
    name = body.get("name")
    description = body.get("description", "")

    if not name: return (
        ResponseProvider.bad_request(error="Role name required"))
    if Role.objects.filter(name=name).exists():
        return ResponseProvider.bad_request(error="Role exists")

    role = Role.objects.create(name=name, description=description)
    return ResponseProvider.created(message="Role created", data={ "name": role.name,
                                                                  "description": role.description})



@csrf_exempt
def delete_role_view(request, name:str):
    """
    Delete a role by name.
    Expects:
        DELETE request with JSON body containing:
            - name (str): Name of the role to delete.
    Returns:
        ResponseProvider:
            - Success if the role is deleted.
            - Bad request if method is not DELETE, JSON is invalid, or name is missing.
            - Not found if the role does not exist.
    """
    if request.method != "DELETE":
        return ResponseProvider.bad_request(error="DELETE method required")

    try:
        RoleService().delete_role_by_name(name)
        return ResponseProvider.success(message=f"Role '{name}' deleted successfully")
    except LookupError as e:
        return ResponseProvider.not_found(error=str(e))


@csrf_exempt
def update_role_view(request, username: str):
    if request.method != "PUT":
        return ResponseProvider.bad_request(error="PUT required")

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return ResponseProvider.bad_request(error="Invalid JSON")

    new_role = body.get("role")
    if not new_role:
        return ResponseProvider.bad_request(error="Role is required")

    return RoleService.update_user_role(request, username=username, new_role=new_role)

@csrf_exempt
def list_roles_view(request):
    """
    Retrieve all roles in the system by name.
    Expects:
        GET request.
    Returns:
        ResponseProvider:
            - Success response containing a list of all role names.
            - Bad request if the HTTP method is not GET.
    """
    if request.method != "GET":
        return ResponseProvider.bad_request(error="GET method required")

    try:
        roles = RoleService.get_all_roles()  # returns list of Role objects
        role_names = [role.name for role in roles]  # extract only names
        return ResponseProvider.success(data=role_names)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
def view_user_profile(request, user_uuid):
    if request.method != "GET":
        return JsonResponse({"error": "GET method required"}, status=405)
    try:
        user = User.objects.select_related('role', 'department', 'team', 'status').get(uuid=user_uuid)
        return JsonResponse({
            "uuid":        str(user.uuid),
            "username":    user.username,
            "email":       user.email,
            "phone_number": user.phone_number,
            "role":        user.role.name if user.role else None,
            "department":  user.department.get_name_display() if user.department else None,
            "team":        user.team.team_name if user.team else None,
            "status":      user.status.name if user.status else None,
        }, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred while retrieving user profile: {str(e)}"}, status=500)

@csrf_exempt
@allowed_http_methods(['POST'])
def assign_role_view(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return ResponseProvider.bad_request(error="Invalid JSON")

    username = body.get("username")
    role_name = body.get("role_name")

    if not username or not role_name:
        return ResponseProvider.bad_request(error="username and role_name are required")

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return ResponseProvider.not_found(error=f"User '{username}' not found")

    try:
        UserService.assign_role(user, role_name)
    except ValueError as e:
        return ResponseProvider.not_found(error=str(e))

    return ResponseProvider.success(
        message=f"Role '{role_name}' assigned to '{username}' successfully",
        data={
            "username": user.username,
            "email": user.email,
            "role": user.role.name if user.role else None,
        }
    )