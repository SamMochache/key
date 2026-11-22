from datetime import date, time

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import (
    AcademicYear,
    CambridgeStage,
    Classroom,
    Curriculum,
    Programme,
    Subject,
    Term,
)
from apps.identity.models import User
from apps.schools.models import School
from apps.teachers.models import Department, Teacher, TeacherSubject
from apps.timetables.models import Period, Timetable, TimetableEntry
from core.constants.timetable import TimetableStatus, WeekDay


class TimetableLessonSyncTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="Lesson Sync School",
            short_name="SYNC",
            city="Nairobi",
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPassword123!",
        )
        self.teacher_user = User.objects.create_user(
            email="teacher@example.com",
            password="StrongPassword123!",
            first_name="Test",
            last_name="Teacher",
        )
        self.other_teacher_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPassword123!",
            first_name="Other",
            last_name="Teacher",
        )
        department = Department.objects.create(
            school=self.school,
            name="Primary",
            code="PRI",
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            school=self.school,
            employee_number="T-001",
            employment_type="FULL_TIME",
            employment_date=date(2025, 1, 1),
            department=department,
        )
        self.other_teacher = Teacher.objects.create(
            user=self.other_teacher_user,
            school=self.school,
            employee_number="T-002",
            employment_type="FULL_TIME",
            employment_date=date(2025, 1, 1),
            department=department,
        )

        curriculum = Curriculum.objects.create(name="Cambridge Primary", version="1.0")
        programme = Programme.objects.create(curriculum=curriculum, name="Cambridge Primary")
        stage = CambridgeStage.objects.create(
            programme=programme,
            name="Stage 3",
            stage_number=3,
            display_order=3,
        )
        subject = Subject.objects.create(
            curriculum=curriculum,
            name="Mathematics",
            code="MATH",
        )
        self.academic_year = AcademicYear.objects.create(
            school=self.school,
            name="2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            is_current=True,
        )
        self.term = Term.objects.create(
            academic_year=self.academic_year,
            term_number=1,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 30),
            is_current=True,
        )
        self.classroom = Classroom.objects.create(
            school=self.school,
            academic_year=self.academic_year,
            term=self.term,
            cambridge_stage=stage,
            name="Ocean",
            code="OCEAN",
            capacity=25,
        )
        self.assignment = TeacherSubject.objects.create(
            teacher=self.teacher,
            subject=subject,
            classroom=self.classroom,
            academic_year=self.academic_year,
            term=self.term,
            start_date=date(2026, 11, 1),
            is_active=True,
        )
        self.period = Period.objects.create(
            school=self.school,
            name="Period 1",
            sequence=1,
            start_time=time(8, 0),
            end_time=time(8, 45),
        )
        self.timetable = Timetable.objects.create(
            school=self.school,
            academic_year=self.academic_year,
            term=self.term,
            name="Term 1 Timetable",
            version=1,
            status=TimetableStatus.PUBLISHED,
            effective_from=date(2026, 11, 1),
        )
        self.entries = {
            weekday: TimetableEntry.objects.create(
                timetable=self.timetable,
                weekday=weekday,
                period=self.period,
                classroom=self.classroom,
                teacher_subject=self.assignment,
            )
            for weekday in (WeekDay.MONDAY, WeekDay.TUESDAY, WeekDay.FRIDAY)
        }
        self.sync_url = reverse("lesson-sync-day")
        self.list_url = reverse("lesson-list")

    def sync_as(self, user, lesson_date):
        self.client.force_authenticate(user)
        return self.client.post(
            self.sync_url,
            {"lesson_date": lesson_date.isoformat()},
            format="json",
        )

    def test_admin_can_publish_timetable_and_teacher_syncs_its_monday_entry(self):
        self.timetable.status = TimetableStatus.DRAFT
        self.timetable.save(update_fields=["status", "updated_at"])

        self.client.force_authenticate(self.admin)
        publish_response = self.client.post(
            reverse("timetable-publish", kwargs={"pk": self.timetable.pk}),
            {},
            format="json",
        )

        self.assertEqual(publish_response.status_code, status.HTTP_200_OK)
        self.assertEqual(publish_response.data["status"], TimetableStatus.PUBLISHED)
        self.assertEqual(self.timetable.entries.count(), 3)

        sync_response = self.sync_as(self.teacher_user, date(2026, 11, 23))
        self.assertEqual(sync_response.status_code, status.HTTP_200_OK)
        self.assertEqual(sync_response.data["created"], 1)
        self.assertEqual(sync_response.data["lessons"][0]["weekday"], WeekDay.MONDAY)

    def test_entry_outside_term_dates_does_not_generate_lesson(self):
        response = self.sync_as(self.teacher_user, date(2026, 12, 7))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["created"], 0)
        self.assertEqual(response.data["lessons"], [])

    def test_inactive_classroom_does_not_generate_lesson(self):
        self.classroom.is_active = False
        self.classroom.save(update_fields=["is_active", "updated_at"])

        response = self.sync_as(self.teacher_user, date(2026, 11, 23))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["created"], 0)
        self.assertEqual(response.data["lessons"], [])

    def test_monday_timetable_entry_generates_monday_lesson_idempotently(self):
        monday = date(2026, 11, 23)

        first = self.sync_as(self.teacher_user, monday)
        second = self.sync_as(self.teacher_user, monday)

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data["created"], 1)
        self.assertEqual(len(first.data["lessons"]), 1)
        self.assertEqual(first.data["lessons"][0]["weekday"], WeekDay.MONDAY)
        self.assertEqual(first.data["lessons"][0]["lesson_date"], "2026-11-23")
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(second.data["created"], 0)
        self.assertEqual(second.data["lessons"], first.data["lessons"])

    def test_tuesday_and_friday_entries_match_their_calendar_dates(self):
        for lesson_date, expected_weekday in (
            (date(2026, 11, 24), WeekDay.TUESDAY),
            (date(2026, 11, 27), WeekDay.FRIDAY),
        ):
            with self.subTest(lesson_date=lesson_date):
                response = self.sync_as(self.teacher_user, lesson_date)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["created"], 1)
                self.assertEqual(response.data["lessons"][0]["weekday"], expected_weekday)

    def test_monday_entry_is_not_generated_for_friday_date(self):
        self.entries[WeekDay.FRIDAY].delete()

        response = self.sync_as(self.teacher_user, date(2026, 11, 27))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["created"], 0)
        self.assertEqual(response.data["lessons"], [])

    def test_unpublished_timetable_does_not_generate_lessons(self):
        self.timetable.status = TimetableStatus.DRAFT
        self.timetable.save(update_fields=["status", "updated_at"])

        response = self.sync_as(self.teacher_user, date(2026, 11, 23))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["created"], 0)
        self.assertEqual(response.data["lessons"], [])

    def test_assignment_must_be_active_on_lesson_date(self):
        self.assignment.end_date = date(2026, 11, 20)
        self.assignment.save(update_fields=["end_date", "updated_at"])

        response = self.sync_as(self.teacher_user, date(2026, 11, 23))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["created"], 0)

    def test_teacher_can_list_own_generated_lesson_but_not_another_teachers(self):
        monday = date(2026, 11, 23)
        created = self.sync_as(self.teacher_user, monday)
        self.assertEqual(created.data["created"], 1)

        self.client.force_authenticate(self.teacher_user)
        own_lessons = self.client.get(self.list_url, {"lesson_date": monday.isoformat()})
        self.assertEqual(own_lessons.status_code, status.HTTP_200_OK)
        self.assertEqual(own_lessons.data["count"], 1)

        self.client.force_authenticate(self.other_teacher_user)
        other_lessons = self.client.get(self.list_url, {"lesson_date": monday.isoformat()})
        self.assertEqual(other_lessons.status_code, status.HTTP_200_OK)
        self.assertEqual(other_lessons.data["count"], 0)
