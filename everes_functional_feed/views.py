# Create your views here.

from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.views import feed as django_feed
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.utils.feedgenerator import Rss201rev2Feed
from everes_core.utils import get_app

FEED_SITE = Site.objects.get_current()
FEED_TITLE = FEED_SITE.name
FEED_BASE_URL = 'http://%s' % FEED_SITE.domain

class LatestContents(Feed):
    title_template = 'everes_functional_feed/feed_title.html'
    description_template = 'everes_functional_feed/feed_description.html'
    def items(self):
        raise NotImplementedError()
    def title(self):
        return FEED_TITLE
    def link(self):
        return FEED_BASE_URL
    def item_link(self, item):
        return item.cast.get_absolute_url()
    def item_author_name(self, item):
        return item.author.get_profile().nickname
    def item_author_link(self, item):
        return item.author.get_absolute_url()
    def item_pubdate(self, item):
        return item.published_from
    def item_categories(self, item):
        return item.tags.all()
    def item_copyright(self, item):
        return item.author.get_full_name()

def get_feed_model(request, app, tag=None):
    app_dict, mod = get_app(request, app)
    class FeedModel(LatestContents):
        def items(self):
            if tag:
                return app_dict['queryset'].filter(tags__name__iexact=tag)[:20]
            return app_dict['queryset'][:20]
    return FeedModel

def feed(request, app):
    if app == 'all':
        app = 'core'
    result = cache.get('everes_feed_%s' % (app,))
    if not result:
        feeds = {app: get_feed_model(request, app)}
        result = django_feed(request, url=app, feed_dict=feeds)
        cache.set('everes_feed_%s' % (app,), result)
    return result

def tag_feed(request, app, tag):
    if app == 'all':
        app = 'core'
    tag = tag.lower()
    result = cache.get('everes_feed_%s_tag_%s' % (app, tag,))
    if not result:
        feeds = {app: get_feed_model(request, app, tag)}
        result = django_feed(request, url=app, feed_dict=feeds)
        cache.set('everes_feed_%s_tag_%s' % (app, tag,), result)
    return result

