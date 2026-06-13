from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView
from apps.accounts.forms import RegistrationForm, ProfileForm
from apps.accounts.services.account_service import AccountService
from apps.safety.models import AuditLog


class LoginView(DjangoLoginView):
    template_name = "apps/accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(
            user=self.request.user,
            action="Successful user login",
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )
        return response


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action="User logout",
                ip_address=request.META.get("REMOTE_ADDR"),
            )
        return super().dispatch(request, *args, **kwargs)


class RegisterView(FormView):
    template_name = "apps/accounts/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Create user
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()

        # Service layer handles profile creation
        exam_type = form.cleaned_data["exam_type"]
        AccountService.create_user_profile(user, exam_type.id)

        # Log user in
        login(self.request, user)
        
        AuditLog.objects.create(
            user=user,
            action="New user registration and auto-login",
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile = getattr(request.user, "profile", None)
        initial = {}
        if profile and profile.exam_type:
            initial["exam_type"] = profile.exam_type

        form = ProfileForm(initial=initial)
        return render(request, "apps/accounts/profile.html", {"form": form, "profile": profile})

    def post(self, request):
        form = ProfileForm(request.POST)
        if form.is_valid():
            exam_type = form.cleaned_data["exam_type"]
            AccountService.update_profile(request.user, exam_type.id)
            return redirect("dashboard")

        return render(request, "apps/accounts/profile.html", {"form": form})
