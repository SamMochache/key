from django.db.models import Count, Q, Prefetch
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .models import AcademicYear, CambridgeStage, Classroom, ClassroomTeacherAssignment, Curriculum, MontessoriLevel, StageSubject, Subject, Term
from .serializers import (
    AcademicYearSerializer,
    CambridgeStageSerializer,
    ClassroomSerializer,
    CurriculumSerializer,
    MontessoriLevelSerializer,
    StageSubjectSerializer,
    SubjectSerializer,
    TermSerializer,
)


def user_school(user):
    teacher_profile = getattr(user, "teacher_profile", None)
    if teacher_profile is not None:
        return teacher_profile.school
    student_profile = getattr(user, "student_profile", None)
    if student_profile is not None:
        return student_profile.school
    return None


def is_admin(user):
    return bool(user.is_staff or user.is_superuser)


class AcademicsAccessPermission(permissions.BasePermission):
    message = "You do not have permission to access academic data."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return is_admin(request.user) or user_school(request.user) is not None
        return is_admin(request.user)


class SchoolScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [AcademicsAccessPermission]
    school_field = "school"

    def filter_school(self, queryset):
        if is_admin(self.request.user):
            return queryset
        school = user_school(self.request.user)
        return queryset.filter(**{self.school_field: school})


class AcademicYearViewSet(SchoolScopedViewSet):
    serializer_class = AcademicYearSerializer

    def get_queryset(self):
        queryset = AcademicYear.objects.select_related("school").all()
        queryset = self.filter_school(queryset)
        if self.request.query_params.get("current") in {"1", "true", "True"}:
            queryset = queryset.filter(is_current=True)
        return queryset

    def perform_create(self, serializer):
        school = serializer.validated_data.get("school")
        if not is_admin(self.request.user):
            school = user_school(self.request.user)
        serializer.save(school=school)


class TermViewSet(SchoolScopedViewSet):
    serializer_class = TermSerializer

    def get_queryset(self):
        queryset = Term.objects.select_related("academic_year", "academic_year__school").all()
        if not is_admin(self.request.user):
            queryset = queryset.filter(academic_year__school=user_school(self.request.user))
        if self.request.query_params.get("current") in {"1", "true", "True"}:
            queryset = queryset.filter(is_current=True)
        return queryset


class CurriculumViewSet(viewsets.ModelViewSet):
    serializer_class = CurriculumSerializer
    permission_classes = [AcademicsAccessPermission]

    def get_queryset(self):
        return Curriculum.objects.annotate(subject_count=Count("subjects", distinct=True)).all()


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [AcademicsAccessPermission]

    def get_queryset(self):
        queryset = Subject.objects.select_related("curriculum").all()
        curriculum = self.request.query_params.get("curriculum")
        if curriculum:
            queryset = queryset.filter(curriculum_id=curriculum)
        if self.request.query_params.get("active") in {"1", "true", "True"}:
            queryset = queryset.filter(is_active=True)
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))
        return queryset


class CambridgeStageViewSet(viewsets.ModelViewSet):
    serializer_class = CambridgeStageSerializer
    permission_classes = [AcademicsAccessPermission]

    def get_queryset(self):
        queryset = CambridgeStage.objects.all()
        if self.request.query_params.get("active") in {"1", "true", "True"}:
            queryset = queryset.filter(is_active=True)
        return queryset


class MontessoriLevelViewSet(viewsets.ModelViewSet):
    serializer_class = MontessoriLevelSerializer
    permission_classes = [AcademicsAccessPermission]

    def get_queryset(self):
        queryset = MontessoriLevel.objects.all()
        if self.request.query_params.get("active") in {"1", "true", "True"}:
            queryset = queryset.filter(is_active=True)
        return queryset


class StageSubjectViewSet(viewsets.ModelViewSet):
    serializer_class = StageSubjectSerializer
    permission_classes = [AcademicsAccessPermission]

    def get_queryset(self):
        queryset = StageSubject.objects.select_related("cambridge_stage", "subject").all()
        stage = self.request.query_params.get("stage")
        if stage:
            queryset = queryset.filter(cambridge_stage_id=stage)
        if self.request.query_params.get("active") in {"1", "true", "True"}:
            queryset = queryset.filter(is_active=True)
        return queryset


class ClassroomViewSet(SchoolScopedViewSet):
    serializer_class = ClassroomSerializer

    def get_queryset(self):
        queryset = (
            Classroom.objects
            .select_related(
                "school", "academic_year", "term", "cambridge_stage", "montessori_level"
            )
            .prefetch_related(
                Prefetch(
                    "teacher_assignments",
                    queryset=ClassroomTeacherAssignment.objects.filter(
                        role=ClassroomTeacherAssignment.Role.PRIMARY,
                        is_active=True,
                    ).select_related("teacher__user"),
                )
            )
            .annotate(
                student_count=Count(
                    "enrollments__student",
                    filter=Q(enrollments__status="ENROLLED"),
                    distinct=True,
                ),
                subject_count=Count(
                    "cambridge_stage__stage_subjects",
                    filter=Q(cambridge_stage__stage_subjects__is_active=True),
                    distinct=True,
                ),
            )
            .all()
        )
        queryset = self.filter_school(queryset)
        academic_year = self.request.query_params.get("academic_year")
        term = self.request.query_params.get("term")
        stage = self.request.query_params.get("stage")
        search = self.request.query_params.get("search", "").strip()
        if academic_year:
            queryset = queryset.filter(academic_year_id=academic_year)
        if term:
            queryset = queryset.filter(term_id=term)
        if stage:
            queryset = queryset.filter(cambridge_stage_id=stage)
        if self.request.query_params.get("active") in {"1", "true", "True"}:
            queryset = queryset.filter(is_active=True)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))
        return queryset

    def perform_create(self, serializer):
        school = serializer.validated_data.get("school")
        if not is_admin(self.request.user):
            school = user_school(self.request.user)
        serializer.save(school=school)

    def destroy(self, request, *args, **kwargs):
        classroom = self.get_object()
        classroom.is_active = False
        classroom.save(update_fields=["is_active", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
