from django.contrib.auth.models import User
from apps.accounts.models import Profile, ExamType
from apps.safety.models import AuditLog


class AccountService:
    @staticmethod
    def create_user_profile(user: User, exam_type_id: int = None) -> Profile:
        """
        Creates a profile linked to the User.
        """
        exam_type = None
        if exam_type_id:
            try:
                exam_type = ExamType.objects.get(id=exam_type_id)
            except ExamType.DoesNotExist:
                pass

        profile, created = Profile.objects.get_or_create(user=user)
        if exam_type:
            profile.exam_type = exam_type
            profile.save()

        AuditLog.objects.create(user=user, action=f"Profile created/updated with exam type: {exam_type}")
        return profile

    @staticmethod
    def update_profile(user: User, exam_type_id: int) -> Profile:
        """
        Updates the target exam type for the user.
        """
        profile, _ = Profile.objects.get_or_create(user=user)
        try:
            exam_type = ExamType.objects.get(id=exam_type_id)
            profile.exam_type = exam_type
            profile.save()
            AuditLog.objects.create(user=user, action=f"Profile exam type updated to: {exam_type.name}")
        except ExamType.DoesNotExist:
            raise ValueError("Invalid Exam Type")
        return profile
