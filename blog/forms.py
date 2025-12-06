from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Comment, Post, Profile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "featured_image", "category", "status"]


class CommentForm(forms.ModelForm):
    website = forms.CharField(  # honeypot
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Comment
        fields = ["content"]

    def clean(self):
        cleaned = super().clean()
        # If bots fill hidden field, reject
        if cleaned.get("website"):
            raise forms.ValidationError("Spam detected.")
        return cleaned


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Needed for password resets and important notices.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("That email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            Profile.objects.get_or_create(user=user)
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "avatar", "location"]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "Tell us a bit about you…",
                }
            ),
            "location": forms.TextInput(
                attrs={"placeholder": "City, Country"},
            ),
        }
        help_texts = {
            "avatar": "JPG/PNG/WEBP, up to 2MB."
        }

    def clean_avatar(self):
        f = self.cleaned_data.get("avatar")
        if not f:
            return f
        if f.size > 2 * 1024 * 1024:  # 2MB
            raise forms.ValidationError("Avatar must be 2MB or less.")
        valid_types = {"image/jpeg", "image/png", "image/webp"}
        ct = getattr(f, "content_type", None)
        if ct and ct not in valid_types:
            raise forms.ValidationError("Use JPG, PNG, or WEBP.")
        return f
