from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from .views import (
    MeetingNotificationViewSet,
    MeetingViewSet,
    ParticipantViewSet,
)

# Primary router -- /api/meetings/
router = DefaultRouter()
router.register(r"meetings", MeetingViewSet, basename="meeting")

# Nested routers -- /api/meetings/{meeting_pk}/...
meetings_router = nested_routers.NestedDefaultRouter(
    router, r"meetings", lookup="meeting"
)
meetings_router.register(
    r"participants",
    ParticipantViewSet,
    basename="meeting-participants",
)
meetings_router.register(
    r"notifications",
    MeetingNotificationViewSet,
    basename="meeting-notifications",
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(meetings_router.urls)),
]
