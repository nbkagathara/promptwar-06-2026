from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.http import JsonResponse
import json
from apps.ai_coach.services.coach_service import CoachService


class CoachGuidanceView(LoginRequiredMixin, View):
    def get(self, request):
        recommendations = CoachService.get_latest_recommendations(request.user, limit=8)
        return render(request, "apps/ai_coach/guidance.html", {"recommendations": recommendations})

    def post(self, request):
        try:
            CoachService.generate_user_coach_guidance(request.user)
            messages.success(request, "AI Coach updated successfully with fresh recommendations!")
        except Exception as e:
            messages.error(request, f"Could not update guidance: {str(e)}")

        return redirect("coach_guidance")


class CoachChatView(LoginRequiredMixin, View):
    def get(self, request):
        chat_messages = CoachService.get_chat_history(request.user)
        return render(request, "apps/ai_coach/chat.html", {"chat_messages": chat_messages})

    def post(self, request):
        try:
            if request.content_type == "application/json":
                body = json.loads(request.body.decode("utf-8"))
                user_msg_content = body.get("message", "").strip()
            else:
                user_msg_content = request.POST.get("message", "").strip()

            if not user_msg_content:
                if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
                    return JsonResponse({"error": "Empty message"}, status=400)
                messages.warning(request, "Cannot send an empty message.")
                return redirect("coach_chat")

            res_data = CoachService.send_chat_message(request.user, user_msg_content)

            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
                return JsonResponse({
                    "user_message": {
                        "content": res_data["user_message"].content,
                        "created_at": res_data["user_message"].created_at.strftime("%I:%M %p"),
                    },
                    "assistant_message": {
                        "content": res_data["assistant_message"].content,
                        "created_at": res_data["assistant_message"].created_at.strftime("%I:%M %p"),
                    },
                    "safety_escalation": res_data["safety_escalation"]
                })

            if res_data["safety_escalation"]:
                messages.error(request, "Safety warning: Please consult crisis support resources if you feel overwhelmed.")

            return redirect("coach_chat")
        except Exception as e:
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json":
                return JsonResponse({"error": str(e)}, status=500)
            messages.error(request, f"Error sending message: {str(e)}")
            return redirect("coach_chat")

