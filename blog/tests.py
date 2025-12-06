from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Post


class PostVisibilityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user("author", password="pass1234")
        self.viewer = User.objects.create_user("viewer", password="pass1234")

        self.category = Category.objects.create(name="Tech", slug="tech")

        now = timezone.now()
        self.live_post = Post.objects.create(
            title="Live",
            content="Visible content",
            author=self.author,
            category=self.category,
            status=Post.Status.PUBLISHED,
            published_at=now - timedelta(days=1),
        )
        self.future_post = Post.objects.create(
            title="Future",
            content="Scheduled",
            author=self.author,
            category=self.category,
            status=Post.Status.PUBLISHED,
            published_at=now + timedelta(days=1),
        )
        self.draft_post = Post.objects.create(
            title="Draft",
            content="Hidden",
            author=self.author,
            category=self.category,
            status=Post.Status.DRAFT,
        )

    def test_published_queryset_hides_drafts_and_future_posts(self):
        qs = Post.objects.published()
        self.assertIn(self.live_post, qs)
        self.assertNotIn(self.future_post, qs)
        self.assertNotIn(self.draft_post, qs)

    def test_visible_to_handles_auth_and_anonymous(self):
        anon_qs = Post.objects.visible_to(AnonymousUser())
        self.assertIn(self.live_post, anon_qs)
        self.assertNotIn(self.draft_post, anon_qs)

        author_qs = Post.objects.visible_to(self.author)
        self.assertIn(self.draft_post, author_qs)

        viewer_qs = Post.objects.visible_to(self.viewer)
        self.assertNotIn(self.draft_post, viewer_qs)

    def test_post_detail_requires_permissions_for_drafts(self):
        url = reverse("blog:post_detail", args=[self.draft_post.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        self.client.force_login(self.author)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
