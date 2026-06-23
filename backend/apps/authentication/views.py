from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario", max_length=150)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)


def login_view(request):
    """Vista de inicio de sesión.

    Mantiene toda la lógica de seguridad dentro de apps/authentication.
    """
    if request.user.is_authenticated:
        return redirect("/dashboard/")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/dashboard/")

            messages.error(request, "Credenciales inválidas.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    """Cierra sesión y redirige a login."""
    logout(request)
    return redirect("/api/auth/login/")

