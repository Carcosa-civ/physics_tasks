from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),                               # все маршруты core, включая logout
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    # logout обрабатывается в core.urls, поэтому здесь его нет
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)