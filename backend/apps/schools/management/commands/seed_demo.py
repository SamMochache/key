from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from apps.assessments.models import Assessment, AssessmentEvaluation, AssessmentSubmission
from apps.attendance.models import AttendanceRecord
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
            raise CommandError(
                "seed_demo is development-only. Run it with DEBUG=True."
            )

        with transaction.atomic():
            if options["reset"]:
                self.reset_demo()
            summary = self.seed()

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        for label, value in summary.items():
            self.stdout.write(f"{label}: {value}")

    def reset_demo(self):
        """Delete only records belonging to this demo dataset."""
        demo_school_names = ["KEY", "GVA"]
        demo_emails = [
            "systemadmin@key.test",
            "admin@keyinternational.test",
            "admin@greenvalley.test",
        ]

        schools = School.objects.filter(short_name__in=demo_school_names)
        school_users = User.objects.filter(email__endswith=".test")

        CommunicationMessage.objects.filter(school__in=schools).delete()
        Notification.objects.filter(school__in=schools).delete()
        SchoolAdministrator.objects.filter(school__in=schools).delete()
        Teacher.objects.filter(school__in=schools).delete()
        Student.objects.filter(school__in=schools).delete()
        Parent.objects.filter(user__in=school_users).delete()
        schools.delete()

        User.objects.filter(email__in=demo_emails).delete()
        User.objects.filter(email__endswith="@keyinternational.test").delete()
        User.objects.filter(email__endswith="@greenvalley.test").delete()
        User.objects.filter(email__endswith="@student.keyinternational.test").delete()
        User.objects.filter(email__endswith="@student.greenvalley.test").delete()

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
                school=school,
                code="PRI",
                defaults={"name": "Primary"},
            )
            departments[(code, "SEC")], _ = Department.objects.get_or_create(
                school=school,
                code="SEC",
                defaults={"name": "Secondary"},
            )

        curriculum, _ = Curriculum.objects.get_or_create(
            name="Cambridge International",
            defaults={"description": "Cambridge international curriculum demo."},
        )
        montessori_curriculum, _ = Curriculum.objects.get_or_create(
            name="Montessori",
            defaults={"description": "Montessori curriculum demo."},
        )

        programmes = {}
        for name in ["Cambridge Primary", "Cambridge Lower Secondary", "Cambridge Upper Secondary"]:
            programmes[name], _ = Programme.objects.get_or_create(
                name=name,
                defaults={"curriculum": curriculum},
            )

        stages = {}
        stage_specs = [
            ("Year 4", "Cambridge Primary", 4, 4),
            ("Year 5", "Cambridge Primary", 5, 5),
            ("Year 7", "Cambridge Lower Secondary", 7, 7),
            ("Year 8", "Cambridge Lower Secondary", 8, 8),
        ]
        for name, programme_name, stage_number, display_order in stage_specs:
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
        for name in ["Casa", "Lower Elementary"]:
            montessori[name], _ = MontessoriLevel.objects.get_or_create(
                name=name,
                defaults={"curriculum": montessori_curriculum},
            )

        subject_names = [
            "English", "Mathematics", "Science", "Global Perspectives", "Computing",
            "Art & Design", "Physical Education", "Biology", "Physics", "Chemistry",
            "Computer Science", "Geography", "History",
        ]
        subjects = {}
        for name in subject_names:
            subjects[name], _ = Subject.objects.get_or_create(name=name)

        for stage in stages.values():
            for subject_name in [
                "English", "Mathematics", "Science", "Global Perspectives",
                "Computing", "Art & Design", "Physical Education",
            ]:
                StageSubject.objects.get_or_create(stage=stage, subject=subjects[subject_name])

        academic_years = {}
        terms = {}
        classrooms = {}
        for code, school in schools.items():
            academic_years[code], _ = AcademicYear.objects.update_or_create(
                school=school,
                name="2026 Academic Year",
                defaults={
                    "start_date": date(2026, 1, 5), "end_date": date(2026, 12, 4),
                    "is_current": True, "is_active": True,
                },
            )
            for number, start, end in [
                (1, date(2026, 1, 5), date(2026, 4, 2)),
                (2, date(2026, 5, 4), date(2026, 8, 7)),
                (3, date(2026, 8, 31), date(2026, 12, 4)),
            ]:
                terms[(code, number)], _ = Term.objects.update_or_create(
                    academic_year=academic_years[code], name=f"Term {number}",
                    defaults={"start_date": start, "end_date": end},
                )
            for stage_name in ["Year 4", "Year 5", "Year 7"]:
                classrooms[(code, stage_name)], _ = Classroom.objects.get_or_create(
                    school=school, academic_year=academic_years[code], name=stage_name,
                    defaults={
                        "cambridge_stage": stages[stage_name],
                        "montessori_level": None,
                        "term": terms[(code, 1)],
                    },
                )

        teacher_specs = [
            ("KEY", "james.otieno@keyinternational.test", "James", "Otieno", "T001", "PRI", "Mathematics"),
            ("KEY", "mary.wanjiku@keyinternational.test", "Mary", "Wanjiku", "T002", "PRI", "English"),
            ("KEY", "daniel.kiptoo@keyinternational.test", "Daniel", "Kiptoo", "T003", "SEC", "Science"),
            ("GVA", "peter.maina@greenvalley.test", "Peter", "Maina", "T001", "PRI", "Mathematics"),
            ("GVA", "grace.njeri@greenvalley.test", "Grace", "Njeri", "T002", "PRI", "English"),
            ("GVA", "samuel.kariuki@greenvalley.test", "Samuel", "Kariuki", "T003", "SEC", "Science"),
        ]
        teachers = []
        teachers_by_school = {"KEY": [], "GVA": []}
        teacher_subjects = []
        for code, email, first, last, employee, dept, subject_name in teacher_specs:
            user = self.user(email, first, last)
            teacher, _ = Teacher.objects.update_or_create(
                user=user,
                defaults={
                    "school": schools[code], "employee_number": employee,
                    "employment_type": "FULL_TIME", "employment_date": date(2024, 1, 8),
                    "status": "ACTIVE", "department": departments[(code, dept)],
                },
            )
            teachers.append(teacher)
            teachers_by_school[code].append(teacher)
            teacher_subjects.append(
                TeacherSubject.objects.get_or_create(
                    teacher=teacher, subject=subjects[subject_name], defaults={"is_active": True}
                )[0]
            )

        assignment_specs = [
            ("KEY", "Year 4", 0, "PRIMARY"), ("KEY", "Year 4", 1, "ASSISTANT"),
            ("KEY", "Year 5", 2, "PRIMARY"), ("GVA", "Year 4", 3, "PRIMARY"),
            ("GVA", "Year 4", 4, "ASSISTANT"), ("GVA", "Year 5", 5, "PRIMARY"),
        ]
        for code, classroom_name, teacher_index, role in assignment_specs:
            ClassroomTeacherAssignment.objects.get_or_create(
                classroom=classrooms[(code, classroom_name)],
                teacher=teachers_by_school[code][teacher_index % len(teachers_by_school[code])],
                role=role, defaults={"is_active": True},
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
        for code, email, first, last, admission, dob, gender, stage_name in student_specs:
            user = self.user(email, first, last)
            student, _ = Student.objects.update_or_create(
                user=user,
                defaults={
                    "school": schools[code], "admission_number": admission,
                    "admission_date": date(2025, 1, 6), "date_of_birth": dob,
                    "gender": gender, "nationality": "Kenyan",
                },
            )
            students[admission] = student
            enrollment, _ = Enrollment.objects.get_or_create(
                student=student, classroom=classrooms[(code, stage_name)],
                defaults={"status": "ACTIVE", "enrollment_date": date(2026, 1, 5)},
            )
            enrollments[admission] = enrollment

        parent_specs = [
            ("KEY", "parent.onyango@keyinternational.test", "Patrick", "Onyango", "KEY-P001", ["KEY001"]),
            ("KEY", "parent.wambui@keyinternational.test", "Jane", "Wambui", "KEY-P002", ["KEY002"]),
            ("GVA", "parent.njeri@greenvalley.test", "David", "Njeri", "GVA-P001", ["GVA001"]),
            ("GVA", "parent.kiprotich@greenvalley.test", "Susan", "Kiprotich", "GVA-P002", ["GVA002", "GVA003"]),
        ]
        parents = []
        for code, email, first, last, phone, admission_numbers in parent_specs:
            user = self.user(email, first, last)
            parent, _ = Parent.objects.update_or_create(
                user=user, defaults={"school": schools[code], "phone_number": phone}
            )
            parents.append(parent)
            for admission in admission_numbers:
                ParentStudentRelationship.objects.get_or_create(
                    parent=parent, student=students[admission],
                    defaults={"relationship": "PARENT", "is_primary": True},
                )

        periods = {}
        timetables = {}
        entries = []
        sessions = []
        for code, school in schools.items():
            for number, start, end in [
                (1, "08:00:00", "08:45:00"), (2, "08:50:00", "09:35:00"),
                (3, "09:45:00", "10:30:00"),
            ]:
                periods[(code, number)], _ = Period.objects.get_or_create(
                    school=school, name=f"Period {number}",
                    defaults={"start_time": start, "end_time": end, "order": number},
                )
            timetable, _ = Timetable.objects.get_or_create(
                school=school, academic_year=academic_years[code], term=terms[(code, 1)],
                name="Term 1 Timetable", defaults={"is_active": True},
            )
            timetables[code] = timetable
            for day, classroom_name, period_number, teacher_subject in [
                ("MONDAY", "Year 4", 1, 0), ("TUESDAY", "Year 5", 1, 1),
                ("WEDNESDAY", "Year 7", 1, 2),
            ]:
                school_teacher_subjects = [
                    ts for ts in teacher_subjects if ts.teacher.school_id == school.id
                ]
                ts = school_teacher_subjects[teacher_subject % len(school_teacher_subjects)]
                entry, _ = TimetableEntry.objects.get_or_create(
                    timetable=timetable, classroom=classrooms[(code, classroom_name)],
                    teacher_subject=ts, day_of_week=day, period=periods[(code, period_number)],
                    defaults={"is_active": True},
                )
                entries.append(entry)
                session, _ = LessonSession.objects.get_or_create(
                    timetable_entry=entry, lesson_date=date(2026, 2, 2 + len(sessions)),
                    defaults={
                        "status": "COMPLETED", "topic": f"{ts.subject.name} Demo Lesson",
                        "notes": "Seeded lesson session for testing.",
                    },
                )
                sessions.append(session)

        attendance_count = 0
        attendance_specs = [
            ("KEY001", sessions[0], "PRESENT"), ("KEY002", sessions[0], "ABSENT"),
            ("KEY003", sessions[2], "LATE"), ("GVA001", sessions[3], "PRESENT"),
            ("GVA002", sessions[3], "LATE"), ("GVA003", sessions[5], "ABSENT"),
        ]
        for admission, session, status in attendance_specs:
            AttendanceRecord.objects.get_or_create(
                lesson_session=session, student=students[admission],
                defaults={
                    "status": status,
                    "marked_by": session.timetable_entry.teacher_subject.teacher.user,
                    "remarks": "Seeded attendance record.",
                },
            )
            attendance_count += 1

        assessments = []
        for session in sessions[:2]:
            assessment = Assessment.objects.get_or_create(
                lesson_session=session,
                teacher=session.timetable_entry.teacher_subject.teacher,
                title=f"{session.timetable_entry.teacher_subject.subject.name} Practice Assessment",
                defaults={
                    "description": "Demo assessment for testing the assessment workflow.",
                    "assessment_type": "ASSIGNMENT", "status": "PUBLISHED",
                    "due_date": session.lesson_date + timedelta(days=7),
                    "maximum_score": Decimal("100.00"), "allow_resubmission": True,
                },
            )[0]
            assessments.append(assessment)
            classroom_enrollments = [
                e for e in enrollments.values()
                if e.classroom_id == session.timetable_entry.classroom_id
            ][:2]
            for index, enrollment in enumerate(classroom_enrollments):
                submission = AssessmentSubmission.objects.get_or_create(
                    assessment=assessment, enrollment=enrollment,
                    defaults={
                        "submitted_at": timezone.now(),
                        "submission_text": "This is a demo student submission.",
                        "submission_url": "https://example.com/demo-submission",
                        "status": "GRADED", "is_late": index == 1,
                        "teacher_notes": "Good effort. Demo feedback.",
                        "submitted_by": enrollment.student.user,
                    },
                )[0]
                AssessmentEvaluation.objects.get_or_create(
                    submission=submission,
                    defaults={
                        "total_score": Decimal("82.00") - Decimal(index * 7),
                        "percentage": Decimal("82.00") - Decimal(index * 7),
                        "narrative_feedback": "Demonstrates good understanding of the learning objective.",
                        "published": True, "published_at": timezone.now(),
                    },
                )

        for student in students.values():
            portfolio = Portfolio.objects.get_or_create(
                student=student,
                defaults={"summary": "Demo learner portfolio showing project work and assessment evidence."},
            )[0]
            PortfolioItem.objects.get_or_create(
                portfolio=portfolio, title="STEM Investigation Project",
                defaults={
                    "lesson_session": sessions[0] if sessions else None,
                    "item_type": "PROJECT",
                    "description": "A demo project item for portfolio testing.",
                    "event_date": date(2026, 2, 5),
                },
            )

        event_count = 0
        for code, school in schools.items():
            for title, event_type, start, end, location in [
                ("Term 1 Parent Meeting", "MEETING", datetime(2026, 2, 14, 9), datetime(2026, 2, 14, 11), "Main Hall"),
                ("Science Project Exhibition", "ACTIVITY", datetime(2026, 3, 12, 10), datetime(2026, 3, 12, 13), "Science Lab"),
            ]:
                CalendarEvent.objects.get_or_create(
                    school=school, academic_year=academic_years[code], title=title,
                    defaults={
                        "term": terms[(code, 1)], "event_type": event_type,
                        "start_at": timezone.make_aware(start), "end_at": timezone.make_aware(end),
                        "all_day": False, "location": location,
                        "description": "Demo calendar event.", "is_active": True,
                    },
                )
                event_count += 1

        communication_count = 0
        notification_count = 0
        for code, school in schools.items():
            school_users = [admin_users[code], *(teacher.user for teacher in teachers_by_school[code])]
            for recipient in school_users:
                CommunicationMessage.objects.get_or_create(
                    school=school, sender=admin_users[code], recipient=recipient,
                    subject="Welcome to the demo school workspace",
                    defaults={"body": "Seeded communication message for testing."},
                )
                Notification.objects.get_or_create(
                    school=school, recipient=recipient, title="Demo notification",
                    defaults={
                        "notification_type": "SYSTEM",
                        "body": "Seeded notification for testing.", "link": "/",
                    },
                )
                communication_count += 1
                notification_count += 1

        return {
            "Schools": 2, "System administrators": 1, "School administrators": 2,
            "Teachers": 6, "Students": 6, "Parents": 4, "Academic years": 2,
            "Terms": 6, "Classrooms": 6, "Teacher-subject assignments": len(teacher_subjects),
            "Classroom teacher assignments": ClassroomTeacherAssignment.objects.filter(
                classroom__school__short_name__in=schools.keys()
            ).count(),
            "Enrollments": len(enrollments),
            "Periods": Period.objects.filter(school__short_name__in=schools.keys()).count(),
            "Timetables": len(timetables), "Timetable entries": len(entries),
            "Lesson sessions": len(sessions), "Attendance records": attendance_count,
            "Assessments": len(assessments),
            "Assessment evaluations": AssessmentEvaluation.objects.filter(
                submission__assessment__in=assessments
            ).count(),
            "Portfolio records": len(students), "Calendar events": event_count,
            "Communication messages": communication_count, "Notifications": notification_count,
            "System administrator account": system_admin.email,
        }
