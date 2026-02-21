from django.contrib import admin

from .models import Meeting, MeetingNotification, Participant


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0
    readonly_fields = ("invited_at", "responded_at")
    fields = (
        "email", "name", "user",
        "status", "invited_at", "responded_at",
    )


class NotificationInline(admin.TabularInline):
    model = MeetingNotification
    extra = 0
    readonly_fields = ("sent_at", "is_sent")
    fields = ("email", "notification_type", "is_sent", "sent_at")


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        "title", "start_time", "end_time",
        "status", "created_by", "created_at",
    )
    list_filter = ("status", "created_at", "start_time")
    search_fields = (
        "title", "description", "location", "created_by__email"
    )
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [ParticipantInline, NotificationInline]

    fieldsets = (
        (
            None,
            {"fields": ("id", "title", "description", "location")},
        ),
        (
            "Schedule",
            {"fields": ("start_time", "end_time", "status")},
        ),
        (
            "Meta",
            {"fields": ("created_by", "created_at", "updated_at")},
        ),
    )


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "email", "name", "meeting", "status", "invited_at"
    )
    list_filter = ("status",)
    search_fields = ("email", "name", "meeting__title")
    readonly_fields = ("invited_at", "responded_at")


@admin.register(MeetingNotification)
class MeetingNotificationAdmin(admin.ModelAdmin):
    list_display = (
        "email", "meeting", "notification_type",
        "is_sent", "sent_at",
    )
    list_filter = ("notification_type", "is_sent")
    search_fields = ("email", "meeting__title")
    readonly_fields = ("sent_at",)
