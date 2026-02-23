from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .jwt_utils import decode_token

User = get_user_model()

class JWTAuthenticationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response  # only assignment
          #
    def __call__(self, request):
        if request.path in ["/api/auth/login/", "/api/auth/register/"]:
            return self.get_response(request)
        # Only check protected paths
        if request.path.startswith("/api/"):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return JsonResponse({"error": "Authorization header missing"}, status=401)

            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return JsonResponse({"error": "Invalid token format"}, status=401)

            payload = decode_token(token)  # only here, inside __call__
            if "error" in payload:
                return JsonResponse(payload, status=401)

            if payload.get("type") != "access":
                return JsonResponse({"error": "Access token required"}, status=401)

            try:
                request.user = User.objects.get(id=payload["user_id"])
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=401)

        response = self.get_response(request)
        return response
