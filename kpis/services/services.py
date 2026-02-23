from Transaction.services.services import TransactionLogHandler
from utils.common import get_clean_request_data
from services.services import KPIService, KPIAssignmentService, TransactionLogService
from services.utils.response_provider import ResponseProvider


class KPIDefinitionHandler:
    """
        Handles KPI Definition operations.

        This handler acts as the business logic layer between
        views and services. It processes requests, validates input,
        calls the appropriate service methods, and formats responses.
        """
    @classmethod
    def create_kpi(cls, request):
        data = get_clean_request_data(
            request,
            required_fields={'kpi_name','measurement_type','calculation_type','weight_value'}
        )
        service = KPIService()

        kpi = service.create_kpi(
            kpi_name=data['kpi_name'],
            measurement_type=data['measurement_type'],
            calculation_type=data['calculation_type'],
            weight_value=data['weight_value'],
            kpi_description=data.get('kpi_description',''),
            department_uuid=data.get('department_uuid'),
            min_threshold=data.get('min_threshold'),
            max_threshold=data.get('max_threshold'),
            triggered_by=request.user,
        )

        return ResponseProvider.created(
            message=f"{kpi.kpi_name} created successfully",
            data=cls._serialize(kpi)
        )

    @staticmethod
    def _serialize(kpi):
        return {
            "uuid": str(kpi.uuid),
            "kpi_name": kpi.kpi_name,
            "kpi_description": kpi.kpi_description,
            "department": kpi.department.name if kpi.department else None,
            "measurement_type": kpi.measurement_type,
            "calculation_type": kpi.calculation_type,
            "weight_value": float(kpi.weight_value),
            "min_threshold": float(kpi.min_threshold) if kpi.min_threshold is not None else None,
            "max_threshold": float(kpi.max_threshold) if kpi.max_threshold is not None else None,
            "created_by": kpi.created_by.username if kpi.created_by else None,
            "created_at": kpi.created_at.isoformat(),
        }

    @classmethod
    def get_kpi(cls, kpi_uuid: str) -> ResponseProvider:
        """
              Retrieve a single KPI definition by UUID.
              Args:
                  kpi_uuid (str): Unique identifier of the KPI.
              Returns:
                  ResponseProvider: API response containing the KPI data.
              """
        kpi = KPIService().get_by_uuid(kpi_uuid)
        return ResponseProvider.success(data=cls._serialize(kpi))

    @classmethod
    def update_kpi(cls, request, kpi_uuid: str) -> ResponseProvider:
        """update a KPI definition by UUID."""
        data = get_clean_request_data(
            request,
            allowed_fields={
                'kpi_name', 'kpi_description', 'measurement_type',
                'calculation_type', 'weight_value',
                'min_threshold', 'max_threshold', 'department_uuid'
            }
        )
        service = KPIService()

        kpi = service.update_kpi(
            kpi_uuid,
            data,
            triggered_by=request.user,
            request=request
        )
        return ResponseProvider.success(
            message=f"{kpi.kpi_name} updated successfully",
            data=cls._serialize(kpi)
        )

    @staticmethod
    def delete_kpi(request, kpi_uuid: str) -> ResponseProvider:
        """Delete a KPI definition by UUID."""
        service = KPIService()

        kpi = service.delete_kpi(
            kpi_uuid,
            triggered_by=request.user,
            request=request
        )
        return ResponseProvider.success(message=f"{kpi.kpi_name} deleted successfully")

    @classmethod
    def get_all_kpis(cls, request) -> ResponseProvider:
        """List KPIs with optional filters."""
        filters = {
            'department_uuid': request.GET.get('department_uuid'),
            'measurement_type': request.GET.get('measurement_type'),
            'calculation_type': request.GET.get('calculation_type'),
            'kpi_name': request.GET.get('kpi_name'),
        }
        # Drop None values so the service can apply only what's provided
        filters = {k: v for k, v in filters.items() if v is not None}

        kpis = KPIService().get_all_kpis(**filters)
        data = [cls._serialize(kpi) for kpi in kpis]
        return ResponseProvider.success(data=data)

#--------------------------------------------------------------
#  KPI ASSIGNMENT HANDLER
#--------------------------------------------------------------
class KPIAssignmentHandler:
    """Handles KPI Assignment operation"""
    @classmethod
    def assign_kpi(cls, request) -> ResponseProvider:
        """create a new KPI assignment"""
        data = get_clean_request_data(
            request,
            required_fields={'kpi_uuid', 'assigned_period'}
        )

        kpi_uuid = data.get('kpi_uuid')
        assigned_period = data.get('assigned_period')

        assignment = KPIAssignmentService().create_kpi_assignment(
            kpi_uuid,
            assigned_period,
            assigned_to_uuid=data.get('assigned_to_uuid'),
            assigned_team_uuid=data.get('assigned_team_uuid'),
            assigned_department_uuid=data.get('assigned_department_uuid'),
            status=data.get('status', 'active'),
            triggered_by=request.user,
            request=request
        )

        return ResponseProvider.created(
            message="KPI assigned successfully",
            data=cls._serialize(assignment)
        )

    @classmethod
    def update_kpi_assignment(cls, request, assignment_uuid: str) -> ResponseProvider:
        data = get_clean_request_data(
            request,
            allowed_fields={'assigned_period', 'status'}
        )

        assignment = KPIAssignmentService().update_assignment(
            assignment_uuid,
            data,
            triggered_by=request.user,
            request=request
        )
        return ResponseProvider.success(
            message="Assignment updated successfully",
            data=cls._serialize(assignment)
        )
    def get_all_kpi_assignments(cls ,request):
        filters = {
            'user_uuid': request.GET.get('user_uuid'),
            'team_uuid': request.GET.get('team_uuid'),
            'department_uuid': request.GET.get('department_uuid'),
            'status': request.GET.get('status'),
        }
        filters ={k:v for k,v in filters.items() if v is not None}
        assignments = KPIAssignmentService().get_all_assignments(**filters)
        data = [cls._serialize(a) for a in assignments]
        return ResponseProvider.success(data=data)



    @staticmethod
    def _serialize(assignment) -> dict:
        return {
            'uuid': str(assignment.uuid),
            'kpi_uuid': str(assignment.kpi.uuid),
            'kpi_name': assignment.kpi.kpi_name,
            'assigned_to_uuid': str(assignment.assigned_to.uuid) if assignment.assigned_to else None,
            'assigned_to_username': assignment.assigned_to.username if assignment.assigned_to else None,
            'assigned_team_uuid': str(assignment.assigned_team.uuid) if assignment.assigned_team else None,
            'assigned_team_name': assignment.assigned_team.team_name if assignment.assigned_team else None,
            'assigned_department_uuid': str(
                assignment.assigned_department.uuid) if assignment.assigned_department else None,
            'assigned_department_name': assignment.assigned_department.name if assignment.assigned_department else None,
            'assigned_period': str(assignment.assigned_period),
            'status': assignment.status,
            'created_at': str(assignment.created_at),
            'updated_at': str(assignment.updated_at),
        }


