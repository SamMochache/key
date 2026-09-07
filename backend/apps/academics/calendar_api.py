from django.db.models import Q
from rest_framework import permissions, serializers, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import CalendarEvent
from .views import is_admin, user_school


class CalendarEventSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    term_number = serializers.IntegerField(source="term.term_number", read_only=True, allow_null=True)

    class Meta:
        model = CalendarEvent
        fields = ("id", "school", "school_name", "academic_year", "academic_year_name", "term", "term_number", "title", "event_type", "start_at", "end_at", "all_day", "location", "description", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "school_name", "academic_year_name", "term_number", "created_at", "updated_at")

    def validate(self, attrs):
        start_at = attrs.get("start_at", getattr(self.instance, "start_at", None))
        end_at = attrs.get("end_at", getattr(self.instance, "end_at", None))
        if start_at and end_at and end_at < start_at:
            raise serializers.ValidationError({"end_at": "End time cannot be before start time."})
        academic_year = attrs.get("academic_year", getattr(self.instance, "academic_year", None))
        school = attrs.get("school", getattr(self.instance, "school", None))
        term = attrs.get("term", getattr(self.instance, "term", None))
        if academic_year and school and academic_year.school_id != school.id:
            raise serializers.ValidationError({"academic_year": "Academic year must belong to the selected institution."})
        if term and academic_year and term.academic_year_id != academic_year.id:
            raise serializers.ValidationError({"term": "Term must belong to the selected academic year."})
        if term and school and term.academic_year.school_id != school.id:
            raise serializers.ValidationError({"term": "Term must belong to the selected institution."})
        return attrs


class CalendarAccessPermission(permissions.BasePermission):
    message = "You do not have permission to access calendar data."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return is_admin(request.user) or user_school(request.user) is not None
        return is_admin(request.user)


class CalendarEventViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarEventSerializer
    permission_classes = [CalendarAccessPermission]

    def get_queryset(self):
        queryset = CalendarEvent.objects.select_related("school", "academic_year", "term").all()
        if not is_admin(self.request.user):
            school = user_school(self.request.user)
            queryset = queryset.filter(school=school, is_active=True) if school else queryset.none()
        else:
            school_id = self.request.query_params.get("school")
            if school_id:
                queryset = queryset.filter(school_id=school_id)
        for param, field in (("academic_year", "academic_year_id"), ("term", "term_id"), ("event_type", "event_type")):
            value = self.request.query_params.get(param)
            if value:
                queryset = queryset.filter(**{field: value})
        if self.request.query_params.get("active") in {"1", "true", "True"}:
            queryset = queryset.filter(is_active=True)
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        search = self.request.query_params.get("search", "").strip()
        if start:
            queryset = queryset.filter(end_at__gte=start)
        if end:
            queryset = queryset.filter(start_at__lte=end)
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search) | Q(location__icontains=search))
        return queryset

    def perform_create(self, serializer):
        school = serializer.validated_data.get("school") if is_admin(self.request.user) else user_school(self.request.user)
        if school is None:
            raise serializers.ValidationError({"school": "A valid institution is required."})
        serializer.save(school=school)

    def perform_update(self, serializer):
        if not is_admin(self.request.user):
            raise PermissionDenied("Only administrators can manage calendar events.")
        serializer.save()

    def perform_destroy(self, instance):
        if not is_admin(self.request.user):
            raise PermissionDenied("Only administrators can manage calendar events.")
        instance.delete()
