from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from apps.moods.models import MoodLog
from apps.journals.models import JournalEntry
from apps.notifications.models import Notification


class Command(BaseCommand):
    help = "Sends daily reminders to users who have not logged their mood or journal today."

    def handle(self, *args, **options):
        today = timezone.now().date()
        users = User.objects.filter(is_active=True)
        reminders_sent = 0

        for user in users:
            # 1. Check if mood is logged today
            mood_logged = MoodLog.objects.filter(user=user, logged_date=today).exists()
            
            # 2. Check if journal is logged today
            journal_logged = JournalEntry.objects.filter(
                user=user, created_at__date=today
            ).exists()

            msg = ""
            if not mood_logged and not journal_logged:
                msg = "Hi! You haven't logged your mood or journal today. Take 2 minutes to check in with AuraWell."
            elif not mood_logged:
                msg = "Hi! Remember to record your daily mood, sleep, and energy levels on AuraWell today."
            elif not journal_logged:
                msg = "Hi! You logged your mood but haven't written a reflection yet. Spill your thoughts today!"

            if msg:
                # Create notification record in DB
                Notification.objects.create(
                    user=user,
                    message=msg,
                    is_sent=True,
                    send_at=timezone.now(),
                )
                reminders_sent += 1
                self.stdout.write(self.style.SUCCESS(f"Reminder queued for {user.username}"))

        self.stdout.write(self.style.SUCCESS(f"Finished sending {reminders_sent} daily reminders."))
