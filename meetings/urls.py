from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from django.urls import path, include
from .views import MeetingViewSet, ParticipantViewSet, MeetingNotificationViewSet

# Primary router
router = DefaultRouter()
router.register(r"meetings", MeetingViewSet, basename="meeting")

# Nested: /api/meetings/{meeting_pk}/participants/
meetings_router = nested_routers.NestedDefaultRouter(router, r"meetings", lookup="meeting")
meetings_router.register(r"participants", ParticipantViewSet, basename="meeting-participants")
meetings_router.register(r"notifications", MeetingNotificationViewSet, basename="meeting-notifications")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(meetings_router.urls)),
]
