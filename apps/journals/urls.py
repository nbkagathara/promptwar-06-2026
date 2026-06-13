from django.urls import path
from apps.journals.views import WriteJournalView, JournalHistoryView, JournalDetailView

urlpatterns = [
    path("write/", WriteJournalView.as_view(), name="write_journal"),
    path("history/", JournalHistoryView.as_view(), name="journal_history"),
    path("<int:pk>/", JournalDetailView.as_view(), name="journal_detail"),
]
