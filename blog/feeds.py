from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from .models import Post


class LatestPostsRSS(Feed):
    title = "Blurry Shady — Latest Posts"
    link = "/"
    description = "New posts from Blurry Shady"

    def items(self):
        return Post.objects.published()[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        # Simple preview; could striptags+truncate later.
        return item.content[:400]

    def item_link(self, item):
        return item.get_absolute_url()


class LatestPostsAtom(LatestPostsRSS):
    feed_type = Atom1Feed
    subtitle = LatestPostsRSS.description
