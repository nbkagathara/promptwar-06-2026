import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from apps.analytics.services.analytics_service import AnalyticsService


class AnalyticsDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        days = int(request.GET.get("days", 7))
        trends = AnalyticsService.get_mood_trends(request.user, days=days)
        metrics = AnalyticsService.get_summary_metrics(request.user)

        context = {
            "days": days,
            "metrics": metrics,
            # Pass trends data serialized to JSON for Chart.js to consume safely
            "trends_json": json.dumps(trends),
        }
        return render(request, "apps/analytics/dashboard.html", context)
