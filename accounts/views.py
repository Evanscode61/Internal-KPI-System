from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from accounts.jwt_utils import generate_access_token, generate_refresh_token, decode_token
import json
from accounts.models import User, Role
from services.services import UserService, RoleService ,AuthService
from services.utils.response_provider import ResponseProvider

user_service = UserService()


@csrf_exempt
def register_view(request):
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
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    body = json.loads(request.body)
    username = body.get("username")
    password = body.get("password")
    email = body.get("email")

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    return JsonResponse({
        "access_token": access_token,
        "refresh_token": refresh_token
    })


@csrf_exempt
def refresh_view(request):
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
        #user=  authenticate(request, refresh_token=payload["refresh_token"])
        user = user_service.authenticate.get(id=payload["user_id"])
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=401)

    new_access_token = generate_access_token(user)

    return JsonResponse({
        "access_token": new_access_token
    })
@csrf_exempt
def reset_password_view(request):
    if request.method != "POST":
        return ResponseProvider.bad_request(error="POST method required")

    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return ResponseProvider.bad_request(error="Invalid JSON")

    try:
        UserService.reset_password(
            username=body.get("username"),
            old_password=body.get("old_password"),
            new_password=body.get("new_password"),
            confirm_password=body.get("confirm_password"),
        )
        return ResponseProvider.success(message="Password reset successful")

    except ValueError as e:
        return ResponseProvider.bad_request(error="Incorrect password")

@csrf_exempt
def logout_view(request):
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
    if request.method not in ["PUT", "PATCH"]:
        return ResponseProvider.bad_request(error="PUT or PATCH required")

    try:
        json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return ResponseProvider.bad_request(error="Invalid JSON data")

    return UserService.list_users(request)


@csrf_exempt
def update_user_view(request, username):
    if request.method not in ["PUT", "PATCH"]:
        return ResponseProvider.bad_request(error="PUT or PATCH required")

    try:
        json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return ResponseProvider.bad_request(error="Invalid JSON data")

    return UserService.update_user(request, username)


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
    return ResponseProvider.created(message="Role created", data={"id": role.id, "name": role.name,
                                                                  "description": role.description})


""" Deleting a role from the database,
only admin"""


@csrf_exempt
def delete_role_view(request):
    if request.method != "DELETE":
        return ResponseProvider.bad_request(error="DELETE required")

    try:
        role_name = json.loads(request.body).get("name")
    except Exception:
        return ResponseProvider.bad_request(error="Invalid JSON")

    if not role_name:
        return ResponseProvider.bad_request(error="Role ID required")

    return RoleService.delete_role(role_name)


@csrf_exempt
def update_role_view(request, username):
    if request.method != "PUT":
        return ResponseProvider.bad_request(error="PUT required")
    body = json.loads(request.body)
    new_role = body.get("role")
    if not new_role:
        return ResponseProvider.bad_request(error="Role is required")
    return RoleService.update_user_role(request, username, new_role)
