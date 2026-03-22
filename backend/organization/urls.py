from django.urls import path

from organization import views
urlpatterns = [
#------------------------------------------------------------------------
# DEPARTMENT URLS
#------------------------------------------------------------------------

path('create_department/', views.create_department_view, name='create-department'),
path('all_departments/', views.get_all_departments_view, name='get-all-departments'),
path('get_department/<str:dept_uuid>/', views.get_department_view, name='get-department'),
path('update_department/<str:dept_uuid>/', views.update_department_view, name='update-department'),
path('delete_department/<str:dept_uuid>/', views.delete_department_view, name='delete-department'),
#----------------------------------------------------------------------------------
# TEAM URLS
#----------------------------------------------------------------------------------

path('create_team/', views.create_team_view, name='create-team'),
path('all_teams/', views.get_all_teams_view, name='get-all-teams'),
path('assign-user_team/', views.assign_user_to_team_view, name='assign-user-to-team'),
path('get_team/<str:team_uuid>/', views.get_team_view, name='get-team'),
path('update_team/<str:team_uuid>/', views.update_team_view, name='update-team'),
path('delete_team/<str:team_uuid>/', views.delete_team_view, name='delete-team'),
]