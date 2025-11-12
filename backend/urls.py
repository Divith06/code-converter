from django.contrib import admin
from django.urls import path, include
from frontend import views as frontend_views

urlpatterns = [
    path('', frontend_views.index, name='index'),
    path('admin/', admin.site.urls),
    path('api/', include('converter_app.urls')),
]
