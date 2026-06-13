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
        
        # New health trends & wellness score summary
        health_trends = AnalyticsService.get_health_trends(request.user, days=days)
        wellness = AnalyticsService.get_wellness_summary(request.user)
        
        # Admin cohort-level analytics
        cohort = None
        if request.user.is_staff:
            cohort = AnalyticsService.get_cohort_analytics()

        context = {
            "days": days,
            "metrics": metrics,
            "wellness": wellness,
            "cohort": cohort,
            "trends_json": json.dumps(trends),
            "health_json": json.dumps(health_trends),
        }
        return render(request, "apps/analytics/dashboard.html", context)

