from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.models import Role, RefreshToken
from kpis.models import KpiDefinition, KpiAssignment, KPIResults, KPIFormula
from Transaction.models import TransactionLog, EventTypes
from services.serviceBase import ServiceBase, service_handler
from services.utils.response_provider import ResponseProvider
import json
from django.db import models
from performance.models import Notification
from performance.email_service import EmailNotificationService
from organization.models import Department, Team
from Base.models import Status



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


    def create_kpi(self, kpi_name, measurement_type, weight_value,
                   kpi_description='', department_uuid=None, min_threshold=None,
                   max_threshold=None,frequency ='monthly', triggered_by: User = None, request=None):

        department = DepartmentService().get_by_uuid(department_uuid) if department_uuid else None



        kpi = self.manager.create(
            kpi_name=kpi_name,
            kpi_description=kpi_description,
            department=department,
            frequency=frequency,
            measurement_type=measurement_type,
            calculation_type= None,
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
        if filters.get('department_uuid'):
            qs = qs.filter(department__uuid=filters['department_uuid'])
        if filters.get('measurement_type'):
            qs = qs.filter(measurement_type=filters['measurement_type'])
        if filters.get('calculation_type'):
            qs = qs.filter(calculation_type=filters['calculation_type'])
        if filters.get('kpi_name'):
            qs = qs.filter(kpi_name__icontains=filters['kpi_name'])
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

    def create_kpi_assignment(self, kpi_uuid, period_start, period_end, assigned_to_uuid=None,
                              assigned_team_uuid=None, assigned_department_uuid=None,
                              status=None, triggered_by: User = None, request=None):
        """
           Creates a KPI assignment for a user, team, or department.
           Validates input before hitting the database, checks for duplicates,
           ensures an active formula exists, then creates the assignment and
           notifies all recipients in-app and by email.
           """

        kpi = KPIService().get_by_uuid(kpi_uuid)
        assigned_to = User.objects.get(uuid=assigned_to_uuid) if assigned_to_uuid else None
        assigned_team = TeamService().get_by_uuid(assigned_team_uuid) if assigned_team_uuid else None
        assigned_department = DepartmentService().get_by_uuid(
            assigned_department_uuid) if assigned_department_uuid else None
        # Validate only one assignment target
        targets_provided = sum([
            bool(assigned_to),
            bool(assigned_team),
            bool(assigned_department),
        ])
        if targets_provided == 0:
            raise ValueError('Please assign to a user, team or department.')
        if targets_provided > 1:
            raise ValueError('A KPI can only be assigned to one target — user, team or department.')

        #  Resolve status FK
        status_obj = None
        if status:
            status_obj = Status.objects.filter(name__iexact=status).first()

            #  Validation — period dates
            from datetime import date as date_type
            start = period_start if isinstance(period_start, date_type) else date_type.fromisoformat(str(period_start))

            if start < date_type.today():
                raise ValueError('Assignment period start cannot be in the past.')

            if period_end:
                end = period_end if isinstance(period_end, date_type) else date_type.fromisoformat(str(period_end))
                if end <= start:
                    raise ValueError('Period end must be after period start.')

        #  Validation duplicate assignment check
        if assigned_to and self.manager.filter(
                kpi=kpi, assigned_to=assigned_to,
                period_start=period_start, period_end=period_end
        ).exists():
            raise ValueError(f'This KPI is already assigned to {assigned_to.username} for this period.')

        if assigned_team and self.manager.filter(
                kpi=kpi, assigned_team=assigned_team,
                period_start=period_start, period_end=period_end
        ).exists():
            raise ValueError(f'This KPI is already assigned to {assigned_team.team_name} team for this period.')

        if assigned_department and self.manager.filter(
                kpi=kpi, assigned_department=assigned_department,
                period_start=period_start, period_end=period_end
        ).exists():
            raise ValueError(f'This KPI is already assigned to {assigned_department.name} department for this period.')

        # Validation, KPI must have an active formula before assignment

        if not KPIFormula.objects.filter(kpi=kpi, status__code='ACT').exists():
            raise ValueError(
                f'KPI "{kpi.kpi_name}" has no active formula. '
                'Please create a formula before assigning this KPI.'
            )

        #  Create assignment
        assignment = self.manager.create(
            kpi=kpi,
            assigned_to=assigned_to,
            assigned_team=assigned_team,
            assigned_department=assigned_department,
            period_start=period_start,
            period_end=period_end,
            status=status_obj,
        )

        #  Log transaction
        try:
            TransactionLogService.log(
                event_code='kpi_assignment',
                triggered_by=triggered_by,
                entity=assignment,
                status_code='ACT',
                message=f'KPI "{kpi.kpi_name}" assigned',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'assignment_id': str(assignment.uuid),
                    'kpi_id': str(kpi.uuid),
                    'assigned_to': assigned_to.username if assigned_to else None,
                    'assigned_team': assigned_team.team_name if assigned_team else None,
                    'assigned_department': assigned_department.name if assigned_department else None,
                    'period_start': str(period_start),
                    'assigned_by': triggered_by.username if triggered_by else None,
                }
            )
        except Exception as e:
            print(f'[TransactionLog ERROR] {e}')

        # Notify recipients  in-app and email
        try:

            if assigned_to:
                # Individual assignment — notify the employee
                Notification.objects.create(
                    recipient=assigned_to,
                    notification_type='kpi_alert',
                    message=(
                        f'A new KPI has been assigned to you: "{kpi.kpi_name}". '
                        f'Period: {period_start} to {period_end or "TBD"}. '
                        f'Please log in to view your assignment and submit your result.'
                    ),
                    is_read=False,
                )
                EmailNotificationService.send_new_assignment_email(
                    employee=assigned_to,
                    kpi_name=kpi.kpi_name,
                    period_start=period_start,
                    period_end=period_end,
                )

            elif assigned_team:
                # Team assignment — notify all team members
                team_members = User.objects.filter(team=assigned_team)
                for member in team_members:
                    Notification.objects.create(
                        recipient=member,
                        notification_type='kpi_alert',
                        message=(
                            f'A new KPI has been assigned to your team "{assigned_team.team_name}": '
                            f'"{kpi.kpi_name}". '
                            f'Period: {period_start} to {period_end or "TBD"}.'
                        ),
                        is_read=False,
                    )
                    EmailNotificationService.send_new_assignment_email(
                        employee=member,
                        kpi_name=kpi.kpi_name,
                        period_start=period_start,
                        period_end=period_end,
                    )

            elif assigned_department:
                # Department assignment — notify all department members
                dept_members = User.objects.filter(department=assigned_department)
                for member in dept_members:
                    Notification.objects.create(
                        recipient=member,
                        notification_type='kpi_alert',
                        message=(
                            f'A new KPI has been assigned to your department "{assigned_department.name}": '
                            f'"{kpi.kpi_name}". '
                            f'Period: {period_start} to {period_end or "TBD"}.'
                        ),
                        is_read=False,
                    )
                    EmailNotificationService.send_new_assignment_email(
                        employee=member,
                        kpi_name=kpi.kpi_name,
                        period_start=period_start,
                        period_end=period_end,
                    )

        except Exception as e:
            print(f'[Notification ERROR] {e}')

        return assignment

    def update_assignment(self, assignment_uuid: str, data: dict, triggered_by: User, request=None):
        assignment = self.get_by_uuid(assignment_uuid)

        old_values = {field: str(getattr(assignment, field, None)) for field in data}

        if 'assigned_to_uuid' in data:
            assignment.assigned_to = User.objects.get(uuid=data.pop('assigned_to_uuid')) if data[
                'assigned_to_uuid'] else None
        if 'assigned_team_uuid' in data:
            assignment.assigned_team = TeamService().get_by_uuid(data.pop('assigned_team_uuid')) if data[
                'assigned_team_uuid'] else None
        if 'assigned_department_uuid' in data:
            assignment.assigned_department = DepartmentService().get_by_uuid(data.pop('assigned_department_uuid')) if \
            data['assigned_department_uuid'] else None
        if 'kpi_uuid' in data:
            assignment.kpi = KPIService().get_by_uuid(data.pop('kpi_uuid')) if data['kpi_uuid'] else None
        if 'status' in data:
            assignment.status = Status.objects.filter(name__iexact=data.pop('status')).first()

        # Set remaining plain fields (period_start, period_end)
        for field, value in data.items():
            setattr(assignment, field, value)

        assignment.save()

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
                    'changed_fields': list(old_values.keys()),
                    'old_values': old_values,
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")
        return assignment

    def delete_assignment(self, assignment_uuid: str, triggered_by=None, request=None):
        assignment = self.get_by_uuid(assignment_uuid)

        try:
            TransactionLogService.log(
                event_code='kpi_assignment_deleted',
                triggered_by=triggered_by,
                entity=assignment,
                status_code='ACT',
                message=f"KPI assignment '{assignment.kpi.kpi_name}' deleted",
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'assignment_uuid': str(assignment_uuid),
                    'kpi_name': assignment.kpi.kpi_name,
                    'deleted_by': triggered_by.username if triggered_by else None,
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        assignment.delete()
        return assignment

    def get_all_assignments(self, **filters):
        qs = self.manager.all()
        if 'employee_scope' in filters:
            scope = filters['employee_scope']
            # Individual assignment — only results assigned directly to this user
            employee_q = models.Q(assigned_to__uuid=scope['user_uuid'])
            if scope.get('team_uuid'):
                employee_q |= models.Q(
                    assigned_team__uuid=scope['team_uuid']
                )
            if scope.get('department_uuid'):
                employee_q |= models.Q(
                    assigned_department__uuid=scope['department_uuid']
                )
            qs = qs.filter(employee_q)
        else:
            if 'user_uuid' in filters:
                qs = qs.filter(assigned_to__uuid=filters['user_uuid'])
            if 'team_uuid' in filters:
                qs = qs.filter(assigned_team__uuid=filters['team_uuid'])
            if 'department_uuid' in filters:
                dept_uuid = filters['department_uuid']
                qs = qs.filter(
                    models.Q(assigned_department__uuid=dept_uuid) |
                    models.Q(assigned_to__department__uuid=dept_uuid) |
                    models.Q(assigned_team__department__uuid=dept_uuid)
                )
        if 'status' in filters:
            qs = qs.filter(status__name=filters['status'])
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
        qs = self.manager.filter(kpi_assignment__isnull=False, is_deleted=False)
        from django.db.models import Q

        if 'employee_scope' in filters:
            scope = filters['employee_scope']
            # Individual assignment — results assigned directly to this user
            employee_q = Q(kpi_assignment__assigned_to__uuid=scope['user_uuid'])
            if scope.get('team_uuid'):
                # Team assignment — only show results submitted by this employee
                employee_q |= Q(
                    kpi_assignment__assigned_team__uuid=scope['team_uuid'],
                    submitted_by__uuid=scope['user_uuid']
                )
            if scope.get('department_uuid'):
                # Department assignment — only show results submitted by this employee
                employee_q |= Q(
                    kpi_assignment__assigned_department__uuid=scope['department_uuid'],
                    submitted_by__uuid=scope['user_uuid']
                )
            qs = qs.filter(employee_q)
        else:
            if 'user_uuid' in filters:
                qs = qs.filter(kpi_assignment__assigned_to__uuid=filters['user_uuid'])

            if 'team_uuid' in filters:
                qs = qs.filter(kpi_assignment__assigned_team__uuid=filters['team_uuid'])

            if 'department_uuid' in filters:
                dept = filters['department_uuid']
                qs = qs.filter(
                    Q(kpi_assignment__assigned_department__uuid=dept) |
                    Q(kpi_assignment__assigned_to__department__uuid=dept) |
                    Q(kpi_assignment__assigned_team__department__uuid=dept)
                )

        if 'period_start' in filters:
            qs = qs.filter(created_at__gte=filters['period_start'])

        if 'period_end' in filters:
            qs = qs.filter(created_at__lte=filters['period_end'])

        return qs

    @staticmethod
    def _get_active_formula(kpi):
        """Fetch the active formula linked to this KPI."""
        return kpi.formula.filter(status__code='ACT').first()

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
            min_t = float(kpi.min_threshold) if kpi.min_threshold else 0
            max_t = float(kpi.max_threshold) if kpi.max_threshold else 1

            # ── Guard against division by zero
            if max_t == min_t:
                print(f'[Formula WARNING] max_threshold equals min_threshold '
                      f'for KPI "{kpi.kpi_name}". Cannot calculate score.')
                return None

            if formula and formula.formula_expression:
                context = {
                    'actual': actual,
                    'target': target,
                    'weight': weight,
                    'min_threshold': min_t,
                    'max_threshold': max_t,
                }
                score = simple_eval(formula.formula_expression, names=context,functions ={'min':min, 'max':max,'abs':abs})
            else:
                # fallback if no active formula found
                max_val = target or actual or 1
                score = (actual / max_val) * 100

            # clamp score between 0 and 100
            score = max(0.0, min(float(score), 100.0))
            return round(float(score), 4)

        except ZeroDivisionError:
            print(f'[Formula ERROR] Division by zero for KPI "{kpi.kpi_name}"')
            return None
        except Exception as e:
            print(f'[Formula Calculation ERROR] {e}')
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
        assignment = result.kpi_assignment
        kpi = assignment.kpi if assignment else None
        return {
            'result_uuid':       str(result.uuid),
            'kpi_name':          kpi.kpi_name if kpi else 'Deleted KPI',
            'actual_value':      str(result.actual_value),
            'calculated_score':  str(result.calculated_score),
            'rating':            result.rating,
            'recorded_by':       result.recorded_by.email,
        }

    def create_result(self, assignment_uuid: str, actual_value,
                      triggered_by: User, request=None):

        with transaction.atomic():
            assignment = KPIAssignmentService().get_by_uuid(assignment_uuid)

            # Assignment must be active to accept submissions
            if assignment.status and assignment.status.code not in ('ACT', 'COM'):
                raise ValueError(
                    f'This assignment is not currently active and cannot accept submissions.'
                )

            existing = self.manager.filter(
                kpi_assignment=assignment,
                submitted_by=triggered_by,
            ).first()
            if existing:
                if existing.approval_status == 'rejected':
                    # Allow resubmission — delete old rejected result
                    existing.delete()
                else:
                    raise ValueError(
                        'You have already submitted a result for this KPI. '
                        'you can only update the result to change your submission if not approved.'
                    )

            #  Validate the submitter belongs to the assignment target
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
            #  actual value must be positive
            try:
                actual_float = float(actual_value)
            except (ValueError, TypeError):
                raise ValueError('Actual value must be a valid number.')

            if actual_float < 0:
                raise ValueError('Actual value cannot be negative.')

            #  KPI must have a target before submission
            kpi = assignment.kpi
            if not kpi.max_threshold:
                raise ValueError(
                    f'KPI "{kpi.kpi_name}" has no target value set. '
                    'Please ask your manager to set the target (max threshold) before submitting.'
                )

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
            from Base.models import Status
            completed_status = Status.objects.filter(code='COM').first()
            if completed_status:
                assignment.status = completed_status
                assignment.save(update_fields=['status'])

            # Log the transaction
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


            return result

    def update_result(self, result_uuid: str, data: dict, triggered_by: User, request=None):
        result = self.get_by_uuid(result_uuid)
        if not result.kpi_assignment:
            raise ValueError('Cannot update a result whose assignment has been deleted')
        kpi = result.kpi_assignment.kpi

        old_values = {'actual_value': str(result.actual_value)}

        if 'actual_value' in data:
            formula = self._get_active_formula(kpi)
            result.actual_value = data['actual_value']
            result.calculated_score = self._calculate_score(data['actual_value'], kpi, formula)
            result.rating = self._derive_comment(result.calculated_score, formula)
            result.comment = ''

        result.save(update_fields=['actual_value', 'calculated_score', 'rating', 'comment'])

        try:
            TransactionLogService.log(
                event_code='kpi_result_updated',
                triggered_by=triggered_by,
                entity=result,
                status_code='ACT',
                message=f'Result updated for KPI "{kpi.kpi_name}"',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                metadata={
                    'result_id': str(result.uuid),
                    'kpi_name': kpi.kpi_name,
                    'updated_by': triggered_by.email,
                    'old_values': old_values,
                    'new_values': {
                        'actual_value': str(result.actual_value),
                        'calculated_score': str(result.calculated_score),
                        'rating': result.rating,
                    },
                }
            )
        except Exception as e:
            print(f"[TransactionLog ERROR] {e}")

        return result

    def export_csv(self, **filters):


        qs = self.get_all_results(**filters).select_related(
            'kpi_assignment__kpi',
            'kpi_assignment__assigned_to',
            'recorded_by',
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'kpi_name', 'assigned_to', 'actual_value',
            'calculated_score', 'rating', 'comment', 'recorded_at', 'recorded_by',
        ])
        for r in qs:
            unit = r.kpi_assignment.kpi.measurement_type or ''
            assigned = (
                r.kpi_assignment.assigned_to.email if r.kpi_assignment.assigned_to else
                r.kpi_assignment.assigned_team.team_name if r.kpi_assignment.assigned_team else
                r.kpi_assignment.assigned_department.name if r.kpi_assignment.assigned_department else ''
            )
            writer.writerow([
                r.kpi_assignment.kpi.kpi_name,
                assigned,
                f"{float(r.actual_value):.2f} {unit}".strip(),
                f"{float(r.calculated_score):.2f}%" if r.calculated_score else '',
                r.rating.replace('_', ' ').title() if r.rating else '',
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

    @staticmethod
    def _validate_formula(expression):
        """
        Test the formula with safe dummy values before saving.
        Ensures it returns a numeric result and only uses allowed variables.
        """
        from simpleeval import simple_eval
        import re

        # Allowed variable names
        allowed_vars = {'actual', 'target', 'weight', 'min_threshold', 'max_threshold'}

        # Allowed functions and keywords to ignore during variable check
        allowed_functions = {'abs', 'round', 'int', 'float', 'min', 'max', 'if', 'else'}

        # Extract all word tokens from expression
        used_vars = set(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expression))

        # ── Remove allowed functions and keywords before checking
        unknown = used_vars - allowed_vars - allowed_functions
        if unknown:
            raise ValueError(
                f"Formula contains invalid variables: {', '.join(unknown)}. "
                f"Allowed variables are: actual, target, weight, min_threshold, max_threshold"
            )

        # Test with safe dummy values
        test_context = {
            'actual': 75.0,
            'target': 100.0,
            'weight': 1.0,
            'min_threshold': 0.0,
            'max_threshold': 100.0,
        }

        try:
            result = simple_eval(
                expression,
                names=test_context,
                functions={'min': min, 'max': max, 'abs': abs}
            )
        except ZeroDivisionError:
            raise ValueError(
                'Formula causes division by zero with test values. '
                'Check your min_threshold and max_threshold values.'
            )
        except Exception as e:
            raise ValueError(f'Formula is invalid: {str(e)}')

        if not isinstance(result, (int, float)):
            raise ValueError('Formula must return a numeric value.')

        return True
    def create_formula(self, kpi_uuid, formula_expression,formula_template=None, data_source='',
                       triggered_by: User = None, request=None):
        kpi = KPIService().get_by_uuid(kpi_uuid)
        self._validate_formula(formula_expression)
        active_status = Status.objects.filter(code='ACT').first()

        formula = self.manager.create(
            kpi=kpi,
            formula_expression=formula_expression,
            formula_template =formula_template,
            data_source=data_source,
            status=active_status,
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
        if 'formula_expression' in data:
            self._validate_formula(data['formula_expression'])

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
            user = User.objects.get(uuid=uuid)
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
    def list_users(request):
        qs = User.objects.select_related("role", "department", "team")

        # Line managers only see users in their department
        if getattr(request, 'is_line_manager', False) and request.department_scope:
            qs = qs.filter(department=request.department_scope)

        users = list(qs.values("uuid", "username", "email", "role__name", "department__name", "team__team_name",
                               "first_name", "last_name"))
        return ResponseProvider.success("Users retrieved successfully", data=users)


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


class OTPService:
    """
    Handles OTP generation, email sending, and verification.
    Used for password reset and first-login flows.
    Flow: create_otp(username, purpose),invalidates old OTPs, generates 6-digit code,
    saves to DB with 10-min expiry, emails the code.
    verify_otp(username, code, purpose)
    validates the code, marks it used, returns the user.
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
                message=f'Role updated for "{user.name}": {old_role} -> {new_role}',
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

    @staticmethod
    def _derive_summary_rating(weighted_score, results):
        """
        Derive the overall summary rating using weighted average
        of actual formula thresholds from all KPIs in the summary.
        Falls back to default thresholds if no active formula found.
        """
        formulas_with_weights = []
        for r in results:
            formula = r.kpi_assignment.kpi.formula.filter(status__code='ACT').first()
            weight = float(r.kpi_assignment.kpi.weight_value or 1)
            if formula:
                formulas_with_weights.append((formula, weight))

        total_fw = sum(w for _, w in formulas_with_weights)

        if formulas_with_weights and total_fw:
            outstanding = sum(float(f.outstanding_threshold or 90) * w for f, w in formulas_with_weights) / total_fw
            good = sum(float(f.good_threshold or 75) * w for f, w in formulas_with_weights) / total_fw
            satisfactory = sum(float(f.satisfactory_threshold or 60) * w for f, w in formulas_with_weights) / total_fw
            needs_imp = sum(float(f.needs_improvement_threshold or 40) * w for f, w in formulas_with_weights) / total_fw
        else:
            outstanding, good, satisfactory, needs_imp = 90, 75, 60, 40

        s = float(weighted_score)
        if s >= outstanding:    return 'outstanding'
        if s >= good:           return 'good'
        if s >= satisfactory:   return 'satisfactory'
        if s >= needs_imp:      return 'needs_improvement'
        return 'poor'

    # Individual Summary

    def generate_individual_summary(self, user_uuid, period_start, period_end,
                                    triggered_by=None, request=None):
        user = User.objects.select_related('department', 'team').get(uuid=user_uuid)

        results = KPIResults.objects.filter(
            submitted_by=user,
            created_at__date__gte=period_start,
            created_at__date__lte=period_end,
            calculated_score__isnull=False,
            approval_status='approved',
            kpi_assignment__isnull=False,
        ).select_related('kpi_assignment__kpi')
        if not results.exists():
            raise ValueError(
                'No approved KPI results found for this period. '
                'Ensure results have been submitted and approved before generating a summary.'
            )

        total_weighted = sum(
            float(r.calculated_score) * float(r.kpi_assignment.kpi.weight_value or 1)
            for r in results
        )
        total_weights = sum(
            float(r.kpi_assignment.kpi.weight_value or 1)
            for r in results
        )
        weighted_score = round(total_weighted / total_weights, 4) if total_weights else 0.0
        rating = self._derive_summary_rating(weighted_score, results)

        summary, _ = self.manager.update_or_create(
            user=user,
            period_start=period_start,
            period_end=period_end,
            defaults={
                'summary_type': PerformanceSummary.SummaryType.INDIVIDUAL,
                'department': user.department,
                'team': user.team,
                'weighted_score': weighted_score,
                'rating': rating,
            }
        )

        self._log(summary, triggered_by, request)
        self._notify_individual(summary, user)
        return summary

    # ── TEAM ──────────────────────────────────────────────────────────────────

    def generate_team_summary(self, team_uuid, period_start, period_end,
                              triggered_by=None, request=None):
        """
        Generates a performance summary for a team.
        Score = average of each member's individual weighted score.
        Each member contributes equally regardless of how many KPIs they had.
        Only members who have at least one approved result are included.
        """
        team = Team.objects.select_related('department').get(uuid=team_uuid)

        # Collect all approved results submitted by members of this team
        # across ALL assignment types — individual, team, and department.
        # Filtering by submitted_by guarantees no double counting since
        # each result row belongs to exactly one submitter.
        all_results = KPIResults.objects.filter(
            submitted_by__team=team,
            created_at__date__gte=period_start,
            created_at__date__lte=period_end,
            calculated_score__isnull=False,
            approval_status='approved',
            kpi_assignment__isnull=False,
        ).select_related('submitted_by', 'kpi_assignment__kpi')

        if not all_results.exists():
            raise ValueError(
                'No approved KPI results found for this period. '
                'Ensure results have been submitted and approved before generating a summary.'
            )

        # Calculate each member's weighted score independently
        # Group results by member using submitted_by
        member_scores = {}
        for r in all_results:
            member = r.submitted_by
            if member not in member_scores:
                member_scores[member] = {'weighted': 0.0, 'weights': 0.0}
            weight = float(r.kpi_assignment.kpi.weight_value or 1)
            member_scores[member]['weighted'] += float(r.calculated_score) * weight
            member_scores[member]['weights'] += weight

        # Each member's score = their own weighted average
        individual_scores = [
            v['weighted'] / v['weights']
            for v in member_scores.values()
            if v['weights'] > 0
        ]

        # Team score = average of member scores — every member contributes equally
        weighted_score = round(
            sum(individual_scores) / len(individual_scores), 4
        ) if individual_scores else 0.0

        rating = self._derive_summary_rating(weighted_score, all_results)

        summary, _ = self.manager.update_or_create(
            team=team,
            period_start=period_start,
            period_end=period_end,
            defaults={
                'summary_type': PerformanceSummary.SummaryType.TEAM,
                'department': team.department,
                'weighted_score': weighted_score,
                'rating': rating,
            }
        )

        self._log(summary, triggered_by, request)
        self._notify_team(summary, team, triggered_by=triggered_by)
        return summary
    # Department Summary

    def generate_department_summary(self, department_uuid, period_start, period_end,
                                    triggered_by=None, request=None):
        """
        Generates a performance summary for a department.
        Uses two-level aggregation:
        each member's weighted score from all their approved results
        each team's score = average of its member scores
        Department score = average of team scores
        Members with no team are grouped as a standalone score contributor.
        Only members with at least one approved result are included.
        No double counting — results grouped by submitted_by.
        """


        department = Department.objects.get(uuid=department_uuid)

        # Collect ALL approved results submitted by anyone in this department
        # across all assignment types — individual, team, and department.
        # Filtering by submitted_by__department guarantees no double counting.
        all_results = KPIResults.objects.filter(
            submitted_by__department=department,
            created_at__date__gte=period_start,
            created_at__date__lte=period_end,
            calculated_score__isnull=False,
            approval_status='approved',
            kpi_assignment__isnull=False,
        ).select_related('submitted_by', 'submitted_by__team', 'kpi_assignment__kpi')

        if not all_results.exists():
            raise ValueError(
                'No approved KPI results found for this period. '
                'Ensure results have been submitted and approved before generating a summary.'
            )

        #  calculate each member's weighted score
        member_scores = {}
        for r in all_results:
            member = r.submitted_by
            if member not in member_scores:
                member_scores[member] = {
                    'weighted': 0.0,
                    'weights': 0.0,
                    'team': member.team,
                }
            weight = float(r.kpi_assignment.kpi.weight_value or 1)
            member_scores[member]['weighted'] += float(r.calculated_score) * weight
            member_scores[member]['weights'] += weight

        #  group member scores by team
        # Members with no team are collected separately as ungrouped
        team_buckets = {}  # team =list of member scores
        ungrouped = []  # members not in any team

        for member, data in member_scores.items():
            if data['weights'] == 0:
                continue
            score = data['weighted'] / data['weights']
            team = data['team']
            if team:
                if team not in team_buckets:
                    team_buckets[team] = []
                team_buckets[team].append(score)
            else:
                ungrouped.append(score)

        # Step 3 — each team score = average of its member scores
        team_scores = [
            sum(scores) / len(scores)
            for scores in team_buckets.values()
            if scores
        ]

        # Ungrouped members contribute their scores directly
        # alongside team scores so they are not lost
        all_contributing_scores = team_scores + ungrouped

        if not all_contributing_scores:
            raise ValueError(
                'No approved KPI results found for this period. '
                'Ensure results have been submitted and approved before generating a summary.'
            )

        # Department score = average of team scores (and ungrouped member scores)
        weighted_score = round(
            sum(all_contributing_scores) / len(all_contributing_scores), 4
        )

        rating = self._derive_summary_rating(weighted_score, all_results)

        summary, _ = self.manager.update_or_create(
            department=department,
            period_start=period_start,
            period_end=period_end,
            defaults={
                'summary_type': PerformanceSummary.SummaryType.DEPARTMENT,
                'weighted_score': weighted_score,
                'rating': rating,
            }
        )

        self._log(summary, triggered_by, request)
        self._notify_department(summary, department, triggered_by=triggered_by)
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

    def _notify_team(self, summary, team, triggered_by=None):
        """
        After team summary is generated:
        notify all team members, the line manager, and HR.
        Skip notifying the manager if they generated the summary themselves.
        """
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

        # ── notify line managers — skip if they generated it themselves ────
        managers = User.objects.filter(
            department     = team.department,
            role__is_manager = True,
        )
        for manager in managers:
            if triggered_by and manager == triggered_by:
                continue  # skip — they generated it themselves
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

    def _notify_department(self, summary, department, triggered_by=None):
        """
        After department summary is generated:
        notify the department line manager and HR.
        Skip notifying the manager if they generated the summary themselves.
        """
        managers = User.objects.filter(
            department     = department,
            role__is_manager= True,
        )

        # ── notify line managers — skip if they generated it themselves ────
        for manager in managers:
            if triggered_by and manager == triggered_by:
                continue  # skip — they generated it themselves
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

    # ── LOGGING

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
            'summary_type', 'subject', 'department',
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
                s.summary_type,
                subject,
                s.department.name if s.department else '',
                s.team.team_name if s.team else '',
                s.period_start,
                s.period_end,
                f"{float(s.weighted_score):.2f}%",
                s.created_at.strftime('%Y-%m-%d %H:%M:%S') if s.created_at else '',
            ])

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=performance_summaries.csv'
        return response