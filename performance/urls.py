from django.urls import path
from performance.views import (
    generate_summary_view,
    get_summary_view,
    get_all_summaries_view,
    export_summaries_csv_view, get_notifications_view, get_all_notifications_view, mark_notification_read_view,
    mark_all_notifications_read_view,
)

urlpatterns = [
    path('performance/summaries/generate/', generate_summary_view, name='generate_summary'),
    path('performance/summaries/get_all/', get_all_summaries_view, name='get_all_summaries'),
    path('performance/summaries/<str:summary_uuid>/',get_summary_view,name='get_summary'),
    path('performance/summaries/export/csv/',export_summaries_csv_view, name='export_summaries_csv'),
path('notifications/get/',
         get_notifications_view,
         name='get_notifications'),

    path('notifications/all/',
         get_all_notifications_view,
         name='get_all_notifications'),

    path('notifications/<int:notification_id>/read/',
         mark_notification_read_view,
         name='mark_notification_read'),

    path('notifications/read_all/',
         mark_all_notifications_read_view,
         name='mark_all_notifications_read'),
]