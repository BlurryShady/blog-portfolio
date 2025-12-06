from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm, ProfileForm, RegistrationForm
from .models import Category, Comment, Post, Profile


def home(request):
    posts = Post.objects.published()
    q = (request.GET.get("q") or "").strip()
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(content__icontains=q))

    paginator = Paginator(posts, 6)
    page = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(
        request,
        "blog/home.html",
        {
            "posts": page_obj.object_list,
            "page_obj": page_obj,
            "q": q,
        },
    )


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.visible_to(request.user), slug=slug)
    comments = post.comments.select_related("author").order_by("-created_at")
    form = CommentForm()

    is_preview = not post.is_public

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to comment.")
            login_url = f"{reverse('blog:login')}?next={request.path}"
            return redirect(login_url)

        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.post = post
            c.author = request.user
            c.save()
            messages.success(request, "Comment published.")
            return redirect(post.get_absolute_url())

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "is_preview": is_preview,
        },
    )


def category_list(request):
    cats = Category.objects.all()
    return render(request, "blog/category_list.html", {"categories": cats})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    posts_qs = Post.objects.published().filter(category=category)

    q = (request.GET.get("q") or "").strip()
    if q:
        posts_qs = posts_qs.filter(
            Q(title__icontains=q) | Q(content__icontains=q)
        )

    paginator = Paginator(posts_qs, 6)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    return render(
        request,
        "blog/category_detail.html",
        {"category": category, "posts": posts},
    )


@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Post updated.")
        return redirect(post.get_absolute_url())
    return render(request, "blog/post_form.html", {"form": form, "edit": True})


@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect("blog:home")
    return render(request, "blog/post_confirm_delete.html", {"post": post})


@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "Post created!")
        return redirect(post.get_absolute_url())
    return render(request, "blog/post_form.html", {"form": form})


def register(request):
    form = RegistrationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Account created! Check your email for future password resets.",
        )
        return redirect("blog:login")
    return render(request, "blog/register.html", {"form": form})


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    form = ProfileForm(request.POST or None,
                       request.FILES or None,
                       instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("blog:home")
    return render(request, "blog/profile_form.html", {"form": form})


def profile_detail(request, username):
    user = get_object_or_404(
        User.objects.select_related("profile"),
        username=username,
    )
    posts_qs = Post.objects.published().filter(author=user)
    paginator = Paginator(posts_qs, 6)
    page = request.GET.get("page")
    posts = paginator.get_page(page)
    return render(
        request,
        "blog/profile_detail.html",
        {"profile_user": user, "posts": posts},
    )


# views.py
@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(
        Comment.objects.select_related("post", "author"),
        pk=pk,
    )
    post = comment.post
    if request.method == "POST" and (
        request.user == comment.author
        or request.user == post.author
        or request.user.is_staff
    ):
        comment.delete()
        messages.success(request, "Comment deleted.")
    else:
        messages.error(
            request,
            "You don't have permission to delete this comment.",
        )
    return redirect(post.get_absolute_url())
