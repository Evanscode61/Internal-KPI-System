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
            required_fields={'kpi_name','measurement_type','calculation_type','weight_value','kpi_description','department_uuid','min_threshold','max_threshold'},
        )
        service = KPIService()
        min_threshold = data.get('min_threshold')
        max_threshold = data.get('max_threshold')

        if min_threshold and max_threshold:
            if float(min_threshold) == float(max_threshold):
                return ResponseProvider.bad_request(
                    message='Min threshold and max threshold cannot be equal — this would cause division by zero in formula calculations.'
                )

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
            "frequency": kpi.frequency if kpi.frequency else None,
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
                'min_threshold', 'max_threshold', 'department_uuid','frequency'
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
            required_fields={'kpi_uuid', 'period_start' }
        )

        kpi_uuid = data.get('kpi_uuid')
        period_start= data.get('period_start')
        period_end = data.get('period_end')
        assigned_to = data.get('assigned_to')
        assigned_team_uuid = data.get('assigned_team_uuid')
        assigned_department_uuid = data.get('assigned_department_uuid')
        status = data.get('status')

        assignment = KPIAssignmentService().create_kpi_assignment(
            kpi_uuid,
            period_start,
            period_end,
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
            allowed_fields={'period_start', 'period_end', 'status',
    'assigned_to_uuid', 'assigned_team_uuid',
    'assigned_department_uuid', 'kpi_uuid',}
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
    def delete_kpi_assignment(cls, request, assignment_uuid: str) -> ResponseProvider:
        assignment = KPIAssignmentService().delete_assignment(
            assignment_uuid,
            triggered_by=request.user,
            request=request
        )
        # Line managers can only delete assignments within their own department
        if getattr(request, 'is_line_manager', False) and request.department_scope:
            if assignment.assigned_department != request.department_scope:
                return ResponseProvider.forbidden(
                    message="You can only delete assignments within your own department"
                )
        kpi_name = assignment.kpi.kpi_name if assignment.kpi else assignment_uuid
        return ResponseProvider.success(
            message=f"KPI assignment for '{kpi_name}' deleted successfully"
        )

    @classmethod
    def get_all_kpi_assignments(cls, request):
        filters = {
            'user_uuid': request.GET.get('user_uuid'),
            'team_uuid': request.GET.get('team_uuid'),
            'department_uuid': request.GET.get('department_uuid'),
            'status': request.GET.get('status'),
        }
        filters = {k: v for k, v in filters.items() if v is not None}

        role_name = request.user.role.name if request.user.role else ''

        # Employees only see their own assignments
        if role_name == 'employee':
            filters['user_uuid'] = str(request.user.uuid)

        # Line managers only see assignments in their department
        elif role_name in ('Business_Line_Manager', 'Tech_Line_Manager'):
            if request.user.department:
                filters['department_uuid'] = str(request.user.department.uuid)

        assignments = KPIAssignmentService().get_all_assignments(**filters)
        data = [cls._serialize(a) for a in assignments]
        return ResponseProvider.success(data=data)

    @staticmethod
    def _serialize(assignment) -> dict:
        return {
            'uuid': str(assignment.uuid),
            'kpi_uuid': str(assignment.kpi.uuid),
            'kpi_name': assignment.kpi.kpi_name,
            'kpi_description': assignment.kpi.kpi_description or '',
            'measurement_type': assignment.kpi.measurement_type or '',
            'weight_value': float(assignment.kpi.weight_value) if assignment.kpi.weight_value else None,
            'target_value': float(assignment.target_value) if assignment.target_value else None,
            'min_threshold': float(assignment.kpi.min_threshold) if assignment.kpi.min_threshold else None,
            'max_threshold': float(assignment.kpi.max_threshold) if assignment.kpi.max_threshold else None,
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
            'created_at': assignment.created_at.strftime('%Y-%m-%d %H:%M') if assignment.created_at else None,
            'updated_at': assignment.updated_at.strftime('%Y-%m-%d %H:%M') if assignment.updated_at else None,
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
            formula_template=data.get('formula_template'),
            data_source=data.get('data_source', ''),
            triggered_by=request.user,
            request=request
        )

        return ResponseProvider.created(
            message=f"Formula for KPI created successfully",
            data=cls._serialize(formula)
        )

    @classmethod
    def get_formula_by_kpi(cls, request, kpi_uuid: str) -> ResponseProvider:
        # Check the KPI belongs to the manager's department
        if getattr(request, 'is_line_manager', False) and request.department_scope:
            from kpis.models import KpiDefinition
            kpi = KpiDefinition.objects.filter(uuid=kpi_uuid).first()
            if not kpi or kpi.department != request.department_scope:
                return ResponseProvider.forbidden(message='Access denied')

        formula = KPIFormulaService().get_by_kpi_uuid(kpi_uuid)

        # Return null data if no formula exists instead of crashing
        if not formula:
            return ResponseProvider.success(data=None)

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
        if not formula:
            return None
        return {
            'uuid': str(formula.uuid),
            'kpi_uuid': str(formula.kpi.uuid),
            'kpi_name': formula.kpi.kpi_name,
            'formula_template' :formula.formula_template,
            'formula_expression': formula.formula_expression,
            'data_source': formula.data_source,
            'created_at': formula.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': formula.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
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

class  KPIResultService:

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
        role = request.user.role.name if request.user.role else ''
        if role.lower() == 'employee':
            if result.kpi_assignment.assigned_to != request.user:
                return ResponseProvider.forbidden(
                    message='You do not have permission to view this result'
                )
        return ResponseProvider.success(data=cls._serialize(result))

    @classmethod
    def get_all_results(cls, request) -> ResponseProvider:
        filters = {
            'user_uuid': request.GET.get('user_uuid'),
            'team_uuid': request.GET.get('team_uuid'),
            'department_uuid': request.GET.get('department_uuid'),
            'period_start': request.GET.get('period_start'),
            'period_end': request.GET.get('period_end'),
        }
        filters = {k: v for k, v in filters.items() if v is not None}

        role = request.user.role.name if request.user.role else ''

        if role.lower() == 'employee':
            filters['user_uuid'] = str(request.user.uuid)
        elif role in ('Business_Line_Manager', 'Tech_Line_Manager'):
            if request.user.department:
                filters['department_uuid'] = str(request.user.department.uuid)
        # admin and hr — no filter, sees everything

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

    @classmethod
    def delete_result(cls, request, result_uuid: str) -> ResponseProvider:
        result = KPIResultAccountService().get_by_uuid(result_uuid)
        role = request.user.role.name if request.user.role else ''

        if role == 'admin':
            pass
        elif role in ('Business_Line_Manager', 'Tech_Line_Manager'):
            if result.approval_status == 'approved':
                return ResponseProvider.forbidden(message='Approved results cannot be deleted')
            assignment = result.kpi_assignment
            manager_dept = request.user.department
            result_dept = (
                assignment.assigned_to.department if assignment.assigned_to else
                assignment.assigned_department if assignment.assigned_department else
                assignment.assigned_team.department if assignment.assigned_team else None
            )
            if result_dept != manager_dept:
                return ResponseProvider.forbidden(message='You can only delete results within your department')
        elif role.lower() == 'employee':
            if result.submitted_by != request.user:
                return ResponseProvider.forbidden(message='You can only delete your own results')
            if result.approval_status == 'approved':
                return ResponseProvider.forbidden(message='You cannot delete an approved result')
        else:
            return ResponseProvider.forbidden(message='You do not have permission to delete results')

        from Base.models import Status
        from django.utils import timezone
        active_status = Status.objects.filter(code='ACT').first()
        if active_status:
            result.kpi_assignment.status = active_status
            result.kpi_assignment.save(update_fields=['status'])

        result.is_deleted = True
        result.deleted_at = timezone.now()
        result.deleted_by = request.user
        result.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

        return ResponseProvider.success(
            message=f'Result for "{result.kpi_assignment.kpi.kpi_name}" deleted successfully'
        )

    @classmethod
    def approve_reject_result(cls, request, result_uuid: str) -> ResponseProvider:
        data = get_clean_request_data(
            request,
            required_fields={'approval_status'},
            allowed_fields={'approval_status', 'manager_comment'}
        )

        approval_status = data.get('approval_status')
        if approval_status not in ('approved', 'rejected'):
            return ResponseProvider.bad_request(
                message="approval_status must be 'approved' or 'rejected'"
            )

        # Fetch result with all related data in one query
        result = KPIResultAccountService().get_by_uuid(result_uuid)
        assignment = result.kpi_assignment
        kpi = assignment.kpi
        manager_comment = data.get('manager_comment', '')

        # Department scope check for managers
        role = request.user.role.name if request.user.role else ''
        if role in ('Business_Line_Manager', 'Tech_Line_Manager'):
            manager_dept = request.user.department
            result_dept = (
                assignment.assigned_to.department if assignment.assigned_to else
                assignment.assigned_department if assignment.assigned_department else
                assignment.assigned_team.department if assignment.assigned_team else None
            )
            if result_dept != manager_dept:
                return ResponseProvider.forbidden(
                    message='You can only review results within your department'
                )

        # Save result and wrap all writes in atomic transaction
        from django.db import transaction
        from Base.models import Status
        from performance.models import Notification
        from performance.email_service import EmailNotificationService

        with transaction.atomic():
            result.approval_status = approval_status
            result.manager_comment = manager_comment
            result.reviewed_by = request.user
            result.save(update_fields=['approval_status', 'manager_comment', 'reviewed_by'])

            #  Revert assignment to Active if rejected
            if approval_status == 'rejected':
                active_status = Status.objects.filter(code='ACT').first()
                if active_status:
                    assignment.status = active_status
                    assignment.save(update_fields=['status'])

            # Build notification message
            employee = result.submitted_by or assignment.assigned_to
            if employee:
                if approval_status == 'approved':
                    message = (
                        f'Your result for "{kpi.kpi_name}" has been approved. '
                        f'Score: {result.calculated_score}% — Rated {result.rating}.'
                    )
                else:
                    message = (
                        f'Your result for "{kpi.kpi_name}" has been rejected by your manager. '
                        f'{("Reason: " + manager_comment + ".") if manager_comment else ""} '
                        f'Please resubmit with the correct value.'
                    )

                # In-app notification
                Notification.objects.create(
                    recipient=employee,
                    notification_type='kpi_alert',
                    message=message,
                    is_read=False,
                )

        # Send email outside transaction , email failure should not rollback DB
        try:
            if employee:
                if approval_status == 'approved':
                    EmailNotificationService.send_result_approved_email(
                        employee=employee,
                        kpi_name=kpi.kpi_name,
                        score=result.calculated_score,
                        rating=result.rating,
                    )
                else:
                    EmailNotificationService.send_result_rejected_email(
                        employee=employee,
                        kpi_name=kpi.kpi_name,
                        manager_comment=manager_comment,
                    )
        except Exception as e:
            print(f'[Email ERROR] {e}')

        return ResponseProvider.success(
            message=f'Result {approval_status} successfully',
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
        kpi        = result.kpi_assignment.kpi
        assignment = result.kpi_assignment
        return {
            'uuid':                 str(result.uuid),
            'assignment_uuid':      str(assignment.uuid),
            'kpi_name':             kpi.kpi_name,
            'kpi_uuid':             str(kpi.uuid),
            'target':               float(kpi.max_threshold) if kpi.max_threshold else None,
            'weight':               float(kpi.weight_value) if kpi.weight_value else None,
            'actual_value':         str(result.actual_value),
            'calculated_score':     str(result.calculated_score) if result.calculated_score else None,
            'rating':               result.rating,
            'comment':              result.comment,
            'approval_status':      result.approval_status,
            'manager_comment':      result.manager_comment or '',
            'reviewed_by':          result.reviewed_by.username if result.reviewed_by else None,
            'period_start':         str(assignment.period_start) if assignment.period_start else None,
            'period_end':           str(assignment.period_end) if assignment.period_end else None,
            'assigned_to_uuid':     str(assignment.assigned_to.uuid) if assignment.assigned_to else None,
            'assigned_to_username': assignment.assigned_to.username if assignment.assigned_to else None,
            'department':           assignment.assigned_to.department.name if assignment.assigned_to and assignment.assigned_to.department else None,
            'submitted_by':         result.submitted_by.username if result.submitted_by else None,
            'recorded_by_uuid':     str(result.recorded_by.uuid) if result.recorded_by else None,
            'created_at':           str(result.created_at),
            'updated_at':           str(result.updated_at),
            'measurement_type' : kpi.measurement_type,
        }