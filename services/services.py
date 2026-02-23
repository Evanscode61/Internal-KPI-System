from ipaddress import ip_address

from django.contrib.auth.hashers import make_password, check_password

import kpis
from Base.models import Status
from accounts.models import User, Role
from kpis.models import KpiDefinition, KpiAssignment,KPIResults,KPIFormula
from Transaction.models import TransactionLog, EventTypes
from organization.models import Department, Team
from services.serviceBase import ServiceBase, service_handler
from services.utils.response_provider import ResponseProvider
import json

class DepartmentService(ServiceBase):
    manager = Department.objects

    def get_all_departments(self):
            return self.manager.all()

    def get_by_uuid(self, dept_uuid: str):
            return self.manager.get(uuid=dept_uuid)

    def create_department(self, name, description='', triggered_by: User = None, request=None):
        department = self.manager.create(
            name=name,
            description=description,
        )
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

    def delete_kpi(self, kpi_uuid: str, triggered_by: User, request=None):
        kpi = self.get_by_uuid(kpi_uuid)
        kpi.delete()

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


    def create_kpi_assignment(self, kpi_uuid, assigned_period, assigned_to_uuid=None,
                          assigned_team_uuid=None, assigned_department_uuid=None,
                          status='active', triggered_by: User = None, request=None):
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
            assigned_period=assigned_period,
            status=status,
        )
        try:
            TransactionLogService.log(
                event_code ='kpi_assignment',
                triggered_by=triggered_by,
                entity=assignment,
                status_code ='assigned successfully',
                message = f'KPI "{kpi.kpi_name}" assigned',
                ip_address = request.META.get('REMOTE_ADDR'),
                metadata ={
                    'assignment_id' : str(assignment.uuid),
                    'kpi_id': str(kpi.uuid),
                    'assigned_to' : assigned_to.role if assigned_to else None,
                    'assigned_team' : assigned_team.team_name if assigned_team else None,
                    'assigned_department' : assigned_department.name if assigned_department else None,
                    'assigned_period' : str(assigned_period),
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
        event_type = EventTypes.objects.get(code=event_code)
        status     = Status.objects.get(code=status_code)

        return TransactionLog.objects.create(
            event_type=event_type,
            triggered_by=triggered_by,
            status=status,
            event_message=message,
            metadata=metadata or {},
            entity_type=entity.__class__.__name__,
            entity_id=str(entity.pk),
            user_ip_address=ip_address
        )

    @staticmethod
    def get_logs_for_entity(entity):
        """All logs for a specific entity e.g. a KPI or KPIResult."""
        return TransactionLog.objects.filter(
            entity_type=entity.__class__.__name__,
            entity_id=str(entity.pk)
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
        ).select_related('event_type', 'status')


class TeamService(ServiceBase):
    manager = Team

    def get_by_uuid(self, team_uuid: str):
        return self.manager.get(uuid=team_uuid)

class KPIResultsService(ServiceBase):
    manager = KPIResults.objects

class KPIFormulaService(ServiceBase):
    manager = KPIFormula.objects


class UserService(ServiceBase):
    manager = User.objects

    def register_user(self, username, email, password, role_name=None):
        if self.filter(email=email).exists():
            raise ValueError("Email already exists")
        role = Role.objects.filter(name=role_name or "Staff").first()
        if not role:
            raise ValueError("Role not found")
        return self.create(
            username=username,
            email=email,
            password=make_password(password),
            role=role,
            is_active=True
        )

    def authenticate_user(self, email, password):
        user = self.filter(email=email).first()
        if not user or not check_password(password, user.password):
            raise ValueError("Invalid credentials")
        if not user.is_active:
            raise ValueError("Account inactive")
        return user

    @staticmethod
    def change_password(self, user, old_password, new_password):
        if not check_password(old_password, user.password):
            raise ValueError("Old password incorrect")
        user.password = make_password(new_password)
        user.save()
        return True

    @staticmethod
    @service_handler(require_auth=True, allowed_roles=["admin"])
    def assign_role(self, user, role_name):
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
                     .values("id", "username", "email", "role__name"))
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

        return user

class RoleService(ServiceBase):
    manager = Role

    class RoleService:

        @staticmethod
        @service_handler(require_auth=True, allowed_roles=["admin"])
        def update_user_role(request, username, new_role):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return ResponseProvider.not_found(error="User not found")

            user.role = new_role
            user.save(update_fields=["role"])

            data = {
                "username": user.username,
                "email": user.email,
                "role": user.role
            }

            return ResponseProvider.success(
                message="User role updated successfully",
                data=data
            )



class AuthService:
    @staticmethod
    def logout(refresh_token):
        try:
            token = RefreshToken.objects.get(token=refresh_token)
            token.delete()
        except RefreshToken.DoesNotExist:
            raise LookupError("Invalid refresh token")

#password management
""" 
    def deactivate_user(self, uuid):
        return self.update(uuid=uuid, is_active=False)
class ForgotPassword:
    objects = None

    def forgot_password(self, email):
        user = self.filter(email=email).first()
        if not user:
            raise ValueError("User not found")

        reset_token = str(uuid.uuid4())

        ForgotPassword.objects.create(
            user=user,
            token=reset_token,
            created_at=timezone.now()
        )

        return reset_token
        """
#status of the account
"""
    def deactivate_user(self, uuid):
        return self.update(uuid=uuid, is_active=False)

    def activate_user(self, uuid):
        return self.update(uuid=uuid, is_active=True)"""




