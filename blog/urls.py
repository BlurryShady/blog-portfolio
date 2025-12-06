from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .feeds import LatestPostsRSS, LatestPostsAtom

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("category/", views.category_list, name="category_list"),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("post/new/", views.post_create, name="post_create"),
    path("post/<slug:slug>/edit/", views.post_edit, name="post_edit"),
    path("post/<slug:slug>/delete/", views.post_delete, name="post_delete"),
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
    path("login/",  auth_views.LoginView.as_view(template_name="blog/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("blog:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("blog:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("u/<str:username>/", views.profile_detail, name="profile_detail"),
    path(
        "comment/<int:pk>/delete/",
        views.comment_delete,
        name="comment_delete",
    ),
    path("feed/", LatestPostsRSS(), name="feed_rss"),
    path("feed/atom/", LatestPostsAtom(), name="feed_atom"),
]
