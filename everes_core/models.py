# -*- coding: utf-8 -*-
#
# Copyright (c) 2008 Makoto Tsuyuki All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
#  3. Neither the name of the authors nor the names of its contributors
#     may be used to endorse or promote products derived from this
#     software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import os
from uuid import uuid4 as uuid #require python2.5 or above

from django.core.cache import cache
from django.conf import settings
from django.db import models
import django.dispatch
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template
from django.template.context import Context
from django.template import TemplateDoesNotExist

from django.contrib.auth import models as auth_models
from django.contrib.sites import models as sites_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from datetime import datetime, timedelta
from utils import get_file_name, iso8601, get_app

contentsmeta_modified = django.dispatch.Signal(providing_args=["app"])

class Tag(models.Model):
    author = models.ForeignKey(auth_models.User)
    name = models.CharField(max_length=30)
    view_at_front = models.BooleanField(default=True)
    class Meta:
        unique_together = ('author', 'name',)
        ordering = ('name',)
    
    def __unicode__(self):
        return '%s(%s)' % (self.name, self.author.username)

class Affiliate(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    js   = models.TextField(_('Affiliate JavaScript'))
    def __unicode__(self):
        return self.name

class PublicManager(models.Manager):
    def get_query_set(self):
        return super(PublicManager, self).get_query_set().filter(published=True).select_related(depth=1)

INPUT_MODE = (('reST', 'reST',), ('HTML', 'HTML',), )

class ContentsMeta(models.Model):
    title = models.CharField(_('Title'), max_length=255, db_index=True)
    summary = models.TextField(_('Summary'), blank=True)
    author = models.ForeignKey(auth_models.User, db_index=True)
    create_date = models.DateTimeField(_('Created at'), auto_now_add=True, editable=False)
    update_date = models.DateTimeField(_('Updated at'), auto_now=True, editable=False)
    published = models.BooleanField(_('Published'), default=True)
    published_from = models.DateTimeField(_('Open time'), default=datetime.now)
    location = models.CharField(_('Longitude and Latitude that taken'), max_length=40, blank=True)
    entity_app_label = models.CharField(_('Entity App Label'), max_length=100, blank=True, editable=False)
    entity_type = models.CharField(_('Entity Type'), max_length=20, blank=True, editable=False)
    
    input_mode = models.CharField(_('Input mode'), max_length=10, blank=False, default='reST', choices=INPUT_MODE)
    
    objects = models.Manager()
    public_objects = PublicManager()

    if settings.USE_WORKFLOW:
        authorized = models.BooleanField(_('Authorized'), default=True, editable=False)
    
    related_item = models.ManyToManyField('self', blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    comment_cache = models.IntegerField(_('Comment Cache'), blank=True, editable=False, default=0)
    trackback_cache = models.IntegerField(_('Comment Cache'), blank=True, editable=False, default=0)

    affiliates = models.ManyToManyField(Affiliate, blank=True)
    
    def save(self,force_insert=False, force_update=False):
        self.entity_app_label = self.__class__._meta.app_label
        self.entity_type = self.__class__._meta.object_name.lower()
        super(ContentsMeta, self).save(force_insert=force_insert, force_update=force_update)
        contentsmeta_modified.send(self, app=self.app_name)
    
    def delete(self):
        super(ContentsMeta, self).delete()
        contentsmeta_modified.send(self, app=self.app_name)
    
    class Meta:
        ordering = ('-published_from',)
    
    def __unicode__(self):
        return u'[%s:%s] %s' % (self.entity_app_label, self.entity_type, self.title)
    
    def render_as_list(self):
        try:
            tmpl = get_template(os.path.join(self.entity_app_label, '%s_as_list.html' % self.entity_type))
        except TemplateDoesNotExist:
            tmpl = get_template('everes_core/contentsmeta_as_list.html')
        obj = self._cast()
        return tmpl.render(Context({'obj': obj, 'MEDIA_URL': settings.MEDIA_URL, 'current_site': sites_models.Site.objects.get_current()}))

    def _get_app_name(self):
        return self.entity_app_label[len('everes_'):]

    def _get_absolute_url(self):
        return ('everes_detail', (), {
            'year': self.published_from.year, 'month': '%02d' % self.published_from.month, 'day': '%02d' % self.published_from.day,
            'slug_or_id': self.id, 'app': self.entity_app_label[len('everes_'):],
        })
    get_absolute_url = models.permalink(_get_absolute_url)

    def _get_absolute_url_by_slug(self):
        return ('everes_detail', (), {
            'year': self.published_from.year, 'month': '%02d' % self.published_from.month, 'day': '%02d' % self.published_from.day,
            'slug_or_id': self.slug, 'app': self.app_name,
        })
    
    def _has_location(self):
        if not self.location or self.location == '0,0' or self.location == '0.000000,0.000000':
            return False
        return True
    def _published_from_as_iso8601(self):
        return u'%04d-%02d-%02dT%02d:%02d:%02d%s' % (
            self.published_from.year,
            self.published_from.month,
            self.published_from.day,
            self.published_from.hour,
            self.published_from.minute,
            self.published_from.second,
            iso8601(self.published_from),)
    def _cast(self):
        return getattr(self, self.entity_type)
    
    app_name = property(_get_app_name)
    has_location = property(_has_location)
    published_from_as_iso8601 = property(_published_from_as_iso8601)
    cast = property(_cast)

class FileContentsMeta(ContentsMeta):
    def _upload_to(self, filename):
        basedir = os.path.join(settings.MEDIA_ROOT, self.__class__._meta.app_label[len('everes_'):])
        d = self.published_from
        if not d:
            d = datetime.now()
        basedir = os.path.join(basedir, d.strftime('%Y/%m/%d'))
        return get_file_name(os.path.join(basedir, filename))[len(settings.MEDIA_ROOT):]

    file = models.FileField(_('File'), upload_to=_upload_to)
    content_type = models.CharField(_('Content Type'), max_length=20, blank=True)
    

    class Meta:
        abstract = True

class ImageContentsMeta(ContentsMeta):
    file = models.ImageField(_('Image'), upload_to='images')
    
    class Meta:
        abstract = True

class Trackback(models.Model):
    contents = models.ForeignKey(ContentsMeta)
    blog_name = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=False, verify_exists=False)
    excerpt = models.TextField(blank=False)
    visible = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('create_date',)

    def save(self, force_insert=False, force_update=False):
        super(Trackback, self).save(force_insert=force_insert, force_update=force_update)
        c = self.contents
        c.trackback_cache += 1
        c.save()

    def delete(self):
        super(Trackback, self).delete()
        c = self.contents
        c.trackback_cache -= 1
        c.save()

class Comment(models.Model):
    contents = models.ForeignKey(ContentsMeta)
    commentator = models.CharField(_('Commentator'), max_length=20)
    url = models.URLField(_('URL'), verify_exists=False, blank=True)
    body = models.TextField(_('Body'))
    create_date = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ('create_date',)

    def save(self, force_insert=False, force_update=False):
        super(Comment, self).save(force_insert=force_insert, force_update=force_update)
        c = self.contents
        c.comment_cache += 1
        c.save()

    def delete(self):
        super(Comment, self).delete()
        c = self.contents
        c.comment_cache -= 1
        c.save()

class CmsUserProfile(models.Model):
    user = models.ForeignKey(auth_models.User, unique=True)
    nickname = models.CharField(_('Nickname'), max_length=20)
    outline  = models.TextField(_('Outline'), blank=True)
    location = models.CharField(_('Usual Longitude and Latitude'), max_length=40, blank=True)

    def __unicode__(self):
        return self.user.username

class LinkRole(models.Model):
    profile = models.ForeignKey(CmsUserProfile)
    name   = models.CharField(_('Link Role'), max_length=50)
    url     = models.URLField(_('Link'))
    
    def __unicode__(self):
        return u'[%s] %s' % (self.profile.user.username, self.name,)

class UniqueIdManager(models.Manager):
    def get_query_set(self):
        limit = datetime.now() + timedelta(seconds=settings.FEEDBACK_UUID_TIMEOUT * -60)
        return super(UniqueIdManager, self).get_query_set().filter(create_date__gte=limit, valid=True)

class UniqueId(models.Model):
    uniqueId = models.CharField(max_length=28, db_index=True)
    valid = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True, editable=False)
    update_date = models.DateTimeField(auto_now=True, editable=False)
    
    def save(self):
        self.uniqueId = str(uuid())
        super(UniqueId, self).save()
    
    def __unicode__(self):
        return 'UniqueId: %s , Created: %s' % (self.uniqueId, self.create_date,)
    
    objects = models.Manager()
    public_objects = UniqueIdManager()


#signal

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from utils import get_app_list

def clear_app_cache(sender, app):
    cache.delete('everes_days')
    cache.delete('everes_sitemap')
    cache.delete('everes_feed_core')
    cache.delete('everes_feed_%s' % app)
    for tag in Tag.objects.all():
        cache.delete('everes_feed_core_tag_%s' % (tag.name,))
        cache.delete('everes_feed_%s_tag_%s' % (app, tag.name))

def app_modified(sender, **kwargs):
    app      = kwargs['app']
    clear_app_cache(sender, app)

def clear_tag_cache(sender, **kwargs):
    cache.delete('everes_sitemap')
    cache.delete('everes_tags')
    for tag in Tag.objects.all():
        cache.delete('everes_feed_core_tag_%s' % (tag.name,),)
        for app in get_app_list():
            cache.delete('everes_feed_%s_tag_%s' % (app, tag.name),)

contentsmeta_modified.connect(app_modified)

post_save.connect(clear_tag_cache, sender=Tag)
post_delete.connect(clear_tag_cache, sender=Tag)
