from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView

from realtimeMonitoringAuthService.forms import LoginForm


class LoginView(TemplateView):
    http_method_names = ["get", "post"]

    def post(self, request):
        form = LoginForm(request.POST or None)
        if request.POST and form.is_valid():
            try:
                user = form.login(request)
                if user:
                    login(request, user)
                    return HttpResponseRedirect("/")
            except Exception as e:
                print("Login error", e)
        errors = ""
        for e in form.errors.values():
            errors += str(e[0])

        return render(
            request,
            "login.html",
            {
                "errors": errors,
                "username": form.cleaned_data["username"],
                "password": form.cleaned_data["password"],
            },
        )


class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/")