from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Category, Post


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.published()

    def lastmod(self, obj):
        return getattr(obj, "updated_at", obj.created_at)

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.3

    def items(self):
        return ["blog:home", "blog:category_list"]

    def location(self, name):
        return reverse(name)
