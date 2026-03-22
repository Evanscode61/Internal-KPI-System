from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied

class ResponseProvider:
    @staticmethod
    def _response(success, code, message, status, data=None, error=None):
        return JsonResponse({'success': success,'code': code,'message': message,'data': data or {},'error': error or ''},status=status,encoder=DjangoJSONEncoder)
    @classmethod
    def handle_exception(cls, ex):
        if isinstance(ex, ValidationError): error = ", ".join(ex.messages) if hasattr(ex, "messages") else str(ex); return cls.bad_request("Validation Error", error)
        if isinstance(ex, ValueError): return cls.bad_request("Bad Request", str(ex))
        if isinstance(ex, ObjectDoesNotExist): return cls.not_found(error=str(ex))
        if isinstance(ex, PermissionDenied): return cls.forbidden(error=str(ex))
        return cls.server_error(error=str(ex))
    @classmethod
    def success(cls, code='200', message='Success', data=None):
        return cls._response(True, code, message, 200, data=data)
    @classmethod
    def created(cls, code='201', message='Created', data=None):
        return cls._response(True, code, message, 201, data=data)
    @classmethod
    def bad_request(cls, code='400', message='Bad Request', error=None):
        return cls._response(False, code, message, 400, error=error)
    @classmethod
    def unauthorized(cls, code='401', message='Unauthorized', error=None):
        return cls._response(False, code, message, 401, error=error)
    @classmethod
    def forbidden(cls, code='403', message='Forbidden', error=None):
        return cls._response(False, code, message, 403, error=error)
    @classmethod
    def not_found(cls, code='404', message='Resource Not Found', error=None):
        return cls._response(False, code, message, 404, error=error)
    @classmethod
    def server_error(cls, code='500', message='Internal Server Error', error=None):
        return cls._response(False, code, message, 500, error=error)
