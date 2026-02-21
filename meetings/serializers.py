from django.utils import timezone
from rest_framework import serializers
from .models import Meeting, Participant, MeetingNotification
from .utils.conflict_detector import check_participants_conflicts


# ──────────────────────────────────────────────
# Participant
# ──────────────────────────────────────────────

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = [
            "id", "meeting", "user", "email", "name",
            "status", "invited_at", "responded_at",
        ]
        read_only_fields = ["id", "meeting", "invited_at", "responded_at"]


class ParticipantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ["email", "name", "user"]

    def validate_email(self, value):
        return value.lower().strip()


class ParticipantStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Participant.STATUS_CHOICES,
        help_text="New participation status.",
    )


# ──────────────────────────────────────────────
# Meeting
# ──────────────────────────────────────────────

class MeetingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    participant_count = serializers.SerializerMethodField()
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Meeting
        fields = [
            "id", "title", "location", "start_time", "end_time",
            "status", "participant_count", "created_by_email", "duration_minutes",
        ]

    def get_participant_count(self, obj):
        return obj.participants.count()


class MeetingDetailSerializer(serializers.ModelSerializer):
    """Full meeting serializer with nested participants."""
    participants = ParticipantSerializer(many=True, read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)

    class Meta:
        model = Meeting
        fields = [
            "id", "title", "description", "location",
            "start_time", "end_time", "status",
            "created_by", "created_by_email",
            "participants", "duration_minutes", "is_upcoming",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]


class MeetingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating / updating meetings."""
    participants = ParticipantCreateSerializer(many=True, required=False)

    class Meta:
        model = Meeting
        fields = [
            "title", "description", "location",
            "start_time", "end_time", "status", "participants",
        ]

    def validate(self, attrs):
        start = attrs.get("start_time")
        end = attrs.get("end_time")

        if start and end and start >= end:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time."}
            )
        if start and start < timezone.now():
            raise serializers.ValidationError(
                {"start_time": "Start time cannot be in the past."}
            )
        return attrs

    def create(self, validated_data):
        participants_data = validated_data.pop("participants", [])
        meeting = Meeting.objects.create(**validated_data)
        for p_data in participants_data:
            Participant.objects.get_or_create(
                meeting=meeting, email=p_data["email"],
                defaults={"name": p_data.get("name", ""), "user": p_data.get("user")},
            )
        return meeting

    def update(self, instance, validated_data):
        validated_data.pop("participants", None)  # handled separately
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ConflictCheckSerializer(serializers.Serializer):
    """
    Request body for the conflict-check endpoint.
    POST /api/meetings/check-conflicts/
    """
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    participant_emails = serializers.ListField(
        child=serializers.EmailField(), min_length=1
    )
    exclude_meeting_id = serializers.UUIDField(required=False, allow_null=True)

    def validate(self, attrs):
        if attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError("end_time must be after start_time.")
        return attrs


# ──────────────────────────────────────────────
# Notifications
# ──────────────────────────────────────────────

class MeetingNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingNotification
        fields = [
            "id", "meeting", "email", "notification_type",
            "message", "is_sent", "sent_at",
        ]
        read_only_fields = fields
