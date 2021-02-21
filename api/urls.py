from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from api.views import PostsViewSet

router = DefaultRouter()
router.register(r'posts', PostsViewSet, basename='posts')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/api-token-auth/', obtain_auth_token, name='get_token')
]
