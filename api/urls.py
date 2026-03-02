from django.urls import path, include


urlpatterns = [
    path("auth/", include("accounts.urls")),
    path("kpis/", include("kpis.urls")),
    path("org/", include("organization.urls")),
    path('performance/', include('performance.urls')),
    path('audit/', include('Transaction.urls')),

]