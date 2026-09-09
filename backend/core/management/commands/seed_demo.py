from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.academics.models import (
    AcademicYear,
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
from apps.enrollment.models import Enrollment
from apps.identity.models import User
from apps.lessons.models import LessonSession
from apps.schools.models import School, SchoolAdministrator
from apps.teachers.models import Department, Teacher, TeacherSubject
from apps.timetables.models import Period, Timetable, TimetableEntry
from apps.students.models import Student
from core.constants.assessment import AssessmentStatus, AssessmentType, SubmissionStatus
from core.constants.attendance import AttendanceStatus, RegisterStatus
from core.constants.enrollment import EnrollmentStatus
from core.constants.lesson import LessonStatus
from core.constants.student import Gender
from core.constants.teacher import TeacherRole, EmploymentType, TeacherStatus
from core.constants.timetable import TimetableStatus, WeekDay


DEMO_SCHOOL = "Nairobi International Montessori & STEM Academy"
DEMO_SHORT_NAME = "NIMSA-DEMO"
DEMO_DOMAIN = "@key-demo.test"
PASSWORDS = {
    "admin": "DemoAdmin123!",
    "teacher": "DemoTeacher123!",
    "student": "DemoStudent123!",
}


class Command(BaseCommand):
    help = "Create a complete, isolated demo school dataset for end-to-end testing."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Remove the existing KEY demo school dataset before recreating it.")

    def handle(self, *args, **options):
        # Do not keep reset and the entire seed operation inside one long-lived
        # transaction. A long transaction can retain locks while the seeder is
        # creating dependent records, which can make PostgreSQL appear to hang.
        if options["reset"]:
            self.reset_demo_data()

        phases = [
            ("school", self.seed_school),
        ]
        school = self.seed_school()
        self.stdout.write("  ✓ School")
        academic_year = self.seed_academics(school)
        self.stdout.write("  ✓ Academic year")
        terms = self.seed_terms(academic_year)
        self.stdout.write("  ✓ Terms")
        departments = self.seed_departments(school)
        self.stdout.write("  ✓ Departments")
        admin = self.seed_admin(school)
        self.stdout.write("  ✓ Admin")
        teachers = self.seed_teachers(school, departments)
        self.stdout.write("  ✓ Teachers")
        curriculum, stages, subjects = self.seed_curriculum()
        self.stdout.write("  ✓ Curriculum and subjects")
        classrooms = self.seed_classrooms(school, academic_year, terms, stages)
        self.stdout.write("  ✓ Classrooms")
        self.seed_teacher_assignments(teachers, classrooms, academic_year, terms, subjects)
        self.stdout.write("  ✓ Teacher subject and homeroom assignments")
        students = self.seed_students(school)
        self.stdout.write("  ✓ Students")
        enrollments = self.seed_enrollments(students, classrooms, academic_year, terms)
        self.stdout.write("  ✓ Enrollments")
        periods = self.seed_periods(school)
        self.stdout.write("  ✓ Periods")
        self.seed_timetables_and_learning_data(school, academic_year, terms, classrooms, teachers, subjects, enrollments, periods)
        self.stdout.write("  ✓ Timetables, lessons, attendance and assessments")
        self.stdout.write(self.style.SUCCESS("\nDemo dataset created successfully."))
        self.stdout.write(f"School: {school.name} ({school.short_name})")
        self.stdout.write("\nLOGIN ACCOUNTS (development/test only):")
        self.stdout.write(f"  Admin: admin@key-demo.test / {PASSWORDS['admin']}")
        for key, label in [("math", "Math teacher"), ("science", "Science teacher"), ("english", "English teacher"), ("montessori", "Montessori teacher")]:
            self.stdout.write(f"  {label}: teacher.{key}@key-demo.test / {PASSWORDS['teacher']}")
        self.stdout.write("  Students: student01@key-demo.test … student16@key-demo.test / " + PASSWORDS["student"])

    def seed_school(self):
        school, _ = School.objects.update_or_create(short_name=DEMO_SHORT_NAME, defaults={"name": DEMO_SCHOOL, "email": "admin@key-demo.test", "phone_number": "+254700000001", "website": "https://demo.key.test", "address": "Westlands, Nairobi", "city": "Nairobi", "country": "Kenya", "timezone": "Africa/Nairobi", "is_active": True})
        return school

    def seed_academics(self, school):
        return AcademicYear.objects.update_or_create(school=school, name="2026", defaults={"start_date": date(2026, 1, 5), "end_date": date(2026, 12, 11), "is_current": True, "is_active": True})[0]

    def seed_terms(self, year):
        specs = [(1, date(2026, 1, 5), date(2026, 4, 3), False), (2, date(2026, 5, 4), date(2026, 8, 21), False), (3, date(2026, 9, 1), date(2026, 12, 11), True)]
        return [Term.objects.update_or_create(academic_year=year, term_number=n, defaults={"start_date": start, "end_date": end, "is_current": current, "is_active": True})[0] for n, start, end, current in specs]

    def seed_departments(self, school):
        specs = [("Mathematics", "MATH", "Mathematics and numeracy"), ("Science & STEM", "STEM", "Science, computing and practical STEM learning"), ("Languages", "LANG", "English language and literacy"), ("Early Years & Montessori", "EY", "Early years and Montessori learning")]
        return {code: Department.objects.update_or_create(school=school, code=code, defaults={"name": name, "description": description, "is_active": True})[0] for name, code, description in specs}

    def user(self, email, first, last, phone=""):
        user, _ = User.objects.update_or_create(email=email, defaults={"first_name": first, "last_name": last, "phone_number": phone, "status": "ACTIVE", "is_active": True, "preferred_language": "en", "timezone": "Africa/Nairobi"})
        return user

    def set_password(self, user, password):
        user.set_password(password)
        user.save(update_fields=["password"])

    def seed_admin(self, school):
        user = self.user("admin@key-demo.test", "Grace", "Wanjiku", "+254700000010")
        user.is_staff = True
        user.is_superuser = False
        self.set_password(user, PASSWORDS["admin"])
        SchoolAdministrator.objects.update_or_create(user=user, defaults={"school": school, "is_active": True})
        return user

    def seed_teachers(self, school, departments):
        specs = [("math", "Daniel", "Mwangi", "MATH", "T-MATH-001"), ("science", "Aisha", "Otieno", "STEM", "T-STEM-002"), ("english", "Peter", "Kamau", "LANG", "T-LANG-003"), ("montessori", "Lucy", "Njeri", "EY", "T-EY-004")]
        teachers = {}
        for key, first, last, department, employee_number in specs:
            user = self.user(f"teacher.{key}{DEMO_DOMAIN}", first, last, f"+2547110000{10 + len(teachers)}")
            self.set_password(user, PASSWORDS["teacher"])
            teacher, _ = Teacher.objects.update_or_create(user=user, defaults={"school": school, "employee_number": employee_number, "employment_type": EmploymentType.FULL_TIME, "employment_date": date(2022, 1, 10), "status": TeacherStatus.ACTIVE, "department": departments[department]})
            teachers[key] = teacher
        return teachers

    def seed_curriculum(self):
        curriculum, _ = Curriculum.objects.update_or_create(name="KEY Demo Curriculum", defaults={"description": "Test curriculum for role isolation and learning workflows.", "version": "2026.1", "is_active": True})
        programme, _ = Programme.objects.update_or_create(curriculum=curriculum, name="Cambridge Primary", defaults={"description": "Primary programme used by the demo school.", "display_order": 1, "is_active": True})
        stage_specs = [("Early Years", 0), ("Grade 1", 1), ("Grade 3", 3), ("Grade 5", 5)]
        stages = {number: CambridgeStage.objects.update_or_create(programme=programme, stage_number=number, defaults={"name": name, "display_order": i + 1, "is_active": True})[0] for i, (name, number) in enumerate(stage_specs)}
        subject_specs = [("Mathematics", "MATH", True), ("English", "ENG", True), ("Science", "SCI", True), ("Computing", "COMP", True), ("Global Perspectives", "GP", False), ("Art & Design", "ART", False), ("Physical Education", "PE", False), ("Montessori Practical Life", "MPL", True)]
        subjects = {code: Subject.objects.update_or_create(curriculum=curriculum, code=code, defaults={"name": name, "description": f"{name} demo subject", "is_core": core, "display_order": i + 1, "is_active": True})[0] for i, (name, code, core) in enumerate(subject_specs)}
        for stage_number, stage in stages.items():
            selected = ["MATH", "ENG", "SCI", "COMP", "PE"] if stage_number else ["ENG", "MPL", "MATH", "ART"]
            for order, code in enumerate(selected, 1):
                StageSubject.objects.update_or_create(cambridge_stage=stage, subject=subjects[code], defaults={"weekly_lessons": 5 if code in {"MATH", "ENG"} else 3, "is_core": subjects[code].is_core, "display_order": order, "is_active": True})
        return curriculum, stages, subjects

    def seed_classrooms(self, school, year, terms, stages):
        names = [("Pre-Primary 1", "PP1", 0), ("Grade 1", "G1", 1), ("Grade 3", "G3", 3), ("Grade 5", "G5", 5)]
        classrooms = {}
        for term in terms:
            for name, code, stage_number in names:
                classrooms[(term.term_number, code)] = Classroom.objects.update_or_create(school=school, academic_year=year, code=f"{code}-2026-T{term.term_number}", defaults={"term": term, "cambridge_stage": stages[stage_number], "name": name, "capacity": 24 if stage_number == 0 else 30, "is_active": True})[0]
        return classrooms

    def seed_teacher_assignments(self, teachers, classrooms, year, terms, subjects):
        mapping = {"math": [("G1", "MATH"), ("G3", "MATH")], "science": [("G3", "SCI"), ("G5", "SCI"), ("G5", "COMP")], "english": [("G1", "ENG"), ("G3", "ENG"), ("G5", "ENG")], "montessori": [("PP1", "MPL"), ("PP1", "ENG"), ("G1", "ART")]}
        homerooms = {"math": "G1", "science": "G3", "english": "G5", "montessori": "PP1"}
        for term in terms:
            for teacher_key, pairs in mapping.items():
                teacher = teachers[teacher_key]
                for class_code, subject_code in pairs:
                    classroom = classrooms[(term.term_number, class_code)]
                    TeacherSubject.objects.update_or_create(teacher=teacher, subject=subjects[subject_code], classroom=classroom, academic_year=year, term=term, defaults={"role": TeacherRole.LEAD, "start_date": term.start_date, "is_active": True})
                ClassroomTeacherAssignment.objects.update_or_create(teacher=teacher, classroom=classrooms[(term.term_number, homerooms[teacher_key])], role=ClassroomTeacherAssignment.Role.PRIMARY, defaults={"is_active": True})

    def seed_students(self, school):
        names = [("Amina", "Otieno", Gender.FEMALE), ("Brian", "Kamau", Gender.MALE), ("Chloe", "Wambui", Gender.FEMALE), ("David", "Kiptoo", Gender.MALE), ("Ethan", "Mwangi", Gender.MALE), ("Faith", "Njeri", Gender.FEMALE), ("Grace", "Achieng", Gender.FEMALE), ("Hassan", "Ali", Gender.MALE), ("Ivy", "Moraa", Gender.FEMALE), ("John", "Ochieng", Gender.MALE), ("Kevin", "Maina", Gender.MALE), ("Lydia", "Atieno", Gender.FEMALE), ("Mercy", "Nyambura", Gender.FEMALE), ("Noah", "Omondi", Gender.MALE), ("Olivia", "Kendi", Gender.FEMALE), ("Paul", "Kariuki", Gender.MALE)]
        students = []
        for index, (first, last, gender) in enumerate(names, 1):
            user = self.user(f"student{index:02d}{DEMO_DOMAIN}", first, last, f"+254720100{index:02d}")
            self.set_password(user, PASSWORDS["student"])
            student, _ = Student.objects.update_or_create(user=user, defaults={"school": school, "admission_number": f"DEMO-{index:03d}", "admission_date": date(2024, 1, 8), "date_of_birth": date(2015 if index <= 12 else 2016, (index % 12) + 1, (index % 20) + 1), "gender": gender, "nationality": "Kenyan", "birth_certificate_number": f"DEMOBC{index:05d}", "is_active": True})
            students.append(student)
        return students

    def seed_enrollments(self, students, classrooms, year, terms):
        cohorts = ["PP1", "G1", "G3", "G5"]
        enrollments = {}
        for term in terms:
            for index, student in enumerate(students):
                class_code = cohorts[index // 4]
                enrollment, _ = Enrollment.objects.update_or_create(student=student, academic_year=year, term=term, defaults={"classroom": classrooms[(term.term_number, class_code)], "enrollment_date": term.start_date, "status": EnrollmentStatus.ENROLLED, "remarks": "Demo enrollment for end-to-end testing."})
                enrollments[(term.term_number, student.id)] = enrollment
        return enrollments

    def seed_periods(self, school):
        specs = [(1, "Period 1", time(8, 0), time(8, 45), False), (2, "Period 2", time(8, 50), time(9, 35), False), (3, "Break", time(9, 35), time(9, 55), True), (4, "Period 3", time(9, 55), time(10, 40), False), (5, "Period 4", time(10, 45), time(11, 30), False)]
        return [Period.objects.update_or_create(school=school, sequence=sequence, defaults={"name": name, "start_time": start, "end_time": end, "is_break": is_break})[0] for sequence, name, start, end, is_break in specs]

    def seed_timetables_and_learning_data(self, school, year, terms, classrooms, teachers, subjects, enrollments, periods):
        teacher_subjects = list(TeacherSubject.objects.filter(academic_year=year).select_related("teacher", "subject", "classroom", "term"))
        for term in terms:
            timetable, _ = Timetable.objects.update_or_create(school=school, academic_year=year, term=term, version=1, defaults={"name": f"Demo Timetable Term {term.term_number}", "status": TimetableStatus.PUBLISHED if term.term_number == 3 else TimetableStatus.ARCHIVED, "effective_from": term.start_date, "effective_to": term.end_date})
            entries = []
            for idx, assignment in enumerate([x for x in teacher_subjects if x.term_id == term.id][:12]):
                entry, _ = TimetableEntry.objects.update_or_create(timetable=timetable, weekday=[WeekDay.MONDAY, WeekDay.TUESDAY, WeekDay.WEDNESDAY, WeekDay.THURSDAY, WeekDay.FRIDAY][idx % 5], period=periods[idx % len(periods)], classroom=assignment.classroom, defaults={"teacher_subject": assignment, "room": f"Room {101 + idx}"})
                entries.append(entry)
            for idx, entry in enumerate(entries):
                session_date = term.start_date + timedelta(days=min(idx + 7, max(0, (term.end_date - term.start_date).days)))
                session, _ = LessonSession.objects.update_or_create(timetable_entry=entry, lesson_date=session_date, defaults={"teacher": entry.teacher_subject.teacher.user, "status": LessonStatus.COMPLETED if idx < 6 else LessonStatus.SCHEDULED, "started_at": timezone.make_aware(datetime.combine(session_date, time(8, 0))) if idx < 6 else None, "ended_at": timezone.make_aware(datetime.combine(session_date, time(8, 45))) if idx < 6 else None, "remarks": "Completed demo lesson." if idx < 6 else "Upcoming demo lesson."})
                self.seed_attendance(session, term, enrollments)
                self.seed_assessments(session, entry.teacher_subject.teacher, entry.teacher_subject.subject, term, enrollments)

    def seed_attendance(self, session, term, enrollments):
        register, _ = AttendanceRegister.objects.update_or_create(lesson_session=session, defaults={"status": RegisterStatus.SUBMITTED if session.status == LessonStatus.COMPLETED else RegisterStatus.DRAFT, "submitted_at": timezone.now() if session.status == LessonStatus.COMPLETED else None})
        class_enrollments = [e for (term_number, _), e in enrollments.items() if term_number == term.term_number and e.classroom_id == session.timetable_entry.classroom_id]
        statuses = [AttendanceStatus.PRESENT, AttendanceStatus.PRESENT, AttendanceStatus.LATE, AttendanceStatus.ABSENT, AttendanceStatus.EXCUSED]
        for index, enrollment in enumerate(class_enrollments):
            AttendanceRecord.objects.update_or_create(attendance_register=register, enrollment=enrollment, defaults={"status": statuses[index % len(statuses)], "remarks": "Demo attendance record."})

    def seed_assessments(self, session, teacher, subject, term, enrollments):
        is_current = term.term_number == 3
        specs = [("Weekly Practice", AssessmentType.ASSIGNMENT, AssessmentStatus.PUBLISHED, 20), ("Concept Check Quiz", AssessmentType.QUIZ, AssessmentStatus.PUBLISHED, 10), ("Practical Project", AssessmentType.PROJECT, AssessmentStatus.DRAFT if is_current else AssessmentStatus.CLOSED, 50)]
        class_enrollments = [e for (term_number, _), e in enrollments.items() if term_number == term.term_number and e.classroom_id == session.timetable_entry.classroom_id]
        for title, assessment_type, status, maximum in specs:
            assessment, _ = Assessment.objects.update_or_create(lesson_session=session, title=title, defaults={"teacher": teacher, "description": f"{title} for {subject.name}. Designed to exercise the student submission and teacher grading workflow.", "assessment_type": assessment_type, "status": status, "due_date": session.lesson_date + timedelta(days=7), "maximum_score": Decimal(str(maximum)), "allow_resubmission": True})
            if status == AssessmentStatus.PUBLISHED:
                for index, enrollment in enumerate(class_enrollments):
                    submitted = index != 3
                    graded = submitted and index < 2
                    submission, _ = AssessmentSubmission.objects.update_or_create(assessment=assessment, enrollment=enrollment, defaults={"submitted_at": timezone.now() if submitted else None, "submission_text": f"Demo response from {enrollment.student.user.full_name}.", "status": SubmissionStatus.GRADED if graded else (SubmissionStatus.SUBMITTED if submitted else SubmissionStatus.DRAFT), "is_late": index == 2, "teacher_notes": "Good work. Review the feedback." if graded else "", "submitted_by": enrollment.student.user})
                    if graded:
                        score = Decimal(maximum) - Decimal(index * 2)
                        AssessmentEvaluation.objects.update_or_create(submission=submission, defaults={"total_score": score, "percentage": (score / Decimal(maximum)) * Decimal(100), "narrative_feedback": "Strong understanding demonstrated. Keep improving the explanation of your reasoning.", "published": True, "published_at": timezone.now()})

    def reset_demo_data(self):
        demo_users = User.objects.filter(email__endswith=DEMO_DOMAIN)
        demo_students = Student.objects.filter(user__in=demo_users)
        demo_teachers = Teacher.objects.filter(user__in=demo_users)
        demo_school = School.objects.filter(short_name=DEMO_SHORT_NAME).first()
        AssessmentEvaluation.objects.filter(submission__enrollment__student__in=demo_students).delete()
        AssessmentSubmission.objects.filter(enrollment__student__in=demo_students).delete()
        Assessment.objects.filter(lesson_session__timetable_entry__classroom__school=demo_school).delete()
        AttendanceRecord.objects.filter(enrollment__student__in=demo_students).delete()
        AttendanceRegister.objects.filter(lesson_session__timetable_entry__classroom__school=demo_school).delete()
        LessonSession.objects.filter(timetable_entry__classroom__school=demo_school).delete()
        TimetableEntry.objects.filter(timetable__school=demo_school).delete()
        Timetable.objects.filter(school=demo_school).delete()
        TeacherSubject.objects.filter(teacher__in=demo_teachers).delete()
        ClassroomTeacherAssignment.objects.filter(teacher__in=demo_teachers).delete()
        Enrollment.objects.filter(student__in=demo_students).delete()
        Student.objects.filter(pk__in=demo_students.values("pk")).delete()
        Teacher.objects.filter(pk__in=demo_teachers.values("pk")).delete()
        SchoolAdministrator.objects.filter(user__in=demo_users).delete()
        Period.objects.filter(school=demo_school).delete()
        Classroom.objects.filter(school=demo_school).delete()
        AcademicYear.objects.filter(school=demo_school).delete()
        Department.objects.filter(school=demo_school).delete()
        if demo_school:
            demo_school.delete()
        Curriculum.objects.filter(name="KEY Demo Curriculum").delete()
        User.objects.filter(email__endswith=DEMO_DOMAIN).delete()
        self.stdout.write(self.style.WARNING("Existing KEY demo dataset removed."))
