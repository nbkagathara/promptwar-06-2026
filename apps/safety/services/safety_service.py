import logging
from django.contrib.auth.models import User
from apps.safety.models import SafetyAlert, AuditLog

logger = logging.getLogger("app")


class SafetyService:
    @staticmethod
    def get_active_crisis_alert(user: User) -> SafetyAlert:
        """
        Retrieves the latest unresolved CRITICAL safety alert.
        """
        return SafetyAlert.objects.filter(user=user, safety_level="CRITICAL", resolved=False).first()

    @staticmethod
    def resolve_alert(user: User, alert_id: int) -> SafetyAlert:
        """
        Marks a safety alert as resolved.
        """
        try:
            alert = SafetyAlert.objects.get(id=alert_id, user=user)
            alert.resolved = True
            alert.save()
            AuditLog.objects.create(
                user=user,
                action=f"Resolved safety alert {alert_id} (Level: {alert.safety_level})",
            )
            return alert
        except SafetyAlert.DoesNotExist:
            logger.error(f"SafetyAlert {alert_id} not found for user {user.username}")
            raise ValueError("Alert not found")
