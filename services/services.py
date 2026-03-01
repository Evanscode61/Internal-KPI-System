from ipaddress import ip_address

from ipaddress import ip_address
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model

import kpis
from Base.models import Status
from accounts.models import Role, RefreshToken
from kpis.models import KpiDefinition, KpiAssignment, KPIResults, KPIFormula
from Transaction.models import TransactionLog, EventTypes
from organization.models import Department, Team
from services.serviceBase import ServiceBase, service_handler
from services.utils.response_provider import ResponseProvider
import json

User = get_user_model()
#-----------------------------------------------------------------------------
# TEAM SERVICE
#----------------------------------------------------------------------------

class TeamService(ServiceBase):
    manager = Team.objects

    def get_by_uuid(self, team_uuid: str):
        return self.manager.get(uuid=team_uuid)

    def get_all_teams(self, **filters):
        qs = self.manager.all()
        if 'department_uuid' in filters:
            qs = qs.filter(department__uuid=filters['department_uuid'])
        return qs


    def create_team(self, team_name, department_uuid, triggered_by: User, request=None):
        department = DepartmentService().get_by_uuid(department_uuid)

        team = self.manager.create(
            team_name=team_name,
            department=department,
        )

        try:
            TransactionLogService.log(
                event_code='team_created',
                triggered_by=triggered_by,
                entity=team,
                status_code='ACT',
                message=f'Team "{team.team_name}" created under "{department.name}"',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'team_id': str(team.uuid),
                    'team_name': team.team_name,
                    'department_id': str(department.uuid),
                    'department_name': department.name,
                    'created_by': triggered_by.email,
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return team

    def update_team(self, team_uuid: str, data: dict, triggered_by: User, request=None):
        team = self.get_by_uuid(team_uuid)

        old_values = {field: str(getattr(team, field, None)) for field in data}

        # Handle department UUID → FK resolution separately
        if 'department_uuid' in data:
            team.department = DepartmentService().get_by_uuid(data.pop('department_uuid'))

        for field, value in data.items():
            setattr(team, field, value)
        team.save()

        try:
            TransactionLogService.log(
                event_code='team_updated',
                triggered_by=triggered_by,
                entity=team,
                status_code='ACT',
                message=f'Team "{team.team_name}" updated',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'team_id': str(team.uuid),
                    'team_name': team.team_name,
                    'updated_by': triggered_by.email,
                    'changed_fields': list(data.keys()),
                    'old_values': old_values,
                    'new_values': {k: str(v) for k, v in data.items()},
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return team

    @service_handler(require_auth=True, allowed_roles=["admin", ])
    def delete_team(self, team_uuid: str, triggered_by: User, request=None):
        team = self.get_by_uuid(team_uuid)
        team.delete()

        try:
            TransactionLogService.log(
                event_code='team_deleted',
                triggered_by=triggered_by,
                entity=team,
                status_code='ACT',
                message=f'Team "{team.team_name}" deleted',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'team_name': team.team_name,
                    'deleted_by': triggered_by.email,
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return team

    def assign_user(self, user_uuid: str, team_uuid: str, triggered_by: User, request=None):
        user = User.objects.get(uuid=user_uuid)
        team = self.get_by_uuid(team_uuid)

        user.team       = team
        user.department = team.department
        user.save(update_fields=['team', 'department'])

        try:
            TransactionLogService.log(
                event_code='user_assigned_to_team',
                triggered_by=triggered_by,
                entity=user,
                status_code='ACT',
                message=f'{user.email} assigned to team "{team.team_name}"',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'user_id': str(user.uuid),
                    'user_email': user.email,
                    'team_id': str(team.uuid),
                    'team_name': team.team_name,
                    'department_name': team.department.name if team.department else None,
                    'assigned_by': triggered_by.email,
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return team
#----------------------------------------------------------------
# DEPARTMENT SERVICE
#-----------------------------------------------------------------

class DepartmentService(ServiceBase):
    manager = Department.objects
    """service that handles business logic related to departments, that is creation, updating 
    retrieving and deleting departments."""

    def get_all_departments(self):
            return self.manager.all()

    def get_by_uuid(self, dept_uuid: str):
            return self.manager.get(uuid=dept_uuid)

    @service_handler(require_auth=True, allowed_roles=["admin", ])
    def create_department(self, name, description='', triggered_by: User = None, request=None):
        department = self.manager.create(
            name=name,
            description=description,
        )
        try:
            TransactionLogService.log(
                event_code='department_created',
                triggered_by=triggered_by,
                entity=department,
                status_code='ACT',
                message=f'Department "{department.name}" created',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'department_id': str(department.uuid),
                    'department_name': department.name,
                    'created_by': triggered_by.email,
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return department

    @service_handler(require_auth=True, allowed_roles=["admin", ])
    def update_department(self, dept_uuid: str, data: dict, triggered_by: User, request=None):
        department = self.get_by_uuid(dept_uuid)

        old_values = {field: str(getattr(department, field, None)) for field in data}

        for field, value in data.items():
            setattr(department, field, value)
        department.save(update_fields=list(data.keys()))

        try:
            TransactionLogService.log(
                event_code='department_updated',
                triggered_by=triggered_by,
                entity=department,
                status_code='ACT',
                message=f'Department "{department.name}" updated',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'department_id': str(department.uuid),
                    'department_name': department.name,
                    'updated_by': triggered_by.email,
                    'changed_fields': list(data.keys()),
                    'old_values': old_values,
                    'new_values': {k: str(v) for k, v in data.items()},
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return department

    @service_handler(require_auth=True, allowed_roles=["admin",])
    def delete_department(self, dept_uuid: str, triggered_by: User, request=None):
        department = self.get_by_uuid(dept_uuid)
        department.delete()

        try:
            TransactionLogService.log(
                event_code='department_deleted',
                triggered_by=triggered_by,
                entity=department,
                status_code='ACT',
                message=f'Department "{department.name}" deleted',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'department_name': department.name,
                    'deleted_by': triggered_by.email,
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return department



#----------------------------------------------------------------
#  KPI DEFINITION SERVICE
#----------------------------------------------------------------
class KPIService(ServiceBase):
    manager = KpiDefinition.objects
    """
       Service responsible for creating, updating, and retrieving KPI assignments.
       Handles business logic related to assigning KPIs to users, teams, or departments.
       """

    def get_by_uuid(self, kpi_uuid: str):
        return self.manager.get(uuid=kpi_uuid)


    def create_kpi(self, kpi_name, measurement_type, calculation_type, weight_value,
                   kpi_description='', department_uuid=None, min_threshold=None,
                   max_threshold=None, triggered_by: User = None, request=None):

        department = DepartmentService().get_by_uuid(department_uuid) if department_uuid else None



        kpi = self.manager.create(
            kpi_name=kpi_name,
            kpi_description=kpi_description,
            department=department,
            measurement_type=measurement_type,
            calculation_type=calculation_type,
            weight_value=weight_value,
            min_threshold=min_threshold,
            max_threshold=max_threshold,
            created_by=triggered_by,
        )
        return kpi

    def update_kpi(self, kpi_uuid: str, data: dict, triggered_by: User, request=None):
        kpi = self.get_by_uuid(kpi_uuid)

        old_values = {field: str(getattr(kpi, field, None)) for field in data}

        if 'department_uuid' in data:
            kpi.department = DepartmentService().get_by_uuid(data.pop('department_uuid'))

        for field, value in data.items():
            setattr(kpi, field, value)
        kpi.save()
        try:
            TransactionLogService.log(
                event_code='kpi_updated',
                triggered_by=triggered_by,
                entity=kpi,
                status_code='ACT',
                message=f'KPI "{kpi.kpi_name}" updated',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'kpi_uuid': str(kpi.uuid),
                    'kpi_name': kpi.kpi_name,
                    'updated_fields': list(data.keys()),
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")
        return kpi


    def delete_kpi(self, kpi_uuid: str, triggered_by: User, request=None):
        kpi = self.get_by_uuid(kpi_uuid)
        kpi_name = kpi.kpi_name
        kpi_uuid_str = str(kpi.uuid)
        kpi.delete()
        try:
            TransactionLogService.log(
                event_code='kpi_deleted',
                triggered_by=triggered_by,
                entity=None,
                status_code='ACT',
                message=f'KPI "{kpi_name}" deleted',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'kpi_uuid': kpi_uuid_str,
                    'kpi_name': kpi_name,
                    'deleted_by': triggered_by.username if triggered_by else None,
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")
        return kpi


    def get_all_kpis(self, **filters):
        qs = self.manager.all()

        if filters.get("department_uuid"):
            qs = qs.filter(department__uuid=filters["department_uuid"])

        if filters.get("measurement_type"):
            qs = qs.filter(measurement_type=filters["measurement_type"])

        if filters.get("calculation_type"):
            qs = qs.filter(calculation_type=filters["calculation_type"])

        if filters.get("kpi_name"):
            qs = qs.filter(name__icontains=filters["kpi_name"])

        return qs
#_____________________________________________________________
# KPI ASSIGNMENT SERVICE
#-------------------------------------------------------------

class KPIAssignmentService(ServiceBase):
    manager = KpiAssignment.objects
    """
      Service responsible for creating, updating, and retrieving KPI assignments.
      Handles business logic related to assigning KPIs to users, teams, or departments.
      """


    def get_by_uuid(self, assignment_uuid: str):
        return self.manager.get(uuid=assignment_uuid)


    def create_kpi_assignment(self, kpi_uuid, period_start, assigned_to_uuid=None,
                          assigned_team_uuid=None, assigned_department_uuid=None,
                          status=None, triggered_by: User = None, request=None):
        kpi = KPIService().get_by_uuid(kpi_uuid)
        """
        Creates a KPI assignment for a user, team, or department for a given period.
        Fetches the KPI and optional assignees using their UUIDs.
        Only provided assignment targets are attached to the record.
        Stores the assignment with the specified status.
        `triggered_by` and `request` may be used for auditing/logging.
        Returns the created KpiAssignment instance.
        """

        assigned_to         = User.objects.get(uuid=assigned_to_uuid) if assigned_to_uuid else None
        assigned_team       = TeamService().get_by_uuid(assigned_team_uuid) if assigned_team_uuid else None
        assigned_department = DepartmentService().get_by_uuid(assigned_department_uuid) if assigned_department_uuid else None

        assignment = self.manager.create(
            kpi=kpi,
            assigned_to=assigned_to,
            assigned_team=assigned_team,
            assigned_department=assigned_department,
            period_start=period_start,
            status=status,
        )
        try:
            TransactionLogService.log(
                event_code ='kpi_assignment',
                triggered_by=triggered_by,
                entity=assignment,
                status_code ='assigned successfully',
                message = f'KPI "{kpi.kpi_name}" assigned',
                ip_address = request.META.get('REMOTE_ADDR') if request else None,
                metadata ={
                    'assignment_id' : str(assignment.uuid),
                    'kpi_id': str(kpi.uuid),
                    'assigned_to' : assigned_to.role if assigned_to else None,
                    'assigned_team' : assigned_team.team_name if assigned_team else None,
                    'assigned_department' : assigned_department.name if assigned_department else None,
                    'period_start' : str(period_start),
                    'assigned_by': triggered_by.role,


                }

            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")
        return assignment


    def update_assignment(self, assignment_uuid: str, data: dict, triggered_by: User, request=None):
        assignment = self.get_by_uuid(assignment_uuid)
        """
        Update an existing KPI assignment.
        Retrieves the assignment by UUID, applies the provided field updates,
        and saves only the modified fields. Previous values are captured for
        audit purposes and a transaction log is recorded for the update action.
        Args:
            assignment_uuid (str): UUID of the assignment to update.
            data (dict): Fields and values to be updated.
            triggered_by (User): User performing the update.
            request (HttpRequest, optional): Request context for logging/auditing.
        Returns:
            KpiAssignment: The updated assignment instance.
        """

        old_values = {field: str(getattr(assignment, field, None)) for field in data}

        for field, value in data.items():
            setattr(assignment, field, value)
        assignment.save(update_fields=list(data.keys()))
        try:
            TransactionLogService.log(
                event_code='kpi_assignment_updated',
                triggered_by=triggered_by,
                entity=assignment,
                status_code='ACT',
                message=f'Assignment for KPI "{assignment.kpi.kpi_name}" updated',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'assignment_id': str(assignment.uuid),
                    'kpi_name': assignment.kpi.kpi_name,
                    'updated_by': triggered_by.email,
                    'changed_fields': list(data.keys()),
                    'old_values': old_values,
                    'new_values': {k: str(v) for k, v in data.items()},
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")
        return assignment


    def get_all_assignments(self, **filters):
        """
        Retrieve assignments with optional filtering.

        This method returns a queryset of assignments and allows filtering
        based on the provided keyword arguments.

        Supported Filters:
            user_uuid (str):
                Filters assignments assigned to a specific user.
            team_uuid (str):
                Filters assignments assigned to a specific team.
            department_uuid (str):
                Filters assignments assigned to a specific department.
            status (str):
                Filters assignments by their current status.
        Args:
            **filters:
                Arbitrary keyword arguments used to filter assignments.
        Returns:
            QuerySet:
                A Django queryset containing assignments that match
                the provided filters.
        Example:
            service.get_all_assignments(user_uuid="123e4567")
            service.get_all_assignments(team_uuid="team-uuid", status="pending")
        """
        qs = self.manager.all()
        if 'user_uuid' in filters:
            qs = qs.filter(assigned_to__uuid=filters['user_uuid'])
        if 'team_uuid' in filters:
            qs = qs.filter(assigned_team__uuid=filters['team_uuid'])
        if 'department_uuid' in filters:
            qs = qs.filter(assigned_department__uuid=filters['department_uuid'])
        if 'status' in filters:
            qs = qs.filter(status=filters['status'])
        return qs



#____________________________________________________________________________
# TRANSACTION LOG SERVICE
#____________________________________________________________________________

class TransactionLogService(ServiceBase):
    manager = TransactionLog.objects
    """Keeps track of transaction logs."""

    @staticmethod
    def get_all_logs(**filters):
        qs = TransactionLog.objects.select_related('event_type', 'triggered_by', 'status')
        if 'user_uuid' in filters:
            qs = qs.filter(triggered_by__uuid=filters['user_uuid'])
        if 'action' in filters:
            qs = qs.filter(event_type__code=filters['action'])
        if 'object_type' in filters:
            qs = qs.filter(entity_type=filters['object_type'])
        if 'time_from' in filters:
            qs = qs.filter(created_at__gte=filters['time_from'])
        if 'time_to' in filters:
            qs = qs.filter(created_at__lte=filters['time_to'])
        return qs

    @staticmethod
    def get_by_uuid(log_uuid: str):
        return TransactionLog.objects.select_related(
            'event_type', 'triggered_by', 'status'
        ).get(uuid=log_uuid)

    @staticmethod
    def log(
            event_code: str,
            triggered_by: User,
            entity,
            status_code: str = 'ACT',
            message: str = '',
            metadata: dict = None,
            ip_address: str = None
    ) -> TransactionLog:
        event_type,_ = EventTypes.objects.get_or_create(code=event_code, defaults = {'name': event_code.replace('_', ' ').title()})

        status,_= Status.objects.get_or_create(code=status_code, defaults={'name': status_code})
        try:
            entity_uuid = entity.uuid
        except AttributeError:
            entity_uuid = None

        return TransactionLog.objects.create(
            event_type=event_type,
            triggered_by=triggered_by,
            status=status,
            message=message,
            metadata=metadata or {},
            entity_type=entity.__class__.__name__,
            entity_uuid=entity_uuid,
            ip_address=ip_address
        )

    @staticmethod
    def get_logs_for_entity(entity):
        """All logs for a specific entity e.g. a KPI or KPIResult."""
        try:
            entity_uuid = entity.uuid
        except AttributeError:
            return TransactionLog.objects.none()

        return TransactionLog.objects.filter(
            entity_type=entity.__class__.__name__,
            entity_uuid=entity_uuid
        ).select_related('event_type', 'triggered_by', 'status')

    @staticmethod
    def get_logs_by_event(event_code: str):
        """All logs for a specific event code e.g. 'kpi_created'."""
        return TransactionLog.objects.filter(
            event_type__code=event_code
        ).select_related('event_type', 'triggered_by', 'status')

    @staticmethod
    def get_user_logs(user: User):
        """Everything a specific user has triggered."""
        return TransactionLog.objects.filter(
            triggered_by=user
        ).select_related('event_type','triggered_by','status')



from simpleeval import simple_eval


class KPIResultAccountService(ServiceBase):
    manager = KPIResults.objects
    """ Service layer responsible for all business logic related to KPI Results.
            This service handles the full lifecycle of a KPI result — from submission
            and score calculation to updating, retrieving, and exporting results.
            It acts as the bridge between the views/handlers and the database,
            ensuring that all results are scored automatically using the active
            formula linked to each KPI."""

    def get_by_uuid(self, result_uuid: str):
        return self.manager.get(uuid=result_uuid)

    def get_all_results(self, **filters):
        qs = self.manager.all()
        if 'user_uuid' in filters:
            qs = qs.filter(kpi_assignment__assigned_to__uuid=filters['user_uuid'])
        if 'team_uuid' in filters:
            qs = qs.filter(kpi_assignment__assigned_team__uuid=filters['team_uuid'])
        if 'department_uuid' in filters:
            qs = qs.filter(kpi_assignment__assigned_department__uuid=filters['department_uuid'])
        if 'period_start' in filters:
            qs = qs.filter(recorded_at__gte=filters['period_start'])
        if 'period_end' in filters:
            qs = qs.filter(recorded_at__lte=filters['period_end'])
        return qs

    @staticmethod
    def _get_active_formula(kpi):
        """Fetch the active formula linked to this KPI."""
        return kpi.formula.filter(status__name='active').first()

    @staticmethod
    def _calculate_score(actual_value, kpi, formula=None):
        """
        Dynamically evaluate the formula expression linked to the KPI.
        Falls back to default formula if none is found.
        """
        try:
            actual = float(actual_value)
            target = float(kpi.max_threshold) if kpi.max_threshold else 1
            weight = float(kpi.weight_value) if kpi.weight_value else 1.0

            if formula and formula.formula_expression:
                context = {
                    'actual':        actual,
                    'target':        target,
                    'weight':        weight,
                    'min_threshold': float(kpi.min_threshold) if kpi.min_threshold else 0,
                    'max_threshold': float(kpi.max_threshold) if kpi.max_threshold else 1,
                }
                score = simple_eval(formula.formula_expression, names=context)
            else:
                # fallback if no active formula found
                max_t = target or actual or 1
                score = (actual / max_t) * 100 * weight

            # clamp score between 0 and 300 — prevents negatives on over-budget KPIs
            score = max(0.0, min(float(score), 300.0))
            return round(float(score), 4)

        except Exception as e:
            print(f"[Formula Calculation ERROR] {e}")
            return None

    @staticmethod
    def _derive_comment(score, formula=None):
        """
        Derive rating label from score using formula thresholds if available,
        otherwise fall back to default thresholds.
        """
        if score is None:
            return ''

        score        = float(score)
        outstanding  = float(formula.outstanding_threshold) if formula and formula.outstanding_threshold else 90
        good         = float(formula.good_threshold) if formula and formula.good_threshold else 75
        satisfactory = float(formula.satisfactory_threshold) if formula and formula.satisfactory_threshold else 60
        needs_imp    = float(formula.needs_improvement_threshold) if formula and formula.needs_improvement_threshold else 40

        if score >= outstanding:  return 'outstanding'
        if score >= good:         return 'good'
        if score >= satisfactory: return 'satisfactory'
        if score >= needs_imp:    return 'needs_improvement'
        return 'poor'

    @staticmethod
    def _build_result_response(result):
        """Build a clean response dict to return to the user after submission."""
        return {
            'result_uuid':       str(result.uuid),
            'kpi_name':          result.kpi_assignment.kpi.kpi_name,
            'actual_value':      str(result.actual_value),
            'calculated_score':  str(result.calculated_score),
            'rating':            result.rating,
            'recorded_by':       result.recorded_by.email,
        }

    def create_result(self, assignment_uuid: str, actual_value,
                      triggered_by: User, request=None):

        assignment = KPIAssignmentService().get_by_uuid(assignment_uuid)

        # ── 0. Prevent duplicate submissions on the same assignment ──────────
        existing = self.manager.filter(
            kpi_assignment = assignment,
            submitted_by   = triggered_by,
        ).first()
        if existing:
            raise ValueError(
                f'You have already submitted a result for this KPI. '
                f'Use the update endpoint to change your submission.'
            )

        # ── 1. Validate the submitter belongs to the assignment target ────────
        if assignment.assigned_to:
            # Individual assignment — only that specific user can submit
            if triggered_by != assignment.assigned_to:
                raise PermissionError('This KPI is not assigned to you')
            submitted_by = assignment.assigned_to

        elif assignment.assigned_team:
            # Team assignment — submitter must be a member of that team
            if triggered_by.team != assignment.assigned_team:
                raise PermissionError('You are not a member of the assigned team')
            submitted_by = triggered_by

        elif assignment.assigned_department:
            # Department assignment — submitter must be in that department
            if triggered_by.department != assignment.assigned_department:
                raise PermissionError('You are not a member of the assigned department')
            submitted_by = triggered_by

        else:
            raise ValueError('KPI assignment has no valid target')
        # ─────────────────────────────────────────────────────────────────────

        kpi = assignment.kpi
        formula = self._get_active_formula(kpi)
        calculated_score = self._calculate_score(actual_value, kpi, formula)
        rating = self._derive_comment(calculated_score, formula)

        result = self.manager.create(
            kpi_assignment=assignment,
            actual_value=actual_value,
            calculated_score=calculated_score,
            rating=rating,
            recorded_by=triggered_by,
            submitted_by=submitted_by,  # ← tracks who submitted
        )

        #  Trigger alert check
        try:
            from performance.alert_service import AlertService
            AlertService.check_and_create_alert(result)
        except Exception as e:
            print(f'[AlertService ERROR] {e}')
        #

        # ── 3. Log the transaction ────────────────────────────────────────────
        try:
            TransactionLogService.log(
                event_code='kpi_result_submitted',
                triggered_by=triggered_by,
                entity=result,
                status_code='ACT',
                message=f'Result submitted for KPI "{kpi.kpi_name}"',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'result_id': str(result.uuid),
                    'kpi_name': kpi.kpi_name,
                    'assignment_id': str(assignment.uuid),
                    'actual_value': str(actual_value),
                    'calculated_score': str(calculated_score),
                    'rating': rating,
                    'submitted_by': submitted_by.username,
                    'formula_used': formula.formula_name if formula else 'default',
                }
            )
        except Exception as e:
            print(f'[TransactionLog ERROR] {e}')
        # ─────────────────────────────────────────────────────────────────────

        return result



    def update_result(self, result_uuid: str, data: dict, triggered_by: User, request=None):
        result = self.get_by_uuid(result_uuid)
        kpi    = result.kpi_assignment.kpi

        old_values = {'actual_value': str(result.actual_value)}

        if 'actual_value' in data:
            formula                 = self._get_active_formula(kpi)
            result.actual_value     = data['actual_value']
            result.calculated_score = self._calculate_score(data['actual_value'], kpi, formula)
            result.comment          = self._derive_comment(result.calculated_score, formula)

        result.save(update_fields=['actual_value', 'calculated_score', 'comment'])

        try:
            TransactionLogService.log(
                event_code='kpi_result_updated',
                triggered_by=triggered_by,
                entity=result,
                status_code='ACT',
                message=f'Result updated for KPI "{kpi.kpi_name}"',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'result_id':  str(result.uuid),
                    'kpi_name':   kpi.kpi_name,
                    'updated_by': triggered_by.email,
                    'old_values': old_values,
                    'new_values': {
                        'actual_value':     str(result.actual_value),
                        'calculated_score': str(result.calculated_score),
                        'comment':          result.comment,
                    },
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return self._build_result_response(result)

    def export_csv(self, **filters):
        import csv, io
        from django.http import HttpResponse

        qs = self.get_all_results(**filters).select_related(
            'kpi_assignment__kpi',
            'kpi_assignment__assigned_to',
            'recorded_by',
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'uuid', 'kpi_name', 'assigned_to', 'actual_value',
            'calculated_score', 'rating', 'comment', 'recorded_at', 'recorded_by',
        ])
        for r in qs:
            writer.writerow([
                str(r.uuid),
                r.kpi_assignment.kpi.kpi_name,
                r.kpi_assignment.assigned_to.email if r.kpi_assignment.assigned_to else '',
                r.actual_value,
                r.calculated_score,
                r.rating,
                r.comment,
                r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else '',
                r.recorded_by.email if r.recorded_by else '',
            ])

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=kpi_results.csv'
        return response

class KPIFormulaService(ServiceBase):
    manager = KPIFormula.objects
    """
    Service layer responsible for managing KPI formula operations.
    Handles retrieval, creation, and updating of KPIFormula records.
    Also logs all create and update operations via TransactionLogService
    for audit and traceability purposes.
    """


    def get_by_uuid(self, formula_uuid: str):
        """Retrieves a KPI formula by its UUID."""
        return self.manager.get(uuid=formula_uuid)

    def get_by_kpi_uuid(self, kpi_uuid: str):
        """
             Retrieve a KPI formula associated with a specific KPI UUID."""
        return self.manager.filter(kpi__uuid=kpi_uuid).first()

    def create_formula(self, kpi_uuid, formula_expression, data_source='',
                       triggered_by: User = None, request=None):
        kpi = KPIService().get_by_uuid(kpi_uuid)

        formula = self.manager.create(
            kpi=kpi,
            formula_expression=formula_expression,
            data_source=data_source,
        )

        try:
            TransactionLogService.log(
                event_code='kpi_formula_created',
                triggered_by=triggered_by,
                entity=formula,
                status_code='ACT',
                message=f'Formula created for KPI "{kpi.kpi_name}"',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'formula_id': str(formula.uuid),
                    'kpi_id': str(kpi.uuid),
                    'kpi_name': kpi.kpi_name,
                    'data_source': data_source,
                    'created_by': triggered_by.email,
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return formula

    def update_formula(self, formula_uuid: str, data: dict, triggered_by: User, request=None):
        """
                Update an existing KPI formula.
                This method:
                - Retrieves the formula by UUID
                - Updates allowed fields dynamically
                - Tracks old and new values for auditing
                - Logs the update operation in the transaction log system"""

        formula = self.get_by_uuid(formula_uuid)

        old_values = {field: str(getattr(formula, field, None)) for field in data}

        for field, value in data.items():
            setattr(formula, field, value)
        formula.save(update_fields=list(data.keys()))

        try:
            TransactionLogService.log(
                event_code='kpi_formula_updated',
                triggered_by=triggered_by,
                entity=formula,
                status_code='ACT',
                message=f'Formula updated for KPI "{formula.kpi.kpi_name}"',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'formula_id': str(formula.uuid),
                    'kpi_name': formula.kpi.kpi_name,
                    'updated_by': triggered_by.email,
                    'changed_fields': list(data.keys()),
                    'old_values': old_values,
                    'new_values': {k: str(v) for k, v in data.items()},
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return formula

    def delete_formula(self, formula_uuid: str, triggered_by: User, request=None):
        """
        Delete an existing KPI formula.
        This method:
        - Retrieves the formula by UUID
        - Stores the formula name before deletion
        - Deletes the formula from the database
        """
        formula = self.get_by_uuid(formula_uuid)
        formula_uuid_str = str(formula.uuid)
        kpi_name = formula.kpi.kpi_name
        formula.delete()
        try:
            TransactionLogService.log(
                event_code='kpi_formula_deleted',
                triggered_by=triggered_by,
                entity=None,
                status_code='ACT',
                message=f'Formula for KPI "{kpi_name}" deleted',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'formula_uuid': formula_uuid_str,
                    'kpi_name': kpi_name,
                    'deleted_by': triggered_by.username if triggered_by else None,
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")
        return formula


class UserService(ServiceBase):

    @property
    def manager(self):
        User = get_user_model()
        return User.objects

    def register_user(self, username, email, password, role_name=None):
        if self.filter(email=email).exists():
            raise ValueError("Email already exists")
        role = Role.objects.filter(name=role_name or "Employee").first()
        if not role:
            raise ValueError("Role not found")
        user = self.create(
            username=username,
            email=email,
            password=make_password(password),
            role=role,
            is_active=True
        )
        try:
            TransactionLogService.log(
                event_code='user_registered',
                triggered_by=user,
                entity=user,
                status_code='ACT',
                message=f'User "{user.username}" registered',
                ip_address=None,
                metadata={'user_uuid': str(user.uuid), 'username': user.username, 'email': user.email}
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")
        return user




    @staticmethod
    def delete_user(uuid):
        """
        Delete a user  by username and returns response provider if
        user doesn't exist, returns success if user is deleted successfully.
        """
        try:
            user = User.objects.get(username=uuid)
        except User.DoesNotExist:
            return ResponseProvider.not_found(error=f"User '{uuid}' not found")

        username = user.username
        user_uuid = str(user.uuid)
        user.delete()
        try:
            TransactionLogService.log(
                event_code='user_deleted',
                triggered_by=None,
                entity=None,
                status_code='ACT',
                message=f'User "{username}" deleted',
                ip_address=None,
                metadata={'user_uuid': user_uuid, 'username': username}
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")
        return ResponseProvider.success(message=f"User '{uuid}' deleted successfully")

    def authenticate_user(self, email, password):
        user = self.filter(email=email).first()
        if not user or not check_password(password, user.password):
            raise ValueError("Invalid credentials")
        if not user.is_active:
            raise ValueError("Account inactive")
        return user

    @staticmethod
    def change_password( user, old_password, new_password):
        if not check_password(old_password, user.password):
            raise ValueError("Old password incorrect")
        user.password = make_password(new_password)
        user.save()
        return True

    @staticmethod

    def assign_role( user, role_name):
        role = Role.objects.filter(name=role_name).first()
        if not role:
            raise ValueError("Role not found")
        user.role = role
        user.save()
        return user

    @staticmethod
    @service_handler(require_auth=True, allowed_roles=["admin"])
    def list_users(request):
        users = list(User.objects.select_related("role")
                     .values("uuid", "username", "email", "role__name"))
        return ResponseProvider.success("Users retrieved successfully", users)

    @staticmethod
    @service_handler(require_auth=True, allowed_roles=["admin"])
    def update_user(request, uuid):
        data = json.loads(request.body or "{}")

        if "password" in data:
            data["password"] = make_password(data["password"])

        if "role" in data:
            role = Role.objects.filter(name=data["role"]).first()
            if not role:
                return ResponseProvider.bad_request("Role not found")
            data["role"] = role

        try:
            user = UserService().update(uuid, **data)
        except ValueError as e:
            return ResponseProvider.bad_request(str(e))

        return ResponseProvider.success("User updated", {"uuid": str(user.uuid)})



    @staticmethod
    def reset_password(username, old_password, new_password, confirm_password):
        if not username or not old_password or not new_password or not confirm_password:
            raise ValueError("All fields are required")

        if new_password != confirm_password:
            raise ValueError("Passwords do not match")

        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise LookupError("User not found")

        if not user.check_password(old_password):
            raise PermissionError("Old password is incorrect")

        if old_password == new_password:
            raise ValueError("New password cannot be the same as old password")

        user.set_password(new_password)
        user.save()
        try:
            TransactionLogService.log(
                event_code='password_reset',
                triggered_by=user,
                entity=user,
                status_code='ACT',
                message=f'Password reset for user "{user.username}"',
                ip_address=None,
                metadata={'user_uuid': str(user.uuid), 'username': user.username}
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")
        return user

    # ─────────────────────────────────────────────────────────────────────────────
    # services/services.py  — paste this class just before class RoleService
    # ─────────────────────────────────────────────────────────────────────────────

class OTPService:
    """
    Handles OTP generation, email sending, and verification.
    Used for password reset and first-login flows.
    Flow:
        1. create_otp(username, purpose)
               → invalidates old OTPs, generates 6-digit code,
                 saves to DB with 10-min expiry, emails the code.
        2. verify_otp(username, code, purpose)
               → validates the code, marks it used, returns the user.
    """

    OTP_EXPIRY_MINUTES = 10

    @staticmethod
    def generate_otp():
        """Generate a cryptographically secure 6-digit OTP."""
        import random
        return str(random.SystemRandom().randint(100000, 999999))

    @classmethod
    def create_otp(cls, username: str, purpose: str):
        """
        Invalidate any existing unused OTPs for this user + purpose,
        then create a fresh one and send it via email.
        """
        from django.utils import timezone
        from datetime import timedelta
        from accounts.models import OTP

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise LookupError(f"User '{username}' not found")

        # Invalidate all previous unused OTPs for the same purpose
        OTP.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False,
        ).update(is_used=True)

        code = cls.generate_otp()
        otp = OTP.objects.create(
            user=user,
            code=code,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=cls.OTP_EXPIRY_MINUTES),
        )

        cls._send_otp_email(user, code, purpose)
        return otp

    @classmethod
    def verify_otp(cls, username: str, code: str, purpose: str):
        """
        Verify the OTP code for a given user and purpose.
        Marks it as used on success.
        Raises ValueError  → wrong code or already used.
        Raises ValueError  → code has expired.
        Raises LookupError → user not found.
        """
        from accounts.models import OTP

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise LookupError(f"User '{username}' not found")

        otp = OTP.objects.filter(
            user=user,
            code=code,
            purpose=purpose,
            is_used=False,
        ).order_by('-created_at').first()

        if not otp:
            raise ValueError("Invalid OTP code")

        if not otp.is_valid():
            raise ValueError("OTP has expired. Please request a new one")

        otp.is_used = True
        otp.save(update_fields=['is_used'])
        return user

    @staticmethod
    def _send_otp_email(user, code, purpose):
        """Send OTP code to the user's registered email address."""
        from django.core.mail import send_mail
        from django.conf import settings

        labels = {
            'password_reset': 'Password Reset',
            'first_login': 'Account Activation',
        }
        label = labels.get(purpose, 'Verification')

        subject = f'Your {label} OTP — Internal KPI System'
        message = (
            f'Dear {user.username},\n\n'
            f'Your one-time password (OTP) for {label} is:\n\n'
            f'        {code}\n\n'
            f'This code is valid for 10 minutes.\n'
            f'Do not share this code with anyone.\n\n'
            f'If you did not request this, please contact your administrator immediately.\n\n'
            f'Internal KPI System'
        )
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'[OTP Email ERROR] Could not send OTP to {user.email}: {e}')

class RoleService(ServiceBase):
    manager = Role.objects

    @staticmethod
    def update_user_role(request, username, new_role):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return ResponseProvider.not_found(error="User not found")

        try:
            role_obj = Role.objects.get(name=new_role)
        except Role.DoesNotExist:
            return ResponseProvider.not_found(error=f"Role '{new_role}' not found")

        old_role = user.role.name if user.role else None
        user.role = role_obj
        user.save(update_fields=["role"])
        try:
            TransactionLogService.log(
                event_code='user_role_updated',
                triggered_by=None,
                entity=user,
                status_code='ACT',
                message=f'Role updated for "{user.username}": {old_role} -> {new_role}',
                ip_address=None,
                metadata={'user_uuid': str(user.uuid), 'username': user.username, 'old_role': old_role, 'new_role': new_role}
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")
        return ResponseProvider.success(
            message="User role updated successfully",
            data={
                "username": user.username,
                "email": user.email,
                "role": user.role.name,
            }
        )

    def delete_role_by_name(self, name: str) -> None:
        """
        Delete a role using its name.
        Args:
            name (str): Name of the role.
        Raises:
            LookupError: If the role does not exist.
        """
        try:
            role = self.manager.get(name=name)
        except self.manager.model.DoesNotExist:
            raise LookupError(f"Role '{name}' not found")
        role.delete()

    def get_all_roles(self):
        """
        Retrieve all roles.
        Returns:
            list[Role]: List of Role objects.
        """
        return list(self.manager.all())

class AuthService:
    manager = RefreshToken.objects
    """
    Service responsible for authentication related actions.
    """

    @staticmethod
    def logout(refresh_token: str) -> None:
        """
        Invalidate a refresh token.

        Args:
            refresh_token (str): The refresh token sent by the client.

        Raises:
            LookupError: If the token does not exist.
        """
        token = RefreshToken.objects.filter(token=refresh_token).first()

        if not token:
            raise LookupError("Token not found")

        token.delete()


#--------------------------------------------------------------------------
#  PERFORMANCE SUMMARY
#--------------------------------------------------------------------------
import csv
import io

from django.db.models import Sum, QuerySet
from django.http import HttpResponse
from django.contrib.auth import get_user_model



from performance.models import PerformanceSummary

class PerformanceSummaryAccountService(ServiceBase):
    """
    Data access layer for PerformanceSummary.
    Handles all DB queries, summary generation, and exports.
    Sends email notifications after every summary is generated.
    """

    manager = PerformanceSummary.objects

    def get_by_uuid(self, summary_uuid: str) -> PerformanceSummary:
        """Fetch a single PerformanceSummary by its UUID."""
        return self.manager.select_related(
            'user', 'department', 'team'
        ).get(uuid=summary_uuid)

    def get_all_summaries(self, **filters) -> QuerySet:
        """
        Return a filtered queryset of summaries.
        Supported filters: user_uuid, team_uuid, department_uuid,
        department_name, period_start, period_end, summary_type.
        """
        qs = self.manager.select_related('user', 'department', 'team').all()

        if 'user_uuid'       in filters:
            qs = qs.filter(user__uuid=filters['user_uuid'])
        if 'team_uuid'       in filters:
            qs = qs.filter(team__uuid=filters['team_uuid'])
        if 'department_uuid' in filters:
            qs = qs.filter(department__uuid=filters['department_uuid'])
        if 'department_name' in filters:
            qs = qs.filter(department__name__iexact=filters['department_name'])
        if 'period_start'    in filters:
            qs = qs.filter(period_start__gte=filters['period_start'])
        if 'period_end'      in filters:
            qs = qs.filter(period_end__lte=filters['period_end'])
        if 'summary_type'    in filters:
            qs = qs.filter(summary_type=filters['summary_type'])

        return qs

    # ── INDIVIDUAL ────────────────────────────────────────────────────────────

    def generate_individual_summary(self, user_uuid, period_start, period_end,
                                    triggered_by=None, request=None):
        """
        Aggregate KPI scores from results where the KPI was
        assigned directly to this individual user.
        Notifies the employee and HR after generation.
        """
        user = User.objects.select_related(
            'department', 'team'
        ).get(uuid=user_uuid)

        results = KPIResults.objects.filter(
            submitted_by                = user,
            kpi_assignment__assigned_to = user,
            created_at__gte             = period_start,
            created_at__lte             = period_end,
            calculated_score__isnull    = False,
        ).select_related('kpi_assignment__kpi')

        total_weighted = sum(
            float(r.calculated_score) * float(r.kpi_assignment.kpi.weight_value or 1)
            for r in results
        )
        total_weights = sum(
            float(r.kpi_assignment.kpi.weight_value or 1)
            for r in results
        )
        weighted_score = round(total_weighted / total_weights, 4) if total_weights else 0.0

        summary, _ = self.manager.update_or_create(
            user         = user,
            period_start = period_start,
            period_end   = period_end,
            defaults     = {
                'summary_type':   PerformanceSummary.SummaryType.INDIVIDUAL,
                'department':     user.department,
                'team':           user.team,
                'weighted_score': weighted_score,
            }
        )

        self._log(summary, triggered_by, request)
        self._notify_individual(summary, user)
        return summary

    # ── TEAM ──────────────────────────────────────────────────────────────────

    def generate_team_summary(self, team_uuid, period_start, period_end,
                              triggered_by=None, request=None):
        """
        Aggregate KPI scores from results where the KPI was
        assigned to this team.
        Notifies all team members, the line manager, and HR.
        """
        from organization.models import Team
        team = Team.objects.select_related('department').get(uuid=team_uuid)

        results = KPIResults.objects.filter(
            kpi_assignment__assigned_team = team,
            created_at__gte               = period_start,
            created_at__lte               = period_end,
            calculated_score__isnull      = False,
        ).select_related('kpi_assignment__kpi')

        total_weighted = sum(
            float(r.calculated_score) * float(r.kpi_assignment.kpi.weight_value or 1)
            for r in results
        )
        total_weights = sum(
            float(r.kpi_assignment.kpi.weight_value or 1)
            for r in results
        )
        weighted_score = round(total_weighted / total_weights, 4) if total_weights else 0.0

        summary, _ = self.manager.update_or_create(
            team         = team,
            period_start = period_start,
            period_end   = period_end,
            defaults     = {
                'summary_type':   PerformanceSummary.SummaryType.TEAM,
                'department':     team.department,
                'weighted_score': weighted_score,
            }
        )

        self._log(summary, triggered_by, request)
        self._notify_team(summary, team)
        return summary

    # ── DEPARTMENT ────────────────────────────────────────────────────────────

    def generate_department_summary(self, department_uuid, period_start, period_end,
                                    triggered_by=None, request=None):
        """
        Aggregate KPI scores from results where the KPI was
        assigned to this department.
        Notifies the department line manager and HR.
        """
        from organization.models import Department
        department = Department.objects.get(uuid=department_uuid)

        results = KPIResults.objects.filter(
            kpi_assignment__assigned_department = department,
            created_at__gte                     = period_start,
            created_at__lte                     = period_end,
            calculated_score__isnull            = False,
        ).select_related('kpi_assignment__kpi')

        total_weighted = sum(
            float(r.calculated_score) * float(r.kpi_assignment.kpi.weight_value or 1)
            for r in results
        )
        total_weights = sum(
            float(r.kpi_assignment.kpi.weight_value or 1)
            for r in results
        )
        weighted_score = round(total_weighted / total_weights, 4) if total_weights else 0.0

        summary, _ = self.manager.update_or_create(
            department   = department,
            period_start = period_start,
            period_end   = period_end,
            defaults     = {
                'summary_type':   PerformanceSummary.SummaryType.DEPARTMENT,
                'weighted_score': weighted_score,
            }
        )

        self._log(summary, triggered_by, request)
        self._notify_department(summary, department)
        return summary

    # ── NOTIFICATION HELPERS ──────────────────────────────────────────────────

    def _notify_individual(self, summary, user):
        """
        After individual summary is generated:
        notify the employee and HR.
        """
        from performance.email_service import EmailNotificationService
        from performance.models import Notification

        # ── always save notification first ────────────────────────────────
        try:
            Notification.objects.create(
                recipient         = user,
                summary           = summary,
                notification_type = Notification.NotificationType.SUMMARY,
                message           = (
                    f'Your performance summary for '
                    f'{summary.period_start} to {summary.period_end} '
                    f'is ready. Score: {summary.weighted_score}'
                ),
                is_read = False,
            )
        except Exception as e:
            print(f'[Notification ERROR] could not save notification for {user.username}: {e}')

        # ── email separately so a failure does not block the notification ──
        try:
            EmailNotificationService.send_individual_summary_email(user, summary)
        except Exception as e:
            print(f'[Email ERROR] summary email to {user.email}: {e}')

        # ── HR notification ────────────────────────────────────────────────
        try:
            self._create_hr_notifications(summary)
        except Exception as e:
            print(f'[HR Notification ERROR] {e}')
        try:
            EmailNotificationService.send_summary_to_hr(summary)
        except Exception as e:
            print(f'[Email ERROR] HR summary email: {e}')

    def _notify_team(self, summary, team):
        """
        After team summary is generated:
        notify all team members, the line manager, and HR.
        """
        from performance.email_service import EmailNotificationService
        from performance.models import Notification

        team_members = User.objects.filter(team=team).select_related('role')

        # ── notify each team member ────────────────────────────────────────
        for member in team_members:
            try:
                Notification.objects.create(
                    recipient         = member,
                    summary           = summary,
                    notification_type = Notification.NotificationType.SUMMARY,
                    message           = (
                        f'Your team {team.team_name} performance summary for '
                        f'{summary.period_start} to {summary.period_end} '
                        f'is ready. Score: {summary.weighted_score}'
                    ),
                    is_read = False,
                )
            except Exception as e:
                print(f'[Notification ERROR] team member {member.username}: {e}')
            try:
                EmailNotificationService.send_team_summary_email([member], summary)
            except Exception as e:
                print(f'[Email ERROR] team summary to {member.email}: {e}')

        # ── notify line managers ───────────────────────────────────────────
        managers = User.objects.filter(
            department     = team.department,
            role__name__in = ['Business_Line_Manager', 'Tech_Line_Manager']
        )
        for manager in managers:
            try:
                Notification.objects.create(
                    recipient         = manager,
                    summary           = summary,
                    notification_type = Notification.NotificationType.SUMMARY,
                    message           = (
                        f'Team {team.team_name} performance summary for '
                        f'{summary.period_start} to {summary.period_end} '
                        f'is ready. Score: {summary.weighted_score}'
                    ),
                    is_read = False,
                )
            except Exception as e:
                print(f'[Notification ERROR] manager {manager.username}: {e}')
            try:
                EmailNotificationService.send_manager_summary_email(manager, summary)
            except Exception as e:
                print(f'[Email ERROR] manager summary to {manager.email}: {e}')

        # ── HR ─────────────────────────────────────────────────────────────
        try:
            self._create_hr_notifications(summary)
        except Exception as e:
            print(f'[HR Notification ERROR] {e}')
        try:
            EmailNotificationService.send_summary_to_hr(summary)
        except Exception as e:
            print(f'[Email ERROR] HR team summary: {e}')

    def _notify_department(self, summary, department):
        """
        After department summary is generated:
        notify the department line manager and HR.
        """
        from performance.email_service import EmailNotificationService
        from performance.models import Notification

        managers = User.objects.filter(
            department     = department,
            role__name__in = ['Business_Line_Manager', 'Tech_Line_Manager']
        )

        # ── notify line managers ───────────────────────────────────────────
        for manager in managers:
            try:
                Notification.objects.create(
                    recipient         = manager,
                    summary           = summary,
                    notification_type = Notification.NotificationType.SUMMARY,
                    message           = (
                        f'{department.name} department performance summary for '
                        f'{summary.period_start} to {summary.period_end} '
                        f'is ready. Score: {summary.weighted_score}'
                    ),
                    is_read = False,
                )
            except Exception as e:
                print(f'[Notification ERROR] dept manager {manager.username}: {e}')
            try:
                EmailNotificationService.send_manager_summary_email(manager, summary)
            except Exception as e:
                print(f'[Email ERROR] dept manager summary to {manager.email}: {e}')

        # ── HR ─────────────────────────────────────────────────────────────
        try:
            self._create_hr_notifications(summary)
        except Exception as e:
            print(f'[HR Notification ERROR] {e}')
        try:
            EmailNotificationService.send_summary_to_hr(summary)
        except Exception as e:
            print(f'[Email ERROR] HR dept summary: {e}')

    def _create_hr_notifications(self, summary):
        """
        Create in-app notifications for all HR users
        whenever any type of summary is generated.
        """
        from performance.models import Notification

        hr_users = User.objects.filter(role__name__iexact='hr')
        for hr_user in hr_users:
            Notification.objects.create(
                recipient         = hr_user,
                summary           = summary,
                notification_type = Notification.NotificationType.SUMMARY,
                message           = (
                    f'New {summary.summary_type} performance summary generated. '
                    f'Score: {summary.weighted_score}'
                ),
                is_read = False,
            )

    # ── LOGGING ───────────────────────────────────────────────────────────────

    def _log(self, summary, triggered_by, request):
        """Log every summary generation to the transaction log."""
        try:
            TransactionLogService.log(
                event_code   = 'performance_summary_generated',
                triggered_by = triggered_by,
                entity       = summary,
                status_code  = 'ACT',
                message      = f'{summary.summary_type.title()} summary generated',
                ip_address   = request.META.get('REMOTE_ADDR') if request else None,
                metadata     = {
                    'summary_uuid':   str(summary.uuid),
                    'summary_type':   summary.summary_type,
                    'weighted_score': str(summary.weighted_score),
                    'generated_by':   triggered_by.email if triggered_by else None,
                }
            )
        except Exception as e:
            print(f'[TransactionLog ERROR] {e}')

    # ── CSV EXPORT ────────────────────────────────────────────────────────────

    def export_csv(self, **filters) -> HttpResponse:
        """Export filtered summaries as a downloadable CSV file."""
        qs = self.get_all_summaries(**filters)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'uuid', 'summary_type', 'subject', 'department',
            'team', 'period_start', 'period_end',
            'weighted_score', 'generated_at',
        ])

        for s in qs:
            if s.summary_type == 'individual':
                subject = s.user.username if s.user else ''
            elif s.summary_type == 'team':
                subject = s.team.team_name if s.team else ''
            else:
                subject = s.department.name if s.department else ''

            writer.writerow([
                str(s.uuid),
                s.summary_type,
                subject,
                s.department.name if s.department else '',
                s.team.team_name if s.team else '',
                s.period_start,
                s.period_end,
                s.weighted_score,
                s.created_at,
            ])

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=performance_summaries.csv'
        return response







