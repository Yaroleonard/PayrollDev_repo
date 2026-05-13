from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/employees/', include('employees.urls')),
    path('api/payroll/', include('payroll.urls')),
    path('api/leaves/', include('leaves.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
