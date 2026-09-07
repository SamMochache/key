from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.assessments.permissions import UserRole, get_user_role, get_user_school
from apps.enrollment.models import Enrollment

from .models import Artifact, Portfolio, PortfolioItem
from .serializers import ArtifactSerializer, PortfolioItemSerializer, PortfolioSerializer


class PortfolioAccessMixin:
    permission_classes = [permissions.IsAuthenticated]

    def scoped_portfolios(self):
        role = get_user_role(self.request.user)
        if role == UserRole.ADMIN:
            return Portfolio.objects.all()
        school = get_user_school(self.request.user)
        if school is None:
            raise PermissionDenied("Your account is not associated with an institution.")
        qs = Portfolio.objects.filter(student__school=school)
        if role == UserRole.STUDENT:
            qs = qs.filter(student__user=self.request.user)
        return qs


class PortfolioViewSet(PortfolioAccessMixin, viewsets.ModelViewSet):
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        return self.scoped_portfolios().select_related("student__user", "student__school")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"].portfolio_role = get_user_role(self.request.user)
        return context

    def perform_create(self, serializer):
        role = get_user_role(self.request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER}:
            raise PermissionDenied("Only staff can create portfolios for learners.")
        serializer.save()

    @action(detail=False, methods=["get"])
    def mine(self, request):
        portfolio = self.scoped_portfolios().filter(student__user=request.user).first()
        if portfolio is None:
            student = getattr(request.user, "student_profile", None)
            if student is None:
                raise PermissionDenied("Student profile not found.")
            portfolio = Portfolio.objects.create(student=student)
        return Response(self.get_serializer(portfolio).data)


class PortfolioItemViewSet(PortfolioAccessMixin, viewsets.ModelViewSet):
    serializer_class = PortfolioItemSerializer

    def get_queryset(self):
        qs = PortfolioItem.objects.filter(portfolio__in=self.scoped_portfolios()).select_related(
            "portfolio__student__user", "assessment_submission__assessment", "lesson_session"
        ).prefetch_related("artifacts")
        item_type = self.request.query_params.get("item_type")
        search = self.request.query_params.get("search")
        portfolio = self.request.query_params.get("portfolio")
        if item_type:
            qs = qs.filter(item_type=item_type)
        if portfolio:
            qs = qs.filter(portfolio_id=portfolio)
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        return qs

    def perform_create(self, serializer):
        role = get_user_role(self.request.user)
        if role not in {UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT}:
            raise PermissionDenied("You do not have permission to add portfolio items.")
        serializer.save()


class ArtifactViewSet(PortfolioAccessMixin, viewsets.ModelViewSet):
    serializer_class = ArtifactSerializer

    def get_queryset(self):
        return Artifact.objects.filter(
            portfolio_item__portfolio__in=self.scoped_portfolios()
        ).select_related("portfolio_item__portfolio__student__user")

    def perform_create(self, serializer):
        item_id = self.request.data.get("portfolio_item")
        try:
            item = PortfolioItem.objects.get(id=item_id)
        except (PortfolioItem.DoesNotExist, ValueError):
            raise PermissionDenied("Portfolio item not found.")
        if not self.scoped_portfolios().filter(id=item.portfolio_id).exists():
            raise PermissionDenied("You cannot add an artifact to this portfolio.")
        serializer.save()
