from django.urls import path
from django.urls import path
from Transaction.views import get_all_logs_view, get_log_view

urlpatterns = [
    path('logs/', get_all_logs_view, name='get_all_logs'),
    path('logs/<str:log_uuid>/', get_log_view, name='get_log'),
]
