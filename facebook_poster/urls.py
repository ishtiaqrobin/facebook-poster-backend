from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacebookViewSet, home
from .auth.facebook_login import facebook_login
from .auth.facebook_callback import facebook_callback

router = DefaultRouter()
router.register(r'facebook', FacebookViewSet, basename='facebook')

urlpatterns = [
    path('', home, name='home'),
    path('api/facebook/login/', facebook_login, name='facebook_login'),
    path('api/facebook/callback/', facebook_callback, name='facebook_callback'),
]
