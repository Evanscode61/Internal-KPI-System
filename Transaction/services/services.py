from Transaction.models import TransactionLog
from services.services import TransactionLogService
from services.utils.response_provider import ResponseProvider


class TransactionLogHandler:

    @classmethod
    def get_all_logs(cls, request) -> ResponseProvider:
        filters = {
            'user_uuid':   request.GET.get('user_uuid'),
            'action':      request.GET.get('action'),
            'object_type': request.GET.get('object_type'),
            'time_from':   request.GET.get('time_from'),
            'time_to':     request.GET.get('time_to'),
        }
        filters = {k: v for k, v in filters.items() if v is not None}

        logs = TransactionLogService.get_all_logs(**filters)
        data = [cls._serialize(log) for log in logs]
        return ResponseProvider.success(data=data)

    @classmethod
    def get_log(cls, log_uuid: str) -> ResponseProvider:
        log = TransactionLogService.get_by_uuid(log_uuid)
        return ResponseProvider.success(data=cls._serialize(log))

    @staticmethod
    def _serialize(log) -> dict:
        return {
            'uuid':         str(log.uuid),
            'event_type':   log.event_type.code if log.event_type else None,
            'triggered_by': log.triggered_by.username if log.triggered_by else None,
            'entity_type':  log.entity_type,
            'entity_uuid':  str(log.entity_uuid) if log.entity_uuid else None,
            'message':      log.message,
            'status':       log.status.code if log.status else None,
            'ip_address':   log.ip_address,
            'metadata':     log.metadata,
            'created_at':   str(log.created_at),
        }