from django.urls import path, include
from .views import create_kpi_definition_view, get_all_kpis_definition_view, delete_kpi_definition_view, \
  update_kpi_definition_view, get_kpi_definition_view

urlpatterns = [
  path('kpi_definition/create/',create_kpi_definition_view, name='create_kpi_definition'),
  path('kpi_definition/list_all/', get_all_kpis_definition_view, name='get_all_kpis_definition'),
  path('kpi_definition/delete/', delete_kpi_definition_view, name='delete_kpi_definition'),
  path('kpi_definition/update/', update_kpi_definition_view, name='update_kpi_definition'),
  path('kpi_definition/get_kpi/<uuid:kpi_uuid>/', get_kpi_definition_view, name='get_kpi_definition' ),
    ]
