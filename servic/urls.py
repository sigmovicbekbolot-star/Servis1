from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('config.urls')),       # HTML интерфейс
    path('api/', include('config.api_urls')),  # API интерфейс
]


