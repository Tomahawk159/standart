from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.views.generic import CreateView

from users.forms import UserLoginForm, UserRegistrationForm
from users.models import User


class LoginView(DjangoLoginView):
    form_class = UserLoginForm
    template_name = '.signing/login.html'
    success_url = settings.LOGIN_REDIRECT_URL


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = '.signing/register.html'
    success_url = settings.LOGIN_REDIRECT_URL

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # авторизуем пользователя после успешной регистрации
        return response


class LogoutView(DjangoLogoutView):
    ...
