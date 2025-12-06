from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class PostQuerySet(models.QuerySet):
    """Reusable filters for post visibility."""

    def published(self):
        """Return posts that are live to the public."""
        now = timezone.now()
        return self.select_related("author", "category").filter(
            status=self.model.Status.PUBLISHED,
            published_at__isnull=False,
            published_at__lte=now,
        )

    def visible_to(self, user):
        """Limit queryset based on viewer permissions."""
        qs = self.select_related("author", "category")

        if not user.is_authenticated:
            return qs.published()

        if user.is_staff:
            return qs

        now = timezone.now()
        return qs.filter(
            Q(status=self.model.Status.PUBLISHED, published_at__lte=now)
            | Q(author=user)
        )


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStamped):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category_detail", args=[self.slug])


class Profile(TimeStamped):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    location = models.CharField(max_length=80, blank=True)

    def __str__(self) -> str:
        return self.user.username


class Post(TimeStamped):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    content = models.TextField()
    featured_image = models.ImageField(
        upload_to="posts/",
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="posts",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    published_at = models.DateTimeField(blank=True, null=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["status", "published_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["title"],
                name="unique_title_case_insensitive",
                condition=Q(status="published"),
            )
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.slug])

    @property
    def is_public(self) -> bool:
        return (
            self.status == self.Status.PUBLISHED
            and self.published_at is not None
            and self.published_at <= timezone.now()
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:160]
            slug = base
            i = 2
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug

        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)


class Comment(TimeStamped):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self.post}"

