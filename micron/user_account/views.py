from django.contrib.auth import get_user_model
from django.http import HttpRequest

from common.views import TitleMixin
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import (
    HttpResponseRedirect,
    get_object_or_404,
    redirect,
    render,
    reverse,
)
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView
from orders.forms import OrderCreateForm
from orders.models import Order
from user_account.forms import (
    ContactForm,
    PasswordChangingForm,
    UserLoginForm,
    UserProfileForm,
    UserRegistrationForm,
    UserUpdateForm,
)
from user_account.models.contact import Contact
from user_account.models.email_verification import EmailVerification
from user_account.models.profile import Profile


class UserLoginView(TitleMixin, SuccessMessageMixin, LoginView):
    """Handle user authentication and login with remember me option."""

    model = get_user_model()
    template_name = "user_account/login.html"
    form_class = UserLoginForm
    success_message = _("You were successfully logged in")
    title = "| Login"
    success_url = reverse_lazy("products:products")

    def form_valid(self, form):
        """Process valid login form and handle remember me functionality."""
        remember_me = form.cleaned_data["remember_me"]
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super(UserLoginView, self).form_valid(form)


@login_required
def profile(request: HttpRequest, profile_id: int):
    """Display and update user profile information."""

    profile = get_object_or_404(Profile, id=profile_id)
    user = profile.user

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_account:profile', request.user.profile.id)
    else:
        form = UserProfileForm(instance=user)

    context = {"title": "| Profile", "form": form, "user": user}
    return render(request, "user_account/profile.html", context)


@login_required
def manage_shipping(request: HttpRequest):
    """Manage user shipping address and delivery preferences."""

    try:
        shipping = Order.objects.filter(user=request.user.id).latest("created_at")
    except Order.DoesNotExist:
        shipping = None
    form = OrderCreateForm(instance=shipping)
    if request.method == "POST":
        form = OrderCreateForm(request.POST, instance=shipping)
        if form.is_valid():
            shipping_user = form.save(commit=False)
            shipping_user.user = request.user
            shipping_user.save()
            return redirect("user_account:profile", request.user.profile.id)

    context = {"title": "| Manage Shipping", "form": form}
    return render(request, "user_account/manage_shipping.html", context)


@login_required
def profile_management(request: HttpRequest):
    """Update user profile settings and preferences."""

    user_form = UserUpdateForm(instance=request.user.profile)
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid():
            user_form.save()
            return redirect("user_account:profile", request.user.profile.id)
    context = {"title": "| Profile Management", "user_form": user_form}
    return render(request, "user_account/profile_management.html", context)


class DeleteAccountView(LoginRequiredMixin, SuccessMessageMixin, TitleMixin, DeleteView):
    """Permanently delete user account and all associated data."""

    model = get_user_model()
    template_name = "user_account/delete_account.html"
    success_url = reverse_lazy("products:products")
    success_message = _("Your account was successfully deleted")
    title = _("| Delete account")

    def get_object(self, queryset=None):
        return self.request.user


class UserRegistrationView(TitleMixin, SuccessMessageMixin, CreateView):
    """Handle new user registration and account creation."""

    model = get_user_model()
    form_class = UserRegistrationForm
    template_name = "user_account/registration/registration.html"
    success_url = reverse_lazy("user_account:login")
    success_message = _("Your account was successfully created")
    title = _("| Registration")


class ResetPasswordView(TitleMixin, SuccessMessageMixin, PasswordResetView):
    """Send password reset email to user."""

    template_name = "user_account/password/password_reset.html"
    email_template_name = "user_account/password/password_reset_email.txt"
    subject_template_name = "user_account/password/password_reset_subject.html"
    success_message = _(
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("user_account:login")
    title = _("| Reset Password")


class ChangePasswordView(TitleMixin, SuccessMessageMixin, PasswordChangeView):
    """Allow authenticated user to change their password."""

    template_name = "user_account/password/password_change.html"
    form_class = PasswordChangingForm
    success_message = _("Your password was successfully changed")
    success_url = reverse_lazy("user_account:login")
    title = "| Change Password"


class EmailVerificationView(TitleMixin, TemplateView):
    """Verify user email address via confirmation link."""

    title = _("| Email Verification")
    template_name = "user_account/registration/email_verification.html"

    def get(self, request, *args, **kwargs):
        """Validate email verification code and activate user email."""

        code = kwargs["code"]
        user = get_user_model().objects.get(email=kwargs["email"])
        email_verifications = EmailVerification.objects.filter(user=user, code=code)
        if (email_verifications.exists() and
                not email_verifications.first().is_expired()):
            user.is_verified_email = True
            user.profile.is_email_verified = True
            user.save()
            user.profile.save()
            return super(EmailVerificationView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse("products:products"))


def logout(request: HttpRequest) -> HttpResponseRedirect:
    """Log out user and clear session data."""

    try:
        for key in list(request.session.keys()):
            if key == "session_key":
                continue
            else:
                del request.session[key]
    except KeyError:
        pass
    messages.success(request, _("Logout Success"))
    auth.logout(request)
    return redirect("products:products")


class ContactView(TitleMixin, SuccessMessageMixin, CreateView):
    """Handle contact form submission and save user messages."""

    model = Contact
    form_class = ContactForm
    template_name = "user_account/contact.html"
    success_url = reverse_lazy("user_account:contact")
    success_message = _("Your message was successfully sent")
    title = _("| Contact US")
