from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. Админ панель
    path('admin/', admin.site.urls),

    # 2. Тилди которуу механизми (СӨЗСҮЗ КЕРЕК!)
    path('i18n/', include('django.conf.urls.i18n')),

    # 3. HTML интерфейс (негизги логика)
    path('', include('config.urls')),

    # 4. API интерфейс
    path('api/', include('config.api_urls')),
]

# Сүрөттөр (media) жана статикалык файлдар үчүн (DEBUG режиминде)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)