from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProfileViewSet, UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")
router.register(r"profiles", ProfileViewSet, basename="profile")

urlpatterns = [
    path("", include(router.urls)),
]
