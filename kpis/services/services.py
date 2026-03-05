from Transaction.services.services import TransactionLogHandler
from utils.common import get_clean_request_data
from services.services import KPIService, KPIAssignmentService, TransactionLogService, KPIFormulaService, \
    KPIResultAccountService
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
        kpi_data =cls._serialize(kpi)

        return ResponseProvider.created(
            message=f"{kpi.kpi_name} created successfully",
            data= kpi_data
        )

    @staticmethod
    def _serialize(kpi ):
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
        )
        return ResponseProvider.success(message=f"{kpi.kpi_name} deleted successfully")

    @classmethod
    def get_all_kpis(cls, request) -> ResponseProvider:
        """List KPIs with optional filters.
        Line managers are automatically scoped to their own department.
        """
        filters = {
            'department_uuid': request.GET.get('department_uuid'),
            'measurement_type': request.GET.get('measurement_type'),
            'calculation_type': request.GET.get('calculation_type'),
            'kpi_name': request.GET.get('kpi_name'),
        }
        filters = {k: v for k, v in filters.items() if v is not None}

        # Line managers can only see KPIs belonging to their own department
        if getattr(request, 'is_line_manager', False) and request.department_scope:
            filters['department_uuid'] = str(request.department_scope.uuid)

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
            required_fields={'kpi_uuid', 'period_start'}
        )

        kpi_uuid = data.get('kpi_uuid')
        period_start= data.get('period_start')

        assignment = KPIAssignmentService().create_kpi_assignment(
            kpi_uuid,
            period_start,
            assigned_to_uuid=data.get('assigned_to_uuid'),
            assigned_team_uuid=data.get('assigned_team_uuid'),
            assigned_department_uuid=data.get('assigned_department_uuid'),
            status=data.get('status', ),
            triggered_by=request.user,
            request=request
        )

        return ResponseProvider.created(
            message="KPI assigned successfully",
            data=cls._serialize(assignment)
        )

    @classmethod
    def update_kpi_assignment(cls, request, assignment_uuid: str) -> ResponseProvider:
        """update a KPI assignment by UUID."""
        data = get_clean_request_data(
            request,
            allowed_fields={'period_start', 'status',}
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
    @classmethod
    def get_all_kpi_assignments(cls ,request):
        """returns a list of all KPI assignments.
        Line managers are automatically scoped to their own department.
        """
        filters = {
            'user_uuid': request.GET.get('user_uuid'),
            'team_uuid': request.GET.get('team_uuid'),
            'department_uuid': request.GET.get('department_uuid'),
            'status': request.GET.get('status'),
        }
        filters ={k:v for k,v in filters.items() if v is not None}

        # Line managers can only see assignments within their own department
        if getattr(request, 'is_line_manager', False) and request.department_scope:
            filters['department_uuid'] = str(request.department_scope.uuid)

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
            'period_start': str(assignment.period_start) if assignment.period_start else None,
            'period_end': str(assignment.period_end) if assignment.period_end else None,
            'status': assignment.status.name if assignment.status else None,
            'created_at': str(assignment.created_at),
            'updated_at': str(assignment.updated_at),
        }

#------------------------------------------------------------------------
#    KPI FORMULA HANDLER
#------------------------------------------------------------------------

class KPIFormulaServiceHandler:

    @classmethod
    def create_formula(cls, request) -> ResponseProvider:
        data = get_clean_request_data(
            request,
            required_fields={'kpi_uuid', 'formula_expression'}
        )

        kpi_uuid           = data.get('kpi_uuid')
        formula_expression = data.get('formula_expression')

        formula = KPIFormulaService().create_formula(
            kpi_uuid,
            formula_expression,
            data_source=data.get('data_source', ''),
            triggered_by=request.user,
            request=request
        )

        return ResponseProvider.created(
            message=f"Formula for KPI created successfully",
            data=cls._serialize(formula)
        )

    @classmethod
    def get_formula_by_kpi(cls, kpi_uuid: str) -> ResponseProvider:
        """
           Retrieve a formula by its associated KPI UUID.
           Args:kpi_uuid (str): UUID of the KPI.
           Returns:ResponseProvider: 200 Success with serialized formula data.
           """
        formula = KPIFormulaService().get_by_kpi_uuid(kpi_uuid)
        return ResponseProvider.success(data=cls._serialize(formula))

    @classmethod
    def update_formula(cls, request, formula_uuid: str) -> ResponseProvider:
        data = get_clean_request_data(
            request,
            allowed_fields={'formula_expression', 'data_source'}
        )

        formula = KPIFormulaService().update_formula(
            formula_uuid,
            data,
            triggered_by=request.user,
            request=request
        )
        return ResponseProvider.success(
            message="Formula updated successfully",
            data=cls._serialize(formula)
        )

    """
        Converting a KPIFormula Django model to JSON-safe dictionary
    """
    @staticmethod
    def _serialize(formula) -> dict:
        return {
            'uuid': str(formula.uuid),
            'kpi_uuid': str(formula.kpi.uuid),
            'kpi_name': formula.kpi.kpi_name,
            'formula_expression': formula.formula_expression,
            'data_source': formula.data_source,
            'created_at': str(formula.created_at),
            'updated_at': str(formula.updated_at),
        }

    @classmethod
    def delete_formula(cls, request, formula_uuid: str) -> ResponseProvider:
        formula = KPIFormulaService().delete_formula(
            formula_uuid,
            triggered_by=request.user,
            request=request
        )
        return ResponseProvider.success(
            message=f"Formula {formula.formula_name} deleted successfully",
        )

