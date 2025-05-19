from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacebookViewSet, home, facebook_profile
from .auth.facebook_login import facebook_login
from .auth.facebook_callback import facebook_callback
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'facebook', FacebookViewSet, basename='facebook')

urlpatterns = [
    path('', home, name='home'),
    path('api/facebook/login/', facebook_login, name='facebook_login'),
    path('api/facebook/callback/', facebook_callback, name='facebook_callback'),
    path('api/facebook/profile/', facebook_profile, name='facebook_profile'),
    path('api/facebook/pages/', FacebookViewSet.as_view({'get': 'pages'}), name='facebook_pages'),
    path('api/facebook/create_post/', FacebookViewSet.as_view({'post': 'create_post'}), name='facebook_create_post'),
    path('api/facebook/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
