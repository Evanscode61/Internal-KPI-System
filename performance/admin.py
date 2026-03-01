from django.contrib import admin
from performance.models import *
admin.site.register(PerformanceSummary)
admin.site.register(KPIAlert)
admin.site.register(Notification)