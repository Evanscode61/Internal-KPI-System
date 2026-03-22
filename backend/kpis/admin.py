from django.contrib import admin
from kpis.models import KpiAssignment,KpiDefinition,KPIFormula,KPIResults

admin.site.register(KpiDefinition)
admin.site.register(KPIFormula)
admin.site.register(KPIResults)
admin.site.register(KpiAssignment)

# Register your models here.
