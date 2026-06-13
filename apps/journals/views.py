from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView
from apps.journals.forms import JournalEntryForm
from apps.journals.models import JournalEntry, AIAnalysis
from apps.journals.services.journal_service import JournalService


class WriteJournalView(LoginRequiredMixin, FormView):
    template_name = "apps/journals/write.html"
    form_class = JournalEntryForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        content = form.cleaned_data["content"]
        
        # Service layer handles saving, safety analysis, and AI analysis
        entry, safety_level, alert = JournalService.create_and_analyze_journal(
            self.request.user, content
        )

        if safety_level == "CRITICAL":
            messages.error(
                self.request,
                "We noticed you might be going through a tough time. Please check the support resources below.",
            )
            # Redirect to emergency support view
            return redirect("crisis_support")
        elif safety_level == "WARNING":
            messages.warning(
                self.request,
                "Journal saved. We detected high levels of distress. Please take care of yourself.",
            )
        else:
            messages.success(self.request, "Journal entry saved and analyzed successfully!")

        return super().form_valid(form)


class JournalHistoryView(LoginRequiredMixin, ListView):
    model = JournalEntry
    template_name = "apps/journals/history.html"
    context_object_name = "journals"
    paginate_by = 10

    def get_queryset(self):
        # Prefetch the related AI analysis to avoid N+1 queries
        return JournalEntry.objects.filter(user=self.request.user).select_related("analysis")


class JournalDetailView(LoginRequiredMixin, DetailView):
    model = JournalEntry
    template_name = "apps/journals/detail.html"
    context_object_name = "journal"

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user).select_related("analysis")
