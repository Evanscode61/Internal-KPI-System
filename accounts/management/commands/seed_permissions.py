from django.core.management.base import BaseCommand
from accounts.models import Permission, Role


class Command(BaseCommand):
    help = 'Seeds the Permission table and links permissions to roles'

    # Define all permissions in the system
    PERMISSIONS = [

        # ── User Management ───────────────────────────────────────────
        {'codename': 'create_user',         'name': 'Create User',
         'description': 'Can create new users'},
        {'codename': 'update_user',         'name': 'Update User',
         'description': 'Can update existing users'},
        {'codename': 'delete_user',         'name': 'Delete User',
         'description': 'Can delete users'},
        {'codename': 'view_all_users',      'name': 'View All Users',
         'description': 'Can view all users in the system'},

        # ── Role Management ───────────────────────────────────────────
        {'codename': 'create_role',         'name': 'Create Role',
         'description': 'Can create new roles'},
        {'codename': 'update_role',         'name': 'Update Role',
         'description': 'Can update existing roles'},
        {'codename': 'delete_role',         'name': 'Delete Role',
         'description': 'Can delete roles'},
        {'codename': 'assign_role',         'name': 'Assign Role',
         'description': 'Can assign roles to users'},

        # ── Department Management ─────────────────────────────────────
        {'codename': 'create_department',   'name': 'Create Department',
         'description': 'Can create departments'},
        {'codename': 'update_department',   'name': 'Update Department',
         'description': 'Can update departments'},
        {'codename': 'delete_department',   'name': 'Delete Department',
         'description': 'Can delete departments'},
        {'codename': 'view_department',     'name': 'View Department',
         'description': 'Can view department details'},

        # ── Team Management ───────────────────────────────────────────
        {'codename': 'create_team',         'name': 'Create Team',
         'description': 'Can create teams'},
        {'codename': 'update_team',         'name': 'Update Team',
         'description': 'Can update teams'},
        {'codename': 'delete_team',         'name': 'Delete Team',
         'description': 'Can delete teams'},
        {'codename': 'assign_user_to_team', 'name': 'Assign User To Team',
         'description': 'Can assign users to teams'},

        # ── KPI Definition ────────────────────────────────────────────
        {'codename': 'create_kpi',          'name': 'Create KPI',
         'description': 'Can create KPI definitions'},
        {'codename': 'update_kpi',          'name': 'Update KPI',
         'description': 'Can update KPI definitions'},
        {'codename': 'delete_kpi',          'name': 'Delete KPI',
         'description': 'Can delete KPI definitions'},
        {'codename': 'view_kpi',            'name': 'View KPI',
         'description': 'Can view KPI definitions'},

        # ── KPI Assignment ────────────────────────────────────────────
        {'codename': 'assign_kpi',          'name': 'Assign KPI',
         'description': 'Can assign KPIs to users, teams, or departments'},
        {'codename': 'update_kpi_assignment','name': 'Update KPI Assignment',
         'description': 'Can update KPI assignments'},
        {'codename': 'view_kpi_assignment',  'name': 'View KPI Assignment',
         'description': 'Can view KPI assignments'},

        # ── KPI Formula ───────────────────────────────────────────────
        {'codename': 'create_kpi_formula',  'name': 'Create KPI Formula',
         'description': 'Can create KPI formulas'},
        {'codename': 'update_kpi_formula',  'name': 'Update KPI Formula',
         'description': 'Can update KPI formulas'},
        {'codename': 'delete_kpi_formula',  'name': 'Delete KPI Formula',
         'description': 'Can delete KPI formulas'},
        {'codename': 'view_kpi_formula',    'name': 'View KPI Formula',
         'description': 'Can view KPI formulas'},

        # ── KPI Results ───────────────────────────────────────────────
        {'codename': 'submit_kpi_result',   'name': 'Submit KPI Result',
         'description': 'Can submit KPI results'},
        {'codename': 'update_kpi_result',   'name': 'Update KPI Result',
         'description': 'Can update KPI results'},
        {'codename': 'view_kpi_result',     'name': 'View KPI Result',
         'description': 'Can view KPI results'},
        {'codename': 'export_kpi_results',  'name': 'Export KPI Results',
         'description': 'Can export KPI results to CSV'},

        # ── Performance Summary ───────────────────────────────────────
        {'codename': 'generate_summary',    'name': 'Generate Summary',
         'description': 'Can generate performance summaries'},
        {'codename': 'view_own_summary',    'name': 'View Own Summary',
         'description': 'Can view own performance summary'},
        {'codename': 'view_team_summary',   'name': 'View Team Summary',
         'description': 'Can view team performance summaries'},
        {'codename': 'view_dept_summary',   'name': 'View Department Summary',
         'description': 'Can view department performance summaries'},
        {'codename': 'view_all_summaries',  'name': 'View All Summaries',
         'description': 'Can view all performance summaries'},
        {'codename': 'export_summaries',    'name': 'Export Summaries',
         'description': 'Can export performance summaries to CSV'},

        # ── Notifications ─────────────────────────────────────────────
        {'codename': 'view_notifications',  'name': 'View Notifications',
         'description': 'Can view own notifications'},
        {'codename': 'mark_notification_read', 'name': 'Mark Notification Read',
         'description': 'Can mark notifications as read'},
    ]

    # Define which permissions each role gets
    ROLE_PERMISSIONS = {
        'admin': [
            'create_user', 'update_user', 'delete_user', 'view_all_users',
            'create_role', 'update_role', 'delete_role', 'assign_role',
            'create_department', 'update_department', 'delete_department', 'view_department',
            'create_team', 'update_team', 'delete_team', 'assign_user_to_team',
            'create_kpi', 'update_kpi', 'delete_kpi', 'view_kpi',
            'assign_kpi', 'update_kpi_assignment', 'view_kpi_assignment',
            'create_kpi_formula', 'update_kpi_formula', 'delete_kpi_formula', 'view_kpi_formula',
            'submit_kpi_result', 'update_kpi_result', 'view_kpi_result', 'export_kpi_results',
            'generate_summary', 'view_own_summary', 'view_team_summary',
            'view_dept_summary', 'view_all_summaries', 'export_summaries',
            'view_notifications', 'mark_notification_read',
        ],
        'hr': [
            'view_all_users',
            'view_department', 'view_kpi', 'view_kpi_assignment',
            'view_kpi_formula', 'view_kpi_result', 'export_kpi_results',
            'generate_summary', 'view_all_summaries', 'export_summaries',
            'view_notifications', 'mark_notification_read',
        ],
        'business_line_manager': [
            'view_all_users',
            'view_department', 'view_kpi', 'assign_kpi',
            'view_kpi_assignment', 'view_kpi_formula',
            'view_kpi_result', 'export_kpi_results',
            'view_team_summary', 'view_dept_summary', 'export_summaries',
            'view_notifications', 'mark_notification_read',
        ],
        'tech_line_manager': [
            'view_all_users',
            'view_department', 'view_kpi', 'assign_kpi',
            'view_kpi_assignment', 'view_kpi_formula',
            'view_kpi_result', 'export_kpi_results',
            'view_team_summary', 'view_dept_summary', 'export_summaries',
            'view_notifications', 'mark_notification_read',
        ],
        'employee': [
            'view_kpi', 'view_kpi_assignment',
            'submit_kpi_result', 'view_kpi_result',
            'view_own_summary',
            'view_notifications', 'mark_notification_read',
        ],
    }

    def handle(self, *args, **kwargs):

        self.stdout.write('\n── Seeding Permissions ──────────────────────')

        # Step 1 — Create all permissions
        perm_created  = 0
        perm_skipped  = 0

        for perm in self.PERMISSIONS:
            obj, created = Permission.objects.get_or_create(
                codename = perm['codename'],
                defaults = {
                    'name':        perm['name'],
                    'description': perm['description'],
                }
            )
            if created:
                perm_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  Created permission: {perm["codename"]}')
                )
            else:
                perm_skipped += 1

        self.stdout.write(
            f'\n  Permissions — {perm_created} created, {perm_skipped} already existed'
        )

        # Step 2 — Link permissions to roles
        self.stdout.write('\n── Linking Permissions to Roles ─────────────')

        for role_name, codenames in self.ROLE_PERMISSIONS.items():
            role = Role.objects.filter(name=role_name).first()

            if not role:
                self.stdout.write(
                    self.style.WARNING(f'  Role not found: {role_name} — skipping')
                )
                continue

            permissions = Permission.objects.filter(codename__in=codenames)
            role.permissions.set(permissions)

            self.stdout.write(
                self.style.SUCCESS(
                    f'  {role_name} → {permissions.count()} permissions assigned'
                )
            )

        self.stdout.write(
            self.style.SUCCESS('\n── Done ─────────────────────────────────────\n')
        )