from django.contrib import admin
from django.urls import path
from controllers import home_controller, auth_controller
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # controller routes
    path('', home_controller.index, name='index'),
    path('login/', auth_controller.login_view, name='login'),
    path('register/', auth_controller.register_view, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
