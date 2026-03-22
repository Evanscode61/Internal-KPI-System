import uuid
from functools import wraps
from services.utils.response_provider import ResponseProvider
from django.core.exceptions import PermissionDenied

class ServiceBase(object):
    manager = None

    def all(self, *args, **kwargs):
        return self.manager.all(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.manager.get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return self.manager.filter(*args, **kwargs)

    def create(self, *args, **kwargs):
        return self.manager.create(**kwargs)

    def update(self, uuid, **kwargs):
        instance = self.manager.get(uuid=uuid)
        for field, value in kwargs.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def delete(self, uuid):
        queryset = self.manager.filter(uuid=uuid)
        return queryset.delete()

    def exists(self, *args, **kwargs):
        return self.manager.exists(*args, **kwargs)


def service_handler(require_auth=True, allowed_roles=None):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            try:
                if require_auth and (not request.user or not request.user.is_authenticated):
                    return ResponseProvider.unauthorized(error="Authentication required")

                if allowed_roles:
                    user_role = getattr(request.user.role, "name", None)
                    if user_role not in allowed_roles:
                        return ResponseProvider.forbidden(error="You do not have permission")

                return func(request, *args, **kwargs)

            except Exception as ex:
                return ResponseProvider.handle_exception(ex)

        return wrapper
    return decorator
