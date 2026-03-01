from django.urls import path, include
from .views import create_kpi_definition_view, get_all_kpis_definition_view, delete_kpi_definition_view, \
  update_kpi_definition_view, get_kpi_definition_view, create_kpi_assignment_view, update_kpi_assignment_view, \
  get_kpi_assignments_view, create_kpi_formula_view, update_kpi_formula_view, delete_kpi_formula_view, \
  get_kpi_formula_view, submit_kpi_result_view, get_kpi_result_view, get_all_kpi_results_view, update_kpi_result_view, \
  export_kpi_results_csv_view

urlpatterns = [
  #-----------------------------------------------------------------------------------------
  # KPI DEFINITION URLS
  #-----------------------------------------------------------------------------------------
  path('kpi_definition/create/',create_kpi_definition_view, name='create_kpi_definition'),
  path('kpi_definition/list_all/', get_all_kpis_definition_view, name='get_all_kpis_definition'),
  path('kpi_definition/delete/<uuid:kpi_uuid>', delete_kpi_definition_view, name='delete_kpi_definition'),
  path('kpi_definition/update/<uuid:kpi_uuid>/', update_kpi_definition_view, name='update_kpi_definition'),
  path('kpi_definition/get_kpi/<uuid:kpi_uuid>/', get_kpi_definition_view, name='get_kpi_definition' ),
  path('kpi_assignment/create/', create_kpi_assignment_view , name='create_kpi_assignment'),
  path('kpi_assignment/update/<uuid:assignment_uuid>/', update_kpi_assignment_view, name='update_kpi_assignment'),
  path('kpi_assignment/get_all/', get_kpi_assignments_view, name='get_kpi_assignments'),
  #-----------------------------------------------------------------------------------------------
  #             KPI FORMULA URLS
  #--------------------------------------------------------------------------------------------------
  path('kpi_formula/create/', create_kpi_formula_view, name='create_kpi_formula'),
  path('kpi_formula/update/<uuid:formula_uuid>', update_kpi_formula_view, name='update_kpi_formula'),
  path('kpi_formula/delete/<uuid:formula_uuid>',delete_kpi_formula_view ,name = 'delete_kpi_formula'),
  path('kpi_formula/get_formula/<uuid:kpi_uuid>', get_kpi_formula_view, name='get_kpi_formula'),

#-------------------------------------------------------------------------------------------------
#       KPI RESULTS URL
#-------------------------------------------------------------------------------------------------
  path('kpi_results/submit/',submit_kpi_result_view, name='submit_kpi_result'),
  path('kpi_results/get_one/<str:result_uuid>/', get_kpi_result_view, name='get_kpi_result'),
  path('kpi_results/get_all/', get_all_kpi_results_view, name='get_all_kpi_results'),
  path('kpi_results/update/<str:result_uuid>/', update_kpi_result_view, name='update_kpi_results'),
  path('kpi_results/export_csv/', export_kpi_results_csv_view, name='export_kpi_results_csv'),



    ]
