from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from user_account.models import Contact, Profile, User
from user_account.tasks import send_email_verification


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control py-2",
                "placeholder": "Enter username or email",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control py-2 js-password-input", "placeholder": "Enter password"}
        )
    )
    remember_me = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = User
        fields = "__all__"


class UserProfileForm(UserChangeForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter first_name"}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter last_name"}
        )
    )
    image = forms.ImageField(
        required=False,
    )
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control py-2",
                "placeholder": "Enter username",
                "readonly": True,
            }
        )
    )
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control py-2",
                "placeholder": "Enter gmail",
                "readonly": True,
            }
        )
    )

    is_email_verified = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
                "disabled": True,
            }
        ),
        required=False,
    )

    created_at = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "class": "form-control py-2",
                "readonly": True,
            }
        ),
        required=False,
    )

    class Meta:
        model = Profile
        fields = ("first_name", "last_name", "image", "username", "email", "is_email_verified", "created_at")


class UserUpdateForm(forms.ModelForm):
    password = None

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter username"}
        )
    )
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter gmail"}
        )
    )

    class Meta:
        model = Profile
        fields = ["username", "email"]
        exclude = ["password1", "password2"]


    def clean_email(self):
        data = self.cleaned_data["email"]

        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("Email already in use.")
        if len(data) >= 350:
            raise forms.ValidationError("Your email is too long")
        return data


class ContactForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter your fullname"}
        )
    )
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter your email"}
        )
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control py-2",
                "placeholder": "Enter your message",
                "style": "resize:none;",
            }
        )
    )

    class Meta:
        model = Contact
        fields = ("name", "email", "message")


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter First name"}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter Last name"}
        )
    )
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter username"}
        )
    )
    email = forms.CharField(
        widget=forms.EmailInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter gmail"}
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter password", "id": "js-first-password"}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control py-2", "placeholder": "Confirm password", "id": "js-second-password"}
        )
    )
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        )

    
    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password1"] != cd["password2"]:
            raise forms.ValidationError("Password1 don't match.")
        return cd["password1"]
        

    def clean_email(self):
        data = self.cleaned_data["email"]

        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("Email already in use.")
        if len(data) >= 350:
            raise forms.ValidationError("Your email is too long")
        return data

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=True)
        send_email_verification.delay(user.id)
        return user


class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter old password"}
        )
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control py-2", "placeholder": "Enter new password"}
        )
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control py-2",
                "placeholder": "Confirm password",
            }
        )
    )

    class Meta:
        model = User
        fields = ("old_password", "new_password1", "new_password2")
