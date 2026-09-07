from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AcademicYear, Term
from .serializers import AcademicYearSerializer, TermSerializer


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))


class SetCurrentAcademicYearView(APIView):
    permission_classes = [AdminOnly]

    def post(self, request, pk):
        year = AcademicYear.objects.select_related("school").get(pk=pk)
        if not year.is_active:
            return Response({"detail": "An inactive academic year cannot be current."}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            AcademicYear.objects.filter(school=year.school, is_current=True).exclude(pk=year.pk).update(is_current=False)
            year.is_current = True
            year.save(update_fields=["is_current", "updated_at"])
        return Response(AcademicYearSerializer(year).data)


class SetCurrentTermView(APIView):
    permission_classes = [AdminOnly]

    def post(self, request, pk):
        term = Term.objects.select_related("academic_year").get(pk=pk)
        if not term.is_active or not term.academic_year.is_active:
            return Response({"detail": "Only active terms in an active academic year can be current."}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            Term.objects.filter(academic_year=term.academic_year, is_current=True).exclude(pk=term.pk).update(is_current=False)
            term.is_current = True
            term.save(update_fields=["is_current", "updated_at"])
        return Response(TermSerializer(term).data)
