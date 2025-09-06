from django.http import HttpRequest

from common.views import TitleMixin
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
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
from django.views.generic import CreateView, TemplateView
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
from user_account.models import EmailVerification, Profile, User


class UserLoginView(TitleMixin, SuccessMessageMixin, LoginView):
    model = User
    template_name = "user_account/login.html"
    form_class = UserLoginForm
    success_message = _("You were successfully logged in")
    title = "| Login"
    success_url = reverse_lazy("products:products")

    def form_valid(self, form):
        remember_me = form.cleaned_data["remember_me"]
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super(UserLoginView, self).form_valid(form)


@login_required
def profile(request: HttpRequest, profile_id: int):
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
    try:
        shipping = Order.objects.filter(user=request.user.id).latest("created")
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
    user_form = UserUpdateForm(instance=request.user.profile)
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid():
            user_form.save()
            return redirect("user_account:profile", request.user.profile.id)
    context = {"title": "| Profile Management", "user_form": user_form}
    return render(request, "user_account/profile_management.html", context)


@login_required
def delete_account(request: HttpRequest):
    user = get_object_or_404(User, id=request.user.id)
    if request.method == "POST":
        messages.success(request, _("Your account was successfully deleted"))
        user.delete()
        return redirect("products:products")
    context = {"title": "| Delete account"}
    return render(request, "user_account/delete_account.html", context)


class UserRegistrationView(TitleMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "user_account/registration/registration.html"
    success_url = reverse_lazy("user_account:login")
    success_message = _("Your account was successfully created")
    title = "| Registration"


class ResetPasswordView(TitleMixin, SuccessMessageMixin, PasswordResetView):
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
    title = "| Reset Password"


class ChangePasswordView(TitleMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = "user_account/password/password_change.html"
    form_class = PasswordChangingForm
    success_message = _("Your password was successfully changed")
    success_url = reverse_lazy("user_account:login")
    title = "| Change Password"


class EmailVerificationView(TitleMixin, TemplateView):
    title = "| Email Verification"
    template_name = "user_account/registration/email_verification.html"

    def get(self, request, *args, **kwargs):
        code = kwargs["code"]
        user = User.objects.get(email=kwargs["email"])
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


def contact(request: HttpRequest):
    form = ContactForm()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your message was successfully sent"))
            return redirect("products:products")
        else:
            messages.error(request, _("Please correct the error below"))
    context = {"title": "| Contact US", "form": form}
    return render(request, "user_account/contact.html", context)
