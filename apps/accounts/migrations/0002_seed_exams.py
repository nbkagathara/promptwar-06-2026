from django.db import migrations


def seed_exam_types(apps, schema_editor):
    ExamType = apps.get_model("accounts", "ExamType")
    exams = [
        ("NEET", "National Eligibility cum Entrance Test for medical studies"),
        ("JEE", "Joint Entrance Examination for engineering"),
        ("UPSC", "Union Public Service Commission civil services"),
        ("CAT", "Common Admission Test for MBA admissions"),
        ("GATE", "Graduate Aptitude Test in Engineering"),
        ("CUET", "Common University Entrance Test"),
        ("SSC", "Staff Selection Commission recruitment"),
        ("Banking", "Banking probationary officer and clerk exams"),
    ]
    for name, desc in exams:
        ExamType.objects.get_or_create(name=name, defaults={"description": desc})


def reverse_seed(apps, schema_editor):
    ExamType = apps.get_model("accounts", "ExamType")
    ExamType.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_exam_types, reverse_seed),
    ]
