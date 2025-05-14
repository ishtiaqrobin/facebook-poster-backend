from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('facebook_poster.urls')),  # Include facebook poster app URLs
]
