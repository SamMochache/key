from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.academics.models import (
    AcademicYear,
    CalendarEvent,
    CambridgeStage,
    Classroom,
    ClassroomTeacherAssignment,
    Curriculum,
    MontessoriLevel,
    Programme,
    StageSubject,
    Subject,
    Term,
)
from apps.assessments.models import Assessment, AssessmentEvaluation, AssessmentSubmission
from apps.attendance.models import AttendanceRecord, AttendanceRegister
from apps.communication.models import CommunicationMessage
from apps.enrollment.models import Enrollment
from apps.identity.models import User
from apps.lessons.models import LessonSession
from apps.notifications.models import Notification
from apps.parents.models import Parent, ParentStudentRelationship
from apps.portfolio.models import Portfolio, PortfolioItem
from apps.schools.models import School, SchoolAdministrator
from apps.students.models import Student
from apps.teachers.models import Department, Teacher, TeacherSubject
from apps.timetables.models import Period, Timetable, TimetableEntry


class Command(BaseCommand):
    help = "Seed the database with deterministic demo data for two schools."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Remove the seeded demo records before recreating them.",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_demo is development-only. Run it with DEBUG=True.")

        with transaction.atomic():
            if options["reset"]:
                self.reset_demo()
            summary = self.seed()

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        for label, value in summary.items():
            self.stdout.write(f"{label}: {value}")

    def reset_demo(self):
        school_codes = ["KEY", "GVA"]
        schools = School.objects.filter(short_name__in=school_codes)
        school_users = User.objects.filter(
            email__in=[
                "systemadmin@key.test",
                "admin@keyinternational.test",
                "admin@greenvalley.test",
            ]
        ) | User.objects.filter(email__endswith="@keyinternational.test") | User.objects.filter(
            email__endswith="@greenvalley.test"
        ) | User.objects.filter(email__endswith="@student.keyinternational.test") | User.objects.filter(
            email__endswith="@student.greenvalley.test"
        )

        assessments = Assessment.objects.filter(teacher__school__in=schools)
        submissions = AssessmentSubmission.objects.filter(assessment__in=assessments)
        AssessmentEvaluation.objects.filter(submission__in=submissions).delete()
        submissions.delete()
        assessments.delete()

        lesson_sessions = LessonSession.objects.filter(timetable_entry__timetable__school__in=schools)
        attendance_registers = AttendanceRegister.objects.filter(lesson_session__in=lesson_sessions)
        AttendanceRecord.objects.filter(attendance_register__in=attendance_registers).delete()
        attendance_registers.delete()

        PortfolioItem.objects.filter(portfolio__student__school__in=schools).delete()
        Portfolio.objects.filter(student__school__in=schools).delete()
        CommunicationMessage.objects.filter(school__in=schools).delete()
        Notification.objects.filter(school__in=schools).delete()

        lesson_sessions.delete()
        TimetableEntry.objects.filter(timetable__school__in=schools).delete()
        Timetable.objects.filter(school__in=schools).delete()
        TeacherSubject.objects.filter(teacher__school__in=schools).delete()
        ClassroomTeacherAssignment.objects.filter(classroom__school__in=schools).delete()
        Enrollment.objects.filter(student__school__in=schools).delete()
        ParentStudentRelationship.objects.filter(parent__school__in=schools).delete()
        Parent.objects.filter(school__in=schools).delete()
        Student.objects.filter(school__in=schools).delete()
        Teacher.objects.filter(school__in=schools).delete()
        Period.objects.filter(school__in=schools).delete()
        CalendarEvent.objects.filter(school__in=schools).delete()
        Classroom.objects.filter(school__in=schools).delete()
        Term.objects.filter(academic_year__school__in=schools).delete()
        AcademicYear.objects.filter(school__in=schools).delete()
        SchoolAdministrator.objects.filter(school__in=schools).delete()
        Department.objects.filter(school__in=schools).delete()
        schools.delete()
        school_users.delete()

    def user(self, email, first_name, last_name, password="TestPass123!", **extra):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": extra.get("phone_number", ""),
                "timezone": "Africa/Nairobi",
                "status": "ACTIVE",
                "is_active": True,
                "is_staff": extra.get("is_staff", False),
            },
        )
        if created:
            user.set_password(password)
        changed = False
        for field, value in {
            "first_name": first_name,
            "last_name": last_name,
            "is_active": True,
            "is_staff": extra.get("is_staff", user.is_staff),
        }.items():
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed = True
        if created or changed:
            user.save()
        return user

    def seed(self):
        system_admin = self.user(
            "systemadmin@key.test",
            "System",
            "Administrator",
            is_staff=True,
        )
        system_admin.is_superuser = True
        system_admin.is_staff = True
        system_admin.save(update_fields=["is_superuser", "is_staff"])

        school_specs = {
            "KEY": {
                "name": "Key International School",
                "email": "admin@keyinternational.test",
                "phone": "+254700100001",
                "address": "Riverside Drive",
                "city": "Nairobi",
            },
            "GVA": {
                "name": "Green Valley Academy",
                "email": "admin@greenvalley.test",
                "phone": "+254700100002",
                "address": "Kiambu Road",
                "city": "Kiambu",
            },
        }
        schools = {}
        for code, spec in school_specs.items():
            schools[code], _ = School.objects.update_or_create(
                short_name=code,
                defaults={
                    "name": spec["name"],
                    "email": spec["email"],
                    "phone_number": spec["phone"],
                    "address": spec["address"],
                    "city": spec["city"],
                    "country": "Kenya",
                    "timezone": "Africa/Nairobi",
                    "is_active": True,
                },
            )

        admin_users = {}
        for code, email, first_name, last_name in [
            ("KEY", "admin@keyinternational.test", "Alice", "Mwangi"),
            ("GVA", "admin@greenvalley.test", "Brian", "Kamau"),
        ]:
            admin_users[code] = self.user(email, first_name, last_name, is_staff=True)
            SchoolAdministrator.objects.update_or_create(
                user=admin_users[code],
                defaults={"school": schools[code], "is_active": True},
            )

        departments = {}
        for code, school in schools.items():
            departments[(code, "PRI")], _ = Department.objects.get_or_create(
                school=school, code="PRI", defaults={"name": "Primary"}
            )
            departments[(code, "SEC")], _ = Department.objects.get_or_create(
                school=school, code="SEC", defaults={"name": "Secondary"}
            )

        cambridge_curriculum, _ = Curriculum.objects.get_or_create(
            name="Cambridge International",
            defaults={
                "description": "Cambridge international curriculum demo.",
                "is_active": True,
            },
        )
        Curriculum.objects.filter(pk=cambridge_curriculum.pk).update(is_active=True)
        montessori_curriculum, _ = Curriculum.objects.get_or_create(
            name="Montessori",
            defaults={"description": "Montessori curriculum demo.", "is_active": True},
        )
        Curriculum.objects.filter(pk=montessori_curriculum.pk).update(is_active=True)

        programmes = {}
        for name, display_order in [
            ("Cambridge Primary", 1),
            ("Cambridge Lower Secondary", 2),
            ("Cambridge Upper Secondary", 3),
        ]:
            programmes[name], _ = Programme.objects.update_or_create(
                curriculum=cambridge_curriculum,
                name=name,
                defaults={"display_order": display_order, "is_active": True},
            )

        stages = {}
        for name, programme_name, stage_number, display_order in [
            ("Year 4", "Cambridge Primary", 4, 4),
            ("Year 5", "Cambridge Primary", 5, 5),
            ("Year 7", "Cambridge Lower Secondary", 7, 7),
            ("Year 8", "Cambridge Lower Secondary", 8, 8),
        ]:
            stages[name], _ = CambridgeStage.objects.update_or_create(
                programme=programmes[programme_name],
                name=name,
                defaults={
                    "stage_number": stage_number,
                    "display_order": display_order,
                    "is_active": True,
                },
            )

        montessori = {}
        for name, code, minimum_age, maximum_age, display_order in [
            ("Casa", "CASA", Decimal("3.0"), Decimal("6.0"), 1),
            ("Lower Elementary", "LOWER-ELEMENTARY", Decimal("6.0"), Decimal("9.0"), 2),
        ]:
            montessori[name], _ = MontessoriLevel.objects.update_or_create(
                name=name,
                defaults={
                    "code": code,
                    "minimum_age": minimum_age,
                    "maximum_age": maximum_age,
                    "description": f"Demo Montessori level: {name}.",
                    "display_order": display_order,
                    "is_active": True,
                },
            )

        subjects = {}
        for display_order, (name, code) in enumerate(
            [
                ("English", "ENG"),
                ("Mathematics", "MATH"),
                ("Science", "SCI"),
                ("Global Perspectives", "GP"),
                ("Computing", "COMP"),
                ("Art & Design", "ART"),
                ("Physical Education", "PE"),
                ("Biology", "BIO"),
                ("Physics", "PHY"),
                ("Chemistry", "CHEM"),
                ("Computer Science", "CS"),
                ("Geography", "GEO"),
                ("History", "HIST"),
            ],
            start=1,
        ):
            subjects[name], _ = Subject.objects.update_or_create(
                curriculum=cambridge_curriculum,
                name=name,
                defaults={
                    "code": code,
                    "description": f"Demo {name} subject.",
                    "is_core": name in {"English", "Mathematics", "Science"},
                    "display_order": display_order,
                    "is_active": True,
                },
            )

        stage_subject_names = [
            "English",
            "Mathematics",
            "Science",
            "Global Perspectives",
            "Computing",
            "Art & Design",
            "Physical Education",
        ]
        for stage in stages.values():
            for display_order, subject_name in enumerate(stage_subject_names, start=1):
                StageSubject.objects.update_or_create(
                    cambridge_stage=stage,
                    subject=subjects[subject_name],
                    defaults={
                        "weekly_lessons": 5
                        if subject_name in {"English", "Mathematics", "Science"}
                        else 2,
                        "is_core": subject_name in {"English", "Mathematics", "Science"},
                        "display_order": display_order,
                        "is_active": True,
                    },
                )

        academic_years = {}
        terms = {}
        classrooms = {}
        for code, school in schools.items():
            academic_years[code], _ = AcademicYear.objects.update_or_create(
                school=school,
                name="2026 Academic Year",
                defaults={
                    "start_date": date(2026, 1, 5),
                    "end_date": date(2026, 12, 4),
                    "is_current": True,
                    "is_active": True,
                },
            )
            for number, start, end in [
                (1, date(2026, 1, 5), date(2026, 4, 2)),
                (2, date(2026, 5, 4), date(2026, 8, 7)),
                (3, date(2026, 8, 31), date(2026, 12, 4)),
            ]:
                terms[(code, number)], _ = Term.objects.update_or_create(
                    academic_year=academic_years[code],
                    term_number=number,
                    defaults={
                        "start_date": start,
                        "end_date": end,
                        "is_current": number == 1,
                        "is_active": True,
                    },
                )
            for stage_name in ["Year 4", "Year 5", "Year 7"]:
                classrooms[(code, stage_name)], _ = Classroom.objects.update_or_create(
                    school=school,
                    academic_year=academic_years[code],
                    code=f"{code}-{stage_name.replace(' ', '')}-2026",
                    defaults={
                        "term": terms[(code, 1)],
                        "name": stage_name,
                        "cambridge_stage": stages[stage_name],
                        "montessori_level": None,
                        "capacity": 30,
                        "is_active": True,
                    },
                )

        teacher_specs = [
            ("KEY", "james.otieno@keyinternational.test", "James", "Otieno", "T001", "PRI", "Mathematics", "Year 4"),
            ("KEY", "mary.wanjiku@keyinternational.test", "Mary", "Wanjiku", "T002", "PRI", "English", "Year 4"),
            ("KEY", "daniel.kiptoo@keyinternational.test", "Daniel", "Kiptoo", "T003", "SEC", "Science", "Year 7"),
            ("GVA", "peter.maina@greenvalley.test", "Peter", "Maina", "T001", "PRI", "Mathematics", "Year 4"),
            ("GVA", "grace.njeri@greenvalley.test", "Grace", "Njeri", "T002", "PRI", "English", "Year 4"),
            ("GVA", "samuel.kariuki@greenvalley.test", "Samuel", "Kariuki", "T003", "SEC", "Science", "Year 7"),
        ]
        teachers_by_school = {"KEY": [], "GVA": []}
        teacher_subjects = []
        teacher_subject_by_key = {}
        for code, email, first, last, employee, dept, subject_name, classroom_name in teacher_specs:
            user = self.user(email, first, last)
            teacher, _ = Teacher.objects.update_or_create(
                user=user,
                defaults={
                    "school": schools[code],
                    "employee_number": employee,
                    "employment_type": "FULL_TIME",
                    "employment_date": date(2024, 1, 8),
                    "status": "ACTIVE",
                    "department": departments[(code, dept)],
                },
            )
            teachers_by_school[code].append(teacher)
            assignment, _ = TeacherSubject.objects.update_or_create(
                teacher=teacher,
                subject=subjects[subject_name],
                classroom=classrooms[(code, classroom_name)],
                academic_year=academic_years[code],
                term=terms[(code, 1)],
                defaults={
                    "role": "LEAD",
                    "start_date": date(2026, 1, 5),
                    "end_date": date(2026, 12, 4),
                    "is_active": True,
                },
            )
            teacher_subjects.append(assignment)
            teacher_subject_by_key[(code, classroom_name, subject_name)] = assignment

        # Mary/Grace also teach English in Year 5 so the seeded Tuesday timetable
        # has a valid teacher-subject assignment instead of pointing at a missing key.
        for code, teacher_index in [("KEY", 1), ("GVA", 1)]:
            teacher = teachers_by_school[code][teacher_index]
            assignment, _ = TeacherSubject.objects.update_or_create(
                teacher=teacher,
                subject=subjects["English"],
                classroom=classrooms[(code, "Year 5")],
                academic_year=academic_years[code],
                term=terms[(code, 1)],
                defaults={
                    "role": "LEAD",
                    "start_date": date(2026, 1, 5),
                    "end_date": date(2026, 12, 4),
                    "is_active": True,
                },
            )
            teacher_subjects.append(assignment)
            teacher_subject_by_key[(code, "Year 5", "English")] = assignment

        assignment_specs = [
            ("KEY", "Year 4", 0, "PRIMARY"),
            ("KEY", "Year 4", 1, "ASSISTANT"),
            ("KEY", "Year 5", 0, "PRIMARY"),
            ("KEY", "Year 7", 2, "PRIMARY"),
            ("GVA", "Year 4", 0, "PRIMARY"),
            ("GVA", "Year 4", 1, "ASSISTANT"),
            ("GVA", "Year 5", 0, "PRIMARY"),
            ("GVA", "Year 7", 2, "PRIMARY"),
        ]
        for code, classroom_name, teacher_index, role in assignment_specs:
            ClassroomTeacherAssignment.objects.update_or_create(
                classroom=classrooms[(code, classroom_name)],
                teacher=teachers_by_school[code][teacher_index],
                role=role,
                defaults={"is_active": True},
            )

        student_specs = [
            ("KEY", "brian.onyango@student.keyinternational.test", "Brian", "Onyango", "KEY001", date(2016, 3, 12), "M", "Year 4"),
            ("KEY", "faith.wambui@student.keyinternational.test", "Faith", "Wambui", "KEY002", date(2015, 7, 22), "F", "Year 5"),
            ("KEY", "kevin.kimani@student.keyinternational.test", "Kevin", "Kimani", "KEY003", date(2014, 11, 4), "M", "Year 7"),
            ("GVA", "linda.njeri@student.greenvalley.test", "Linda", "Njeri", "GVA001", date(2016, 2, 18), "F", "Year 4"),
            ("GVA", "mark.kiprotich@student.greenvalley.test", "Mark", "Kiprotich", "GVA002", date(2015, 6, 30), "M", "Year 5"),
            ("GVA", "sharon.akinyi@student.greenvalley.test", "Sharon", "Akinyi", "GVA003", date(2014, 9, 16), "F", "Year 7"),
        ]
        students = {}
        enrollments = {}
        for code, email, first, last, admission, dob, gender, classroom_name in student_specs:
            user = self.user(email, first, last)
            student, _ = Student.objects.update_or_create(
                user=user,
                defaults={
                    "school": schools[code],
                    "admission_number": admission,
                    "admission_date": date(2025, 1, 6),
                    "date_of_birth": dob,
                    "gender": gender,
                    "nationality": "Kenyan",
                    "is_active": True,
                },
            )
            students[admission] = student
            enrollment, _ = Enrollment.objects.update_or_create(
                student=student,
                academic_year=academic_years[code],
                term=terms[(code, 1)],
                defaults={
                    "classroom": classrooms[(code, classroom_name)],
                    "status": "ENROLLED",
                    "enrollment_date": date(2026, 1, 5),
                    "remarks": "Seeded demo enrollment.",
                },
            )
            enrollments[admission] = enrollment

        parent_specs = [
            ("KEY", "parent.onyango@keyinternational.test", "Patrick", "Onyango", ["KEY001"]),
            ("KEY", "parent.wambui@keyinternational.test", "Jane", "Wambui", ["KEY002"]),
            ("GVA", "parent.njeri@greenvalley.test", "David", "Njeri", ["GVA001"]),
            ("GVA", "parent.kiprotich@greenvalley.test", "Susan", "Kiprotich", ["GVA002", "GVA003"]),
        ]
        for code, email, first, last, admission_numbers in parent_specs:
            parent_user = self.user(email, first, last)
            parent, _ = Parent.objects.update_or_create(
                user=parent_user,
                defaults={"school": schools[code], "is_active": True},
            )
            for admission in admission_numbers:
                ParentStudentRelationship.objects.update_or_create(
                    parent=parent,
                    student=students[admission],
                    defaults={
                        "relationship": "PARENT",
                        "can_view_reports": True,
                        "is_primary_contact": True,
                        "is_active": True,
                    },
                )

        periods = {}
        timetables = {}
        entries = []
        sessions = []
        timetable_specs = [
            ("MONDAY", "Year 4", "Mathematics", 1),
            ("TUESDAY", "Year 5", "English", 1),
            ("WEDNESDAY", "Year 7", "Science", 1),
        ]
        lesson_dates = {
            "MONDAY": date(2026, 2, 2),
            "TUESDAY": date(2026, 2, 3),
            "WEDNESDAY": date(2026, 2, 4),
        }
        for code, school in schools.items():
            for number, start, end in [
                (1, time(8, 0), time(8, 45)),
                (2, time(8, 50), time(9, 35)),
                (3, time(9, 45), time(10, 30)),
            ]:
                periods[(code, number)], _ = Period.objects.update_or_create(
                    school=school,
                    sequence=number,
                    defaults={
                        "name": f"Period {number}",
                        "start_time": start,
                        "end_time": end,
                        "is_break": False,
                    },
                )

            timetable, _ = Timetable.objects.update_or_create(
                school=school,
                academic_year=academic_years[code],
                term=terms[(code, 1)],
                version=1,
                defaults={
                    "name": "Term 1 Timetable",
                    "status": "PUBLISHED",
                    "effective_from": date(2026, 1, 5),
                    "effective_to": date(2026, 4, 2),
                },
            )
            timetables[code] = timetable

            for day, classroom_name, subject_name, period_number in timetable_specs:
                teacher_subject = teacher_subject_by_key[(code, classroom_name, subject_name)]
                entry, _ = TimetableEntry.objects.update_or_create(
                    timetable=timetable,
                    weekday=day,
                    period=periods[(code, period_number)],
                    classroom=classrooms[(code, classroom_name)],
                    defaults={
                        "teacher_subject": teacher_subject,
                        "room": "Room 1",
                    },
                )
                entries.append(entry)
                session, _ = LessonSession.objects.update_or_create(
                    timetable_entry=entry,
                    lesson_date=lesson_dates[day],
                    defaults={
                        "teacher": teacher_subject.teacher.user,
                        "status": "COMPLETED",
                        "remarks": f"{subject_name} demo lesson session.",
                    },
                )
                sessions.append(session)

        attendance_specs = [
            ("KEY001", sessions[0], "PRESENT"),
            ("KEY002", sessions[0], "ABSENT"),
            ("KEY003", sessions[2], "LATE"),
            ("GVA001", sessions[3], "PRESENT"),
            ("GVA002", sessions[3], "LATE"),
            ("GVA003", sessions[5], "ABSENT"),
        ]
        attendance_count = 0
        for admission, session, status in attendance_specs:
            register, _ = AttendanceRegister.objects.update_or_create(
                lesson_session=session,
                defaults={"status": "SUBMITTED", "submitted_at": timezone.now()},
            )
            AttendanceRecord.objects.update_or_create(
                attendance_register=register,
                enrollment=enrollments[admission],
                defaults={"status": status, "remarks": "Seeded attendance record."},
            )
            attendance_count += 1

        assessments = []
        for session in sessions[:2]:
            teacher = session.timetable_entry.teacher_subject.teacher
            assessment, _ = Assessment.objects.update_or_create(
                lesson_session=session,
                teacher=teacher,
                title=f"{session.timetable_entry.teacher_subject.subject.name} Practice Assessment",
                defaults={
                    "description": "Demo assessment for testing the assessment workflow.",
                    "assessment_type": "ASSIGNMENT",
                    "status": "PUBLISHED",
                    "due_date": session.lesson_date + timedelta(days=7),
                    "maximum_score": Decimal("100.00"),
                    "allow_resubmission": True,
                },
            )
            assessments.append(assessment)
            classroom_enrollments = [
                enrollment
                for enrollment in enrollments.values()
                if enrollment.classroom_id == session.timetable_entry.classroom_id
            ][:2]
            for index, enrollment in enumerate(classroom_enrollments):
                submission, _ = AssessmentSubmission.objects.update_or_create(
                    assessment=assessment,
                    enrollment=enrollment,
                    defaults={
                        "submitted_at": timezone.now(),
                        "submission_text": "This is a demo student submission.",
                        "submission_url": "https://example.com/demo-submission",
                        "status": "GRADED",
                        "is_late": index == 1,
                        "teacher_notes": "Good effort. Demo feedback.",
                        "submitted_by": enrollment.student.user,
                    },
                )
                AssessmentEvaluation.objects.update_or_create(
                    submission=submission,
                    defaults={
                        "total_score": Decimal("82.00") - Decimal(index * 7),
                        "percentage": Decimal("82.00") - Decimal(index * 7),
                        "narrative_feedback": "Demonstrates good understanding of the learning objective.",
                        "published": True,
                        "published_at": timezone.now(),
                    },
                )

        for student in students.values():
            portfolio, _ = Portfolio.objects.update_or_create(
                student=student,
                defaults={
                    "summary": "Demo learner portfolio showing project work and assessment evidence."
                },
            )
            PortfolioItem.objects.update_or_create(
                portfolio=portfolio,
                title="STEM Investigation Project",
                defaults={
                    "lesson_session": sessions[0],
                    "assessment_submission": None,
                    "item_type": "PROJECT",
                    "description": "A demo project item for portfolio testing.",
                    "event_date": date(2026, 2, 5),
                },
            )

        event_count = 0
        for code, school in schools.items():
            for title, event_type, start, end, location in [
                (
                    "Term 1 Parent Meeting",
                    "MEETING",
                    datetime(2026, 2, 14, 9),
                    datetime(2026, 2, 14, 11),
                    "Main Hall",
                ),
                (
                    "Science Project Exhibition",
                    "ACTIVITY",
                    datetime(2026, 3, 12, 10),
                    datetime(2026, 3, 12, 13),
                    "Science Lab",
                ),
            ]:
                CalendarEvent.objects.update_or_create(
                    school=school,
                    academic_year=academic_years[code],
                    title=title,
                    defaults={
                        "term": terms[(code, 1)],
                        "event_type": event_type,
                        "start_at": timezone.make_aware(start),
                        "end_at": timezone.make_aware(end),
                        "all_day": False,
                        "location": location,
                        "description": "Demo calendar event.",
                        "is_active": True,
                    },
                )
                event_count += 1

        communication_count = 0
        notification_count = 0
        for code, school in schools.items():
            school_users = [admin_users[code], *(teacher.user for teacher in teachers_by_school[code])]
            for recipient in school_users:
                CommunicationMessage.objects.update_or_create(
                    school=school,
                    sender=admin_users[code],
                    recipient=recipient,
                    subject="Welcome to the demo school workspace",
                    defaults={"body": "Seeded communication message for testing."},
                )
                Notification.objects.update_or_create(
                    school=school,
                    recipient=recipient,
                    title="Demo notification",
                    defaults={
                        "notification_type": "SYSTEM",
                        "body": "Seeded notification for testing.",
                        "link": "/",
                    },
                )
                communication_count += 1
                notification_count += 1

        return {
            "Schools": 2,
            "System administrators": 1,
            "School administrators": 2,
            "Teachers": 6,
            "Students": 6,
            "Parents": 4,
            "Academic years": 2,
            "Terms": 6,
            "Classrooms": 6,
            "Teacher-subject assignments": len(teacher_subjects),
            "Classroom teacher assignments": ClassroomTeacherAssignment.objects.filter(
                classroom__school__short_name__in=schools.keys()
            ).count(),
            "Enrollments": len(enrollments),
            "Periods": Period.objects.filter(school__short_name__in=schools.keys()).count(),
            "Timetables": len(timetables),
            "Timetable entries": len(entries),
            "Lesson sessions": len(sessions),
            "Attendance registers": AttendanceRegister.objects.filter(
                lesson_session__in=sessions
            ).count(),
            "Attendance records": attendance_count,
            "Assessments": len(assessments),
            "Assessment evaluations": AssessmentEvaluation.objects.filter(
                submission__assessment__in=assessments
            ).count(),
            "Portfolio records": len(students),
            "Calendar events": event_count,
            "Communication messages": communication_count,
            "Notifications": notification_count,
            "System administrator account": system_admin.email,
        }
