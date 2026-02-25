from ipaddress import ip_address

from django.contrib.auth.hashers import make_password, check_password

import kpis
from Base.models import Status
from accounts.models import User, Role ,RefreshToken
from kpis.models import KpiDefinition, KpiAssignment,KPIResults,KPIFormula
from Transaction.models import TransactionLog, EventTypes
from organization.models import Department, Team
from services.serviceBase import ServiceBase, service_handler
from services.utils.response_provider import ResponseProvider
import json
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

    @service_handler(require_auth=True, allowed_roles=["admin", ])
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

    @service_handler(require_auth=True, allowed_roles=["admin", ])
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


    def delete_kpi(self, kpi_uuid: str, triggered_by: User, request=None):
        kpi = self.get_by_uuid(kpi_uuid)
        kpi.delete()
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

    @service_handler(require_auth=True, allowed_roles=["admin", "Business Line manager", "Tech Line manager"])
    def get_by_uuid(self, assignment_uuid: str):
        return self.manager.get(uuid=assignment_uuid)

    @service_handler(require_auth=True, allowed_roles=["admin", "Business Line manager", "Tech Line manager"])
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

    @service_handler(require_auth=True, allowed_roles=["admin", "Business Line manager", "Tech Line manager"])
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

    @service_handler(require_auth=True, allowed_roles=["admin","Business Line manager","Tech Line manager"])
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




class KPIResultsService(ServiceBase):
    manager = KPIResults.objects

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
        return self.manager.filter(kpi__uuid=kpi_uuid)

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
        formula.delete()
        return formula


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




    @staticmethod
    def delete_user(username: str):
        """
        Delete a user  by username and returns response provider if
        user doesn't exist, returns success if user is deleted successfully.
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return ResponseProvider.not_found(error=f"User '{username}' not found")

        user.delete()
        return ResponseProvider.success(message=f"User '{username}' deleted successfully")

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
    manager = Role.objects

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

    @staticmethod
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