class KPIResultService:

    @classmethod
    def submit_result(cls, request) -> ResponseProvider:
        """A user or system submits an actual_value for a KPI assignment."""
        data = get_clean_request_data(
            request,
            required_fields={'assignment_uuid', 'actual_value'}
        )

        result = KPIResultAccountService().create_result(
            data.get('assignment_uuid'),
            data.get('actual_value'),
            triggered_by=request.user,
            request=request
        )

        return ResponseProvider.created(
            message="KPI result submitted successfully",
            data=cls._serialize(result)
        )

    @classmethod
    def get_result(cls, request, result_uuid: str) -> ResponseProvider:
        result = KPIResultAccountService().get_by_uuid(result_uuid)

        if request.user.role.name.lower() == 'employee':
            if result.kpi_assignment.assigned_to != request.user:
                return ResponseProvider.forbidden(
                    message='You do not have permission to view this result'
                )

        return ResponseProvider.success(data=cls._serialize(result))

    @classmethod
    def get_all_results(cls, request) -> ResponseProvider:
        filters = {
            'user_uuid':       request.GET.get('user_uuid'),
            'team_uuid':       request.GET.get('team_uuid'),
            'department_uuid': request.GET.get('department_uuid'),
            'period_start':    request.GET.get('period_start'),
            'period_end':      request.GET.get('period_end'),
        }
        filters = {k: v for k, v in filters.items() if v is not None}

        if request.user.role and request.user.role.name.lower() == 'employee':
            # Employees can only see their own results
            filters['user_uuid'] = str(request.user.uuid)
        elif getattr(request, 'is_line_manager', False) and request.department_scope:
            # Line managers can only see results within their own department
            filters['department_uuid'] = str(request.department_scope.uuid)

        results = KPIResultAccountService().get_all_results(**filters)
        return ResponseProvider.success(data=[cls._serialize(r) for r in results])

    @classmethod
    def update_result(cls, request, result_uuid: str) -> ResponseProvider:
        data = get_clean_request_data(
            request,
            allowed_fields={'actual_value'}
        )

        result = KPIResultAccountService().update_result(
            result_uuid,
            data,
            triggered_by=request.user,
            request=request
        )
        return ResponseProvider.success(
            message="KPI result updated successfully",
            data=cls._serialize(result)
        )

    @staticmethod
    def export_results_csv(request) -> ResponseProvider:
        filters = {
            'department_uuid': request.GET.get('department_uuid'),
            'team_uuid':       request.GET.get('team_uuid'),
            'period_start':    request.GET.get('period_start'),
            'period_end':      request.GET.get('period_end'),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        return KPIResultAccountService().export_csv(**filters)

    @staticmethod
    def _serialize(result) -> dict:
        return {
            'uuid': str(result.uuid),
            'assignment_uuid': str(result.kpi_assignment.uuid),
            'kpi_name': result.kpi_assignment.kpi.kpi_name,
            'assigned_to_uuid': str(
                result.kpi_assignment.assigned_to.uuid) if result.kpi_assignment.assigned_to else None,
            'assigned_to_username': result.kpi_assignment.assigned_to.username if result.kpi_assignment.assigned_to else None,
            'actual_value': str(result.actual_value),
            'calculated_score': str(result.calculated_score) if result.calculated_score else None,
            'rating': result.rating,  # was result.comment before
            'comment': result.comment,  # free text comment if any
            'recorded_by_uuid': str(result.recorded_by.uuid) if result.recorded_by else None,
            'created_at': str(result.created_at),
            'updated_at': str(result.updated_at),
        }