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
    help = "Create a complete, repeatable demo dataset for two schools."

    def handle(self, *args, **options):
        with transaction.atomic():
            data = self.seed()

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        for label, value in data.items():
            self.stdout.write(f"  {label}: {value}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Demo login accounts"))
        self.stdout.write(f"  System administrator: {SYSTEM_ADMIN_EMAIL} / {PASSWORD}")
        self.stdout.write("  KEY administrator: admin@keyinternational.test / TestPass123!")
        self.stdout.write("  GVA administrator: admin@greenvalley.test / TestPass123!")
        self.stdout.write("  KEY teacher: james.otieno@keyinternational.test / TestPass123!")
        self.stdout.write("  GVA teacher: peter.maina@greenvalley.test / TestPass123!")
        self.stdout.write("  KEY student: brian.onyango@student.keyinternational.test / TestPass123!")
        self.stdout.write("  GVA student: linda.njeri@student.greenvalley.test / TestPass123!")

    def user(self, email, first_name, last_name, *, staff=False, superuser=False):
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
        changed = False
        if user.first_name != first_name:
            user.first_name = first_name
            changed = True
        if user.last_name != last_name:
            user.last_name = last_name
            changed = True
        if staff and not user.is_staff:
            user.is_staff = True
            changed = True
        if superuser and not user.is_superuser:
            user.is_superuser = True
            changed = True
        if not user.check_password(PASSWORD):
            user.set_password(PASSWORD)
            changed = True
        if changed:
            user.save()
        return user

    def seed(self):
        schools = {}
        for values in [
            {
                "name": "Key International School",
                "short_name": "KEY",
                "email": "admin@keyinternational.test",
                "phone_number": "+254700100001",
                "address": "Riverside Drive",
                "city": "Nairobi",
            },
            {
                "name": "Green Valley Academy",
                "short_name": "GVA",
                "email": "admin@greenvalley.test",
                "phone_number": "+254700100002",
                "address": "Kiambu Road",
                "city": "Kiambu",
            },
        ]:
            school, _ = School.objects.get_or_create(
                short_name=values["short_name"],
                defaults={**values, "country": "Kenya", "timezone": "Africa/Nairobi", "is_active": True},
            )
            schools[school.short_name] = school

        system_admin = self.user(
            SYSTEM_ADMIN_EMAIL,
            "System",
            "Administrator",
            staff=True,
            superuser=True,
        )

        admin_users = {
            "KEY": self.user("admin@keyinternational.test", "Alice", "Mwangi", staff=True),
            "GVA": self.user("admin@greenvalley.test", "Brian", "Kamau", staff=True),
        }
        for code, user in admin_users.items():
            SchoolAdministrator.objects.get_or_create(user=user, defaults={"school": schools[code], "is_active": True})

        curriculum, _ = Curriculum.objects.get_or_create(
            name="Cambridge International",
            defaults={
                "description": "Cambridge curriculum used by the demo schools.",
                "version": "2026",
                "is_active": True,
            },
        )
        programme_specs = [
            ("Cambridge Primary", "Primary education programme", 1),
            ("Cambridge Lower Secondary", "Lower secondary education programme", 2),
            ("Cambridge Upper Secondary", "Upper secondary education programme", 3),
        ]
        programmes = {}
        for name, description, order in programme_specs:
            programmes[name], _ = Programme.objects.get_or_create(
                curriculum=curriculum,
                name=name,
                defaults={"description": description, "display_order": order, "is_active": True},
            )

        stages = {}
        stage_specs = [
            ("Cambridge Primary", "Year 4", 4, 4),
            ("Cambridge Primary", "Year 5", 5, 5),
            ("Cambridge Lower Secondary", "Year 7", 7, 7),
        ]
        for programme_name, name, number, order in stage_specs:
            stages[name], _ = CambridgeStage.objects.get_or_create(
                programme=programmes[programme_name],
                stage_number=number,
                defaults={"name": name, "display_order": order, "is_active": True},
            )

        montessori = {}
        for name, code, minimum, maximum, order in [
            ("Casa", "CASA", Decimal("3.0"), Decimal("6.0"), 1),
            ("Lower Elementary", "LE", Decimal("6.0"), Decimal("9.0"), 2),
            ("Upper Elementary", "UE", Decimal("9.0"), Decimal("12.0"), 3),
        ]:
            montessori[code], _ = __import__("apps.academics.models", fromlist=["MontessoriLevel"]).MontessoriLevel.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "minimum_age": minimum,
                    "maximum_age": maximum,
                    "description": f"Demo Montessori level: {name}.",
                    "display_order": order,
                    "is_active": True,
                },
            )

        subjects = {}
        subject_specs = [
            ("English", "ENG", True, 1),
            ("Mathematics", "MATH", True, 2),
            ("Science", "SCI", True, 3),
            ("Global Perspectives", "GP", False, 4),
            ("Computing", "COMP", False, 5),
            ("Art & Design", "ART", False, 6),
            ("Physical Education", "PE", False, 7),
            ("Geography", "GEO", False, 8),
        ]
        for name, code, core, order in subject_specs:
            subjects[name], _ = Subject.objects.get_or_create(
                curriculum=curriculum,
                code=code,
                defaults={"name": name, "description": f"Demo {name} subject.", "is_core": core, "display_order": order, "is_active": True},
            )

        for stage_name, subject_names in {
            "Year 4": ["English", "Mathematics", "Science", "Global Perspectives", "Computing", "Art & Design", "Physical Education"],
            "Year 5": ["English", "Mathematics", "Science", "Global Perspectives", "Computing", "Art & Design", "Physical Education"],
            "Year 7": ["English", "Mathematics", "Science", "Global Perspectives", "Computing", "Geography", "Physical Education"],
        }.items():
            for index, subject_name in enumerate(subject_names, start=1):
                StageSubject.objects.get_or_create(
                    cambridge_stage=stages[stage_name],
                    subject=subjects[subject_name],
                    defaults={"weekly_lessons": 5 if subject_name in {"English", "Mathematics", "Science"} else 2, "is_core": subjects[subject_name].is_core, "display_order": index, "is_active": True},
                )

        academic_years = {}
        terms = {}
        classrooms = {}
        for code, school in schools.items():
            year, _ = AcademicYear.objects.get_or_create(
                school=school,
                name="2026",
                defaults={"start_date": date(2026, 1, 5), "end_date": date(2026, 12, 4), "is_current": True, "is_active": True},
            )
            academic_years[code] = year
            for number, start, end in [
                (1, date(2026, 1, 5), date(2026, 4, 2)),
                (2, date(2026, 4, 27), date(2026, 8, 7)),
                (3, date(2026, 8, 31), date(2026, 12, 4)),
            ]:
                term, _ = Term.objects.get_or_create(
                    academic_year=year,
                    term_number=number,
                    defaults={"start_date": start, "end_date": end, "is_current": number == 3, "is_active": True},
                )
                terms[(code, number)] = term

            for stage_name in ["Year 4", "Year 5", "Year 7"]:
                classroom, _ = Classroom.objects.get_or_create(
                    academic_year=year,
                    code=f"{code}-{stage_name.replace(' ', '').upper()}",
                    defaults={
                        "school": school,
                        "term": terms[(code, 1)],
                        "cambridge_stage": stages[stage_name],
                        "montessori_level": None,
                        "name": stage_name,
                        "capacity": 30,
                        "is_active": True,
                    },
                )
                classrooms[(code, stage_name)] = classroom

        departments = {}
        for code, school in schools.items():
            for name, dep_code in [("Primary", "PRI"), ("Secondary", "SEC")]:
                departments[(code, dep_code)], _ = Department.objects.get_or_create(
                    school=school,
                    code=dep_code,
                    defaults={"name": name, "description": f"{name} department at {school.name}.", "is_active": True},
                )

        teacher_specs = [
            ("KEY", "james.otieno@keyinternational.test", "James", "Otieno", "KEY-T001", "PRI"),
            ("KEY", "mary.wanjiku@keyinternational.test", "Mary", "Wanjiku", "KEY-T002", "PRI"),
            ("KEY", "daniel.kiptoo@keyinternational.test", "Daniel", "Kiptoo", "KEY-T003", "SEC"),
            ("GVA", "peter.maina@greenvalley.test", "Peter", "Maina", "GVA-T001", "PRI"),
            ("GVA", "grace.njeri@greenvalley.test", "Grace", "Njeri", "GVA-T002", "PRI"),
            ("GVA", "samuel.kariuki@greenvalley.test", "Samuel", "Kariuki", "GVA-T003", "SEC"),
        ]
        teachers = {}
        for code, email, first, last, employee, dep_code in teacher_specs:
            user = self.user(email, first, last)
            teachers[email], _ = Teacher.objects.get_or_create(
                user=user,
                defaults={
                    "school": schools[code],
                    "employee_number": employee,
                    "employment_type": "FULL_TIME",
                    "employment_date": date(2024, 1, 8),
                    "status": "ACTIVE",
                    "department": departments[(code, dep_code)],
                },
            )

        student_specs = [
            ("KEY", "brian.onyango@student.keyinternational.test", "Brian", "Onyango", "KEY-ST001", date(2016, 3, 14), "MALE", "Year 4"),
            ("KEY", "faith.wambui@student.keyinternational.test", "Faith", "Wambui", "KEY-ST002", date(2016, 7, 2), "FEMALE", "Year 5"),
            ("KEY", "kevin.kimani@student.keyinternational.test", "Kevin", "Kimani", "KEY-ST003", date(2014, 11, 21), "MALE", "Year 7"),
            ("GVA", "linda.njeri@student.greenvalley.test", "Linda", "Njeri", "GVA-ST001", date(2016, 2, 9), "FEMALE", "Year 4"),
            ("GVA", "mark.kiprotich@student.greenvalley.test", "Mark", "Kiprotich", "GVA-ST002", date(2015, 8, 19), "MALE", "Year 5"),
            ("GVA", "sharon.akinyi@student.greenvalley.test", "Sharon", "Akinyi", "GVA-ST003", date(2014, 10, 5), "FEMALE", "Year 7"),
        ]
        students = {}
        for code, email, first, last, admission, dob, gender, stage_name in student_specs:
            user = self.user(email, first, last)
            students[email] = Student.objects.get_or_create(
                user=user,
                defaults={
                    "school": schools[code],
                    "admission_number": admission,
                    "admission_date": date(2025, 1, 6),
                    "date_of_birth": dob,
                    "gender": gender,
                    "nationality": "Kenyan",
                    "birth_certificate_number": f"BC-{admission}",
                    "is_active": True,
                },
            )[0]

        parent_specs = [
            ("KEY", "parent.brian@studentfamily.test", "Patrick", "Onyango"),
            ("KEY", "parent.faith@studentfamily.test", "Esther", "Wambui"),
            ("GVA", "parent.linda@studentfamily.test", "Joseph", "Njeri"),
            ("GVA", "parent.mark@studentfamily.test", "Ruth", "Kiprotich"),
        ]
        parents = {}
        for code, email, first, last in parent_specs:
            user = self.user(email, first, last)
            parents[email] = Parent.objects.get_or_create(user=user, defaults={"school": schools[code], "is_active": True})[0]

        relationships = [
            ("parent.brian@studentfamily.test", "brian.onyango@student.keyinternational.test"),
            ("parent.faith@studentfamily.test", "faith.wambui@student.keyinternational.test"),
            ("parent.faith@studentfamily.test", "kevin.kimani@student.keyinternational.test"),
            ("parent.linda@studentfamily.test", "linda.njeri@student.greenvalley.test"),
            ("parent.mark@studentfamily.test", "mark.kiprotich@student.greenvalley.test"),
            ("parent.mark@studentfamily.test", "sharon.akinyi@student.greenvalley.test"),
        ]
        for parent_email, student_email in relationships:
            ParentStudentRelationship.objects.get_or_create(
                parent=parents[parent_email],
                student=students[student_email],
                defaults={"relationship": "PARENT", "can_view_reports": True, "is_primary_contact": True, "is_active": True},
            )

        enrollments = {}
        for code, _, email, _, _, _, _, stage_name in student_specs:
            student = students[email]
            enrollment, _ = Enrollment.objects.get_or_create(
                student=student,
                academic_year=academic_years[code],
                term=terms[(code, 1)],
                defaults={
                    "classroom": classrooms[(code, stage_name)],
                    "enrollment_date": date(2026, 1, 5),
                    "status": "ENROLLED",
                    "remarks": "Demo enrollment for application testing.",
                },
            )
            enrollments[email] = enrollment

        periods = {}
        for code, school in schools.items():
            for sequence, name, start, end, is_break in [
                (1, "Period 1", time(8, 0), time(8, 45), False),
                (2, "Period 2", time(8, 50), time(9, 35), False),
                (3, "Break", time(9, 35), time(9, 55), True),
                (4, "Period 3", time(9, 55), time(10, 40), False),
            ]:
                periods[(code, sequence)], _ = Period.objects.get_or_create(
                    school=school,
                    sequence=sequence,
                    defaults={"name": name, "start_time": start, "end_time": end, "is_break": is_break},
                )

        teacher_by_code = {
            "KEY": [teachers["james.otieno@keyinternational.test"], teachers["mary.wanjiku@keyinternational.test"], teachers["daniel.kiptoo@keyinternational.test"]],
            "GVA": [teachers["peter.maina@greenvalley.test"], teachers["grace.njeri@greenvalley.test"], teachers["samuel.kariuki@greenvalley.test"]],
        }
        teacher_subjects = []
        for code in schools:
            mapping = [
                ("Year 4", "English", 0),
                ("Year 4", "Mathematics", 1),
                ("Year 5", "Science", 1),
                ("Year 7", "Computing", 2),
            ]
            for stage_name, subject_name, teacher_index in mapping:
                ts, _ = TeacherSubject.objects.get_or_create(
                    teacher=teacher_by_code[code][teacher_index],
                    subject=subjects[subject_name],
                    classroom=classrooms[(code, stage_name)],
                    academic_year=academic_years[code],
                    term=terms[(code, 1)],
                    defaults={"role": "LEAD", "start_date": date(2026, 1, 5), "is_active": True},
                )
                teacher_subjects.append(ts)

        for code, teachers_for_school in teacher_by_code.items():
            for index, stage_name in enumerate(["Year 4", "Year 5", "Year 7"]):
                ClassroomTeacherAssignment.objects.get_or_create(
                    classroom=classrooms[(code, stage_name)],
                    teacher=teachers_for_school[index],
                    role="PRIMARY",
                    defaults={"is_active": True},
                )
            ClassroomTeacherAssignment.objects.get_or_create(
                classroom=classrooms[(code, "Year 4")],
                teacher=teachers_for_school[1],
                role="ASSISTANT",
                defaults={"is_active": True},
            )

        timetables = {}
        entries = []
        for code, school in schools.items():
            timetable, _ = Timetable.objects.get_or_create(
                school=school,
                academic_year=academic_years[code],
                term=terms[(code, 1)],
                version=1,
                defaults={"name": f"{school.short_name} Term 1 Timetable", "status": "PUBLISHED", "effective_from": date(2026, 1, 5)},
            )
            timetables[code] = timetable
            for sequence, ts in enumerate([x for x in teacher_subjects if x.teacher.school_id == school.id][:3], start=1):
                entry, _ = TimetableEntry.objects.get_or_create(
                    timetable=timetable,
                    weekday="MONDAY",
                    period=periods[(code, sequence)],
                    classroom=ts.classroom,
                    teacher_subject=ts,
                    defaults={"room": f"Room {sequence}0{1}"},
                )
                entries.append(entry)

        lesson_sessions = []
        lesson_dates = [date(2026, 2, 2), date(2026, 2, 3), date(2026, 2, 4)]
        for entry in entries:
            teacher_user = entry.teacher_subject.teacher.user
            session, _ = LessonSession.objects.get_or_create(
                timetable_entry=entry,
                lesson_date=lesson_dates[entry.period.sequence - 1],
                defaults={
                    "started_at": timezone.make_aware(datetime.combine(lesson_dates[entry.period.sequence - 1], entry.period.start_time)),
                    "ended_at": timezone.make_aware(datetime.combine(lesson_dates[entry.period.sequence - 1], entry.period.end_time)),
                    "teacher": teacher_user,
                    "status": "COMPLETED",
                    "remarks": "Demo lesson completed successfully.",
                },
            )
            lesson_sessions.append(session)

        attendance_count = 0
        for session in lesson_sessions:
            register, _ = AttendanceRegister.objects.get_or_create(
                lesson_session=session,
                defaults={"status": "SUBMITTED", "submitted_at": timezone.now()},
            )
            code = session.timetable_entry.classroom.school.short_name
            class_enrollments = [e for e in enrollments.values() if e.classroom_id == session.timetable_entry.classroom_id]
            statuses = ["PRESENT", "LATE", "ABSENT"]
            for index, enrollment in enumerate(class_enrollments):
                AttendanceRecord.objects.get_or_create(
                    attendance_register=register,
                    enrollment=enrollment,
                    defaults={"status": statuses[index % len(statuses)], "remarks": "Demo attendance record."},
                )
                attendance_count += 1

        assessments = []
        for session in lesson_sessions[:2]:
            assessment, _ = Assessment.objects.get_or_create(
                lesson_session=session,
                teacher=session.timetable_entry.teacher_subject.teacher,
                title=f"{session.timetable_entry.teacher_subject.subject.name} Practice Assessment",
                defaults={
                    "description": "Demo assessment used to exercise the assessment workflow.",
                    "assessment_type": "ASSIGNMENT",
                    "status": "PUBLISHED",
                    "due_date": session.lesson_date + timedelta(days=7),
                    "maximum_score": Decimal("100.00"),
                    "allow_resubmission": True,
                },
            )
            assessments.append(assessment)

            class_enrollments = [e for e in enrollments.values() if e.classroom_id == session.timetable_entry.classroom_id]
            for index, enrollment in enumerate(class_enrollments[:2]):
                submission, _ = AssessmentSubmission.objects.get_or_create(
                    assessment=assessment,
                    enrollment=enrollment,
                    defaults={
                        "submitted_at": timezone.now(),
                        "submission_text": "This is a demo student submission.",
                        "submission_url": "https://example.com/demo-submission",
                        "status": "GRADED",
                        "is_late": index == 1,
                        "teacher_notes": "Good effort. Demo feedback for testing.",
                        "submitted_by": enrollment.student.user,
                    },
                )
                AssessmentEvaluation.objects.get_or_create(
                    submission=submission,
                    defaults={
                        "total_score": Decimal("82.00") - Decimal(index * 7),
                        "percentage": Decimal("82.00") - Decimal(index * 7),
                        "narrative_feedback": "Demonstrates good understanding of the assessed learning objective.",
                        "published": True,
                        "published_at": timezone.now(),
                    },
                )

        portfolio_count = 0
        for student in students.values():
            portfolio, _ = Portfolio.objects.get_or_create(
                student=student,
                defaults={"summary": "Demo learner portfolio showing project work, assessment evidence, and progress."},
            )
            item, _ = PortfolioItem.objects.get_or_create(
                portfolio=portfolio,
                title="STEM Investigation Project",
                defaults={
                    "lesson_session": lesson_sessions[0] if lesson_sessions else None,
                    "assessment_submission": None,
                    "item_type": "PROJECT",
                    "description": "A demo project item for portfolio testing.",
                    "event_date": date(2026, 2, 5),
                },
            )
            portfolio_count += 1

        event_count = 0
        for code, school in schools.items():
            event_specs = [
                ("Term 1 Parent Meeting", "MEETING", datetime(2026, 2, 14, 9, 0), datetime(2026, 2, 14, 11, 0), "Main Hall"),
                ("Science Project Exhibition", "ACTIVITY", datetime(2026, 3, 12, 10, 0), datetime(2026, 3, 12, 13, 0), "Science Lab"),
            ]
            for title, event_type, start, end, location in event_specs:
                CalendarEvent.objects.get_or_create(
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
                        "description": "Demo calendar event for testing.",
                        "is_active": True,
                    },
                )
                event_count += 1

        communication_count = 0
        notification_count = 0
        for code, school in schools.items():
            admin = admin_users[code]
            school_users = [admin] + teacher_by_code[code]
            for recipient in school_users:
                CommunicationMessage.objects.get_or_create(
                    school=school,
                    sender=admin,
                    recipient=recipient,
                    subject="Welcome to the demo school workspace",
                    defaults={"body": "This message is seeded data for testing communication workflows."},
                )
                Notification.objects.get_or_create(
                    school=school,
                    recipient=recipient,
                    title="Demo notification",
                    defaults={
                        "notification_type": "SYSTEM",
                        "body": "This notification confirms that seeded school data is available.",
                        "link": "/",
                    },
                )
                communication_count += 1
                notification_count += 1

        return {
            "Schools": 2,
            "System administrators": 1,
            "School administrators": len(admin_users),
            "Curricula": Curriculum.objects.count(),
            "Programmes": Programme.objects.count(),
            "Cambridge stages": CambridgeStage.objects.count(),
            "Montessori levels": len(montessori),
            "Subjects": Subject.objects.count(),
            "Stage-subject links": StageSubject.objects.count(),
            "Academic years": len(academic_years),
            "Terms": len(terms),
            "Classrooms": len(classrooms),
            "Teachers": len(teachers),
            "Teacher-subject assignments": TeacherSubject.objects.filter(id__in=[x.id for x in teacher_subjects]).count(),
            "Classroom teacher assignments": ClassroomTeacherAssignment.objects.filter(classroom__school__short_name__in=schools.keys()).count(),
            "Students": len(students),
            "Parents": len(parents),
            "Parent-student relationships": ParentStudentRelationship.objects.count(),
            "Enrollments": len(enrollments),
            "Periods": Period.objects.filter(school__short_name__in=schools.keys()).count(),
            "Timetables": len(timetables),
            "Timetable entries": len(entries),
            "Lesson sessions": len(lesson_sessions),
            "Attendance records": attendance_count,
            "Assessments": len(assessments),
            "Assessment evaluations": AssessmentEvaluation.objects.filter(submission__assessment__in=assessments).count(),
            "Portfolio records": portfolio_count,
            "Calendar events": event_count,
            "Communication messages": communication_count,
            "Notifications": notification_count,
            "System administrator account": system_admin.email,
        }
