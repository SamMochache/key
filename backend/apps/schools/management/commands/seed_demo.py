from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
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


PASSWORD = "TestPass123!"
SYSTEM_ADMIN_EMAIL = "systemadmin@key.test"


class Command(BaseCommand):
    help = "Create repeatable demo data for two schools."

    def handle(self, *args, **options):
        with transaction.atomic():
            summary = self.seed()
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        for key, value in summary.items():
            self.stdout.write(f"  {key}: {value}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Demo login accounts"))
        for email in [
            SYSTEM_ADMIN_EMAIL,
            "admin@keyinternational.test",
            "admin@greenvalley.test",
            "james.otieno@keyinternational.test",
            "peter.maina@greenvalley.test",
            "brian.onyango@student.keyinternational.test",
            "linda.njeri@student.greenvalley.test",
        ]:
            self.stdout.write(f"  {email} / {PASSWORD}")

    def make_user(self, email, first_name, last_name, *, staff=False, superuser=False):
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": "+254700000000",
                "timezone": "Africa/Nairobi",
                "is_active": True,
                "is_staff": staff,
                "is_superuser": superuser,
            },
        )
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = True
        user.is_staff = user.is_staff or staff
        user.is_superuser = user.is_superuser or superuser
        if not user.check_password(PASSWORD):
            user.set_password(PASSWORD)
        user.save()
        return user

    def seed(self):
        schools = {}
        school_data = [
            ("KEY", "Key International School", "admin@keyinternational.test", "+254700100001", "Riverside Drive", "Nairobi"),
            ("GVA", "Green Valley Academy", "admin@greenvalley.test", "+254700100002", "Kiambu Road", "Kiambu"),
        ]
        for code, name, email, phone, address, city in school_data:
            school, _ = School.objects.get_or_create(
                short_name=code,
                defaults={
                    "name": name,
                    "email": email,
                    "phone_number": phone,
                    "address": address,
                    "city": city,
                    "country": "Kenya",
                    "timezone": "Africa/Nairobi",
                    "is_active": True,
                },
            )
            schools[code] = school

        system_admin = self.make_user(SYSTEM_ADMIN_EMAIL, "System", "Administrator", staff=True, superuser=True)
        admins = {
            "KEY": self.make_user("admin@keyinternational.test", "Alice", "Mwangi", staff=True),
            "GVA": self.make_user("admin@greenvalley.test", "Brian", "Kamau", staff=True),
        }
        for code, user in admins.items():
            SchoolAdministrator.objects.get_or_create(user=user, defaults={"school": schools[code], "is_active": True})

        curriculum, _ = Curriculum.objects.get_or_create(
            name="Cambridge International",
            defaults={"description": "Cambridge curriculum used by the demo schools.", "version": "2026", "is_active": True},
        )
        programmes = {}
        for name, order in [("Cambridge Primary", 1), ("Cambridge Lower Secondary", 2), ("Cambridge Upper Secondary", 3)]:
            programmes[name], _ = Programme.objects.get_or_create(
                curriculum=curriculum,
                name=name,
                defaults={"description": f"{name} programme.", "display_order": order, "is_active": True},
            )

        stages = {}
        for programme, name, number in [
            ("Cambridge Primary", "Year 4", 4),
            ("Cambridge Primary", "Year 5", 5),
            ("Cambridge Lower Secondary", "Year 7", 7),
        ]:
            stages[name], _ = CambridgeStage.objects.get_or_create(
                programme=programmes[programme],
                stage_number=number,
                defaults={"name": name, "display_order": number, "is_active": True},
            )

        for name, code, minimum, maximum, order in [
            ("Casa", "CASA", "3.0", "6.0", 1),
            ("Lower Elementary", "LE", "6.0", "9.0", 2),
            ("Upper Elementary", "UE", "9.0", "12.0", 3),
        ]:
            MontessoriLevel.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "minimum_age": Decimal(minimum),
                    "maximum_age": Decimal(maximum),
                    "description": f"Demo Montessori level: {name}.",
                    "display_order": order,
                    "is_active": True,
                },
            )

        subjects = {}
        for name, code, core, order in [
            ("English", "ENG", True, 1),
            ("Mathematics", "MATH", True, 2),
            ("Science", "SCI", True, 3),
            ("Global Perspectives", "GP", False, 4),
            ("Computing", "COMP", False, 5),
            ("Art & Design", "ART", False, 6),
            ("Physical Education", "PE", False, 7),
            ("Geography", "GEO", False, 8),
        ]:
            subjects[name], _ = Subject.objects.get_or_create(
                curriculum=curriculum,
                code=code,
                defaults={"name": name, "description": f"Demo {name} subject.", "is_core": core, "display_order": order, "is_active": True},
            )

        stage_subjects = {
            "Year 4": ["English", "Mathematics", "Science", "Global Perspectives", "Computing", "Art & Design", "Physical Education"],
            "Year 5": ["English", "Mathematics", "Science", "Global Perspectives", "Computing", "Art & Design", "Physical Education"],
            "Year 7": ["English", "Mathematics", "Science", "Global Perspectives", "Computing", "Geography", "Physical Education"],
        }
        for stage_name, names in stage_subjects.items():
            for order, subject_name in enumerate(names, 1):
                StageSubject.objects.get_or_create(
                    cambridge_stage=stages[stage_name],
                    subject=subjects[subject_name],
                    defaults={"weekly_lessons": 5 if subject_name in {"English", "Mathematics", "Science"} else 2, "is_core": subjects[subject_name].is_core, "display_order": order, "is_active": True},
                )

        years, terms, classrooms = {}, {}, {}
        for code, school in schools.items():
            year, _ = AcademicYear.objects.get_or_create(
                school=school,
                name="2026",
                defaults={"start_date": date(2026, 1, 5), "end_date": date(2026, 12, 4), "is_current": True, "is_active": True},
            )
            years[code] = year
            for number, start, end in [
                (1, date(2026, 1, 5), date(2026, 4, 2)),
                (2, date(2026, 4, 27), date(2026, 8, 7)),
                (3, date(2026, 8, 31), date(2026, 12, 4)),
            ]:
                terms[(code, number)], _ = Term.objects.get_or_create(
                    academic_year=year,
                    term_number=number,
                    defaults={"start_date": start, "end_date": end, "is_current": number == 3, "is_active": True},
                )
            for stage_name in ["Year 4", "Year 5", "Year 7"]:
                classrooms[(code, stage_name)], _ = Classroom.objects.get_or_create(
                    academic_year=year,
                    code=f"{code}-{stage_name.replace(' ', '').upper()}",
                    defaults={
                        "school": school,
                        "term": terms[(code, 1)],
                        "cambridge_stage": stages[stage_name],
                        "name": stage_name,
                        "capacity": 30,
                        "is_active": True,
                    },
                )

        departments = {}
        for code, school in schools.items():
            for name, dep_code in [("Primary", "PRI"), ("Secondary", "SEC")]:
                departments[(code, dep_code)], _ = Department.objects.get_or_create(
                    school=school,
                    code=dep_code,
                    defaults={"name": name, "description": f"{name} department at {school.name}.", "is_active": True},
                )

        teacher_data = [
            ("KEY", "james.otieno@keyinternational.test", "James", "Otieno", "KEY-T001", "PRI"),
            ("KEY", "mary.wanjiku@keyinternational.test", "Mary", "Wanjiku", "KEY-T002", "PRI"),
            ("KEY", "daniel.kiptoo@keyinternational.test", "Daniel", "Kiptoo", "KEY-T003", "SEC"),
            ("GVA", "peter.maina@greenvalley.test", "Peter", "Maina", "GVA-T001", "PRI"),
            ("GVA", "grace.njeri@greenvalley.test", "Grace", "Njeri", "GVA-T002", "PRI"),
            ("GVA", "samuel.kariuki@greenvalley.test", "Samuel", "Kariuki", "GVA-T003", "SEC"),
        ]
        teachers = {}
        for code, email, first, last, employee, dep_code in teacher_data:
            teachers[email], _ = Teacher.objects.get_or_create(
                user=self.make_user(email, first, last),
                defaults={"school": schools[code], "employee_number": employee, "employment_type": "FULL_TIME", "employment_date": date(2024, 1, 8), "status": "ACTIVE", "department": departments[(code, dep_code)]},
            )

        student_data = [
            ("KEY", "brian.onyango@student.keyinternational.test", "Brian", "Onyango", "KEY-ST001", date(2016, 3, 14), "MALE", "Year 4"),
            ("KEY", "faith.wambui@student.keyinternational.test", "Faith", "Wambui", "KEY-ST002", date(2016, 7, 2), "FEMALE", "Year 5"),
            ("KEY", "kevin.kimani@student.keyinternational.test", "Kevin", "Kimani", "KEY-ST003", date(2014, 11, 21), "MALE", "Year 7"),
            ("GVA", "linda.njeri@student.greenvalley.test", "Linda", "Njeri", "GVA-ST001", date(2016, 2, 9), "FEMALE", "Year 4"),
            ("GVA", "mark.kiprotich@student.greenvalley.test", "Mark", "Kiprotich", "GVA-ST002", date(2015, 8, 19), "MALE", "Year 5"),
            ("GVA", "sharon.akinyi@student.greenvalley.test", "Sharon", "Akinyi", "GVA-ST003", date(2014, 10, 5), "FEMALE", "Year 7"),
        ]
        students = {}
        for code, email, first, last, admission, dob, gender, stage_name in student_data:
            students[email], _ = Student.objects.get_or_create(
                user=self.make_user(email, first, last),
                defaults={"school": schools[code], "admission_number": admission, "admission_date": date(2025, 1, 6), "date_of_birth": dob, "gender": gender, "nationality": "Kenyan", "birth_certificate_number": f"BC-{admission}", "is_active": True},
            )

        parent_data = [
            ("KEY", "parent.brian@studentfamily.test", "Patrick", "Onyango"),
            ("KEY", "parent.faith@studentfamily.test", "Esther", "Wambui"),
            ("GVA", "parent.linda@studentfamily.test", "Joseph", "Njeri"),
            ("GVA", "parent.mark@studentfamily.test", "Ruth", "Kiprotich"),
        ]
        parents = {}
        for code, email, first, last in parent_data:
            parents[email], _ = Parent.objects.get_or_create(user=self.make_user(email, first, last), defaults={"school": schools[code], "is_active": True})
        for parent_email, student_email in [
            ("parent.brian@studentfamily.test", "brian.onyango@student.keyinternational.test"),
            ("parent.faith@studentfamily.test", "faith.wambui@student.keyinternational.test"),
            ("parent.faith@studentfamily.test", "kevin.kimani@student.keyinternational.test"),
            ("parent.linda@studentfamily.test", "linda.njeri@student.greenvalley.test"),
            ("parent.mark@studentfamily.test", "mark.kiprotich@student.greenvalley.test"),
            ("parent.mark@studentfamily.test", "sharon.akinyi@student.greenvalley.test"),
        ]:
            ParentStudentRelationship.objects.get_or_create(parent=parents[parent_email], student=students[student_email], defaults={"relationship": "PARENT", "can_view_reports": True, "is_primary_contact": True, "is_active": True})

        enrollments = {}
        for code, email, *_rest, stage_name in student_data:
            enrollments[email], _ = Enrollment.objects.get_or_create(
                student=students[email], academic_year=years[code], term=terms[(code, 1)],
                defaults={"classroom": classrooms[(code, stage_name)], "enrollment_date": date(2026, 1, 5), "status": "ENROLLED", "remarks": "Demo enrollment for application testing."},
            )

        periods = {}
        for code, school in schools.items():
            for sequence, name, start, end in [
                (1, "Period 1", time(8, 0), time(8, 45)),
                (2, "Period 2", time(8, 50), time(9, 35)),
                (3, "Period 3", time(9, 55), time(10, 40)),
            ]:
                periods[(code, sequence)], _ = Period.objects.get_or_create(school=school, sequence=sequence, defaults={"name": name, "start_time": start, "end_time": end, "is_break": False})

        teachers_by_school = {
            "KEY": [teachers["james.otieno@keyinternational.test"], teachers["mary.wanjiku@keyinternational.test"], teachers["daniel.kiptoo@keyinternational.test"]],
            "GVA": [teachers["peter.maina@greenvalley.test"], teachers["grace.njeri@greenvalley.test"], teachers["samuel.kariuki@greenvalley.test"],],
        }
        teacher_subjects = []
        mappings = [("Year 4", "English", 0), ("Year 4", "Mathematics", 1), ("Year 5", "Science", 1), ("Year 7", "Computing", 2)]
        for code in schools:
            for stage_name, subject_name, teacher_index in mappings:
                teacher_subjects.append(TeacherSubject.objects.get_or_create(
                    teacher=teachers_by_school[code][teacher_index], subject=subjects[subject_name], classroom=classrooms[(code, stage_name)], academic_year=years[code], term=terms[(code, 1)],
                    defaults={"role": "LEAD", "start_date": date(2026, 1, 5), "is_active": True},
                )[0])
            for index, stage_name in enumerate(["Year 4", "Year 5", "Year 7"]):
                ClassroomTeacherAssignment.objects.get_or_create(classroom=classrooms[(code, stage_name)], teacher=teachers_by_school[code][index], role="PRIMARY", defaults={"is_active": True})
            ClassroomTeacherAssignment.objects.get_or_create(classroom=classrooms[(code, "Year 4")], teacher=teachers_by_school[code][1], role="ASSISTANT", defaults={"is_active": True})

        timetables, entries = {}, []
        for code, school in schools.items():
            timetables[code], _ = Timetable.objects.get_or_create(school=school, academic_year=years[code], term=terms[(code, 1)], version=1, defaults={"name": f"{code} Term 1 Timetable", "status": "PUBLISHED", "effective_from": date(2026, 1, 5)})
            school_ts = [x for x in teacher_subjects if x.teacher.school_id == school.id]
            for sequence, ts in zip([1, 2, 3], school_ts[:3]):
                entries.append(TimetableEntry.objects.get_or_create(timetable=timetables[code], weekday="MONDAY", period=periods[(code, sequence)], classroom=ts.classroom, teacher_subject=ts, defaults={"room": f"Room 10{sequence}"})[0])

        sessions = []
        for index, entry in enumerate(entries):
            lesson_date = date(2026, 2, 2) + timedelta(days=index % 3)
            sessions.append(LessonSession.objects.get_or_create(
                timetable_entry=entry, lesson_date=lesson_date,
                defaults={"started_at": timezone.make_aware(datetime.combine(lesson_date, entry.period.start_time)), "ended_at": timezone.make_aware(datetime.combine(lesson_date, entry.period.end_time)), "teacher": entry.teacher_subject.teacher.user, "status": "COMPLETED", "remarks": "Demo lesson completed."},
            )[0])

        for session in sessions:
            register = AttendanceRegister.objects.get_or_create(lesson_session=session, defaults={"status": "SUBMITTED", "submitted_at": timezone.now()})[0]
            class_enrollments = [e for e in enrollments.values() if e.classroom_id == session.timetable_entry.classroom_id]
            for index, enrollment in enumerate(class_enrollments):
                AttendanceRecord.objects.get_or_create(attendance_register=register, enrollment=enrollment, defaults={"status": ["PRESENT", "LATE", "ABSENT"][index % 3], "remarks": "Demo attendance record."})

        assessments = []
        for session in sessions[:2]:
            assessment = Assessment.objects.get_or_create(
                lesson_session=session, teacher=session.timetable_entry.teacher_subject.teacher,
                title=f"{session.timetable_entry.teacher_subject.subject.name} Practice Assessment",
                defaults={"description": "Demo assessment for testing the assessment workflow.", "assessment_type": "ASSIGNMENT", "status": "PUBLISHED", "due_date": session.lesson_date + timedelta(days=7), "maximum_score": Decimal("100.00"), "allow_resubmission": True},
            )[0]
            assessments.append(assessment)
            for index, enrollment in enumerate([e for e in enrollments.values() if e.classroom_id == session.timetable_entry.classroom_id][:2]):
                submission = AssessmentSubmission.objects.get_or_create(
                    assessment=assessment, enrollment=enrollment,
                    defaults={"submitted_at": timezone.now(), "submission_text": "This is a demo student submission.", "submission_url": "https://example.com/demo-submission", "status": "GRADED", "is_late": index == 1, "teacher_notes": "Good effort. Demo feedback.", "submitted_by": enrollment.student.user},
                )[0]
                AssessmentEvaluation.objects.get_or_create(submission=submission, defaults={"total_score": Decimal("82.00") - Decimal(index * 7), "percentage": Decimal("82.00") - Decimal(index * 7), "narrative_feedback": "Demonstrates good understanding of the learning objective.", "published": True, "published_at": timezone.now()})

        for student in students.values():
            portfolio = Portfolio.objects.get_or_create(student=student, defaults={"summary": "Demo learner portfolio showing project work and assessment evidence."})[0]
            PortfolioItem.objects.get_or_create(portfolio=portfolio, title="STEM Investigation Project", defaults={"lesson_session": sessions[0] if sessions else None, "item_type": "PROJECT", "description": "A demo project item for portfolio testing.", "event_date": date(2026, 2, 5)})

        for code, school in schools.items():
            for title, event_type, start, end, location in [
                ("Term 1 Parent Meeting", "MEETING", datetime(2026, 2, 14, 9), datetime(2026, 2, 14, 11), "Main Hall"),
                ("Science Project Exhibition", "ACTIVITY", datetime(2026, 3, 12, 10), datetime(2026, 3, 12, 13), "Science Lab"),
            ]:
                CalendarEvent.objects.get_or_create(school=school, academic_year=years[code], title=title, defaults={"term": terms[(code, 1)], "event_type": event_type, "start_at": timezone.make_aware(start), "end_at": timezone.make_aware(end), "all_day": False, "location": location, "description": "Demo calendar event.", "is_active": True})

            school_users = [admins[code], *teachers_by_school[code]]
            for recipient in school_users:
                CommunicationMessage.objects.get_or_create(school=school, sender=admins[code], recipient=recipient, subject="Welcome to the demo school workspace", defaults={"body": "Seeded communication message for testing."})
                Notification.objects.get_or_create(school=school, recipient=recipient, title="Demo notification", defaults={"notification_type": "SYSTEM", "body": "Seeded notification for testing.", "link": "/"})

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
            "Timetables": len(timetables),
            "Timetable entries": len(entries),
            "Lesson sessions": len(sessions),
            "Assessments": len(assessments),
            "Portfolio records": len(students),
            "System administrator account": system_admin.email,
        }
