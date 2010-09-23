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

from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_day, archive_month, archive_year
from django.http import Http404
from everes_core.models import ContentsMeta, Comment, Trackback, CmsUserProfile
from everes_core import APP_DICT
from views import google_sitemaps, generate_uuid, detail, list_by_app, detail_by_slug, add_comment, add_trackback, list_by_tag, list_by_app_and_tag

def noop(*list):
    raise Http404()

CORE_DICT = APP_DICT.copy()
CORE_DICT.update({'template_name': 'everes_core/contentsmeta_list.html'})

urlpatterns = patterns('',
    url(r'about/$', object_list, dict(queryset=CmsUserProfile.objects.all().select_related(depth=1).order_by('id'), paginate_by=100, allow_empty=True, template_name='everes_core/about.html'), name='everes_about'),
    url(r'^api/google_sitemaps/$', google_sitemaps, name='google_sitemaps'),
    url(r'^api/generate_uuid/$', generate_uuid, name='api_generate_uuid'),
    url(r'^reactions/comments/$', object_list, dict(queryset=Comment.objects.all().select_related(depth=1).order_by('-create_date'), paginate_by=settings.PAGENT_BY, allow_empty=True), name='everes_comment_list'),
    url(r'^reactions/trackbacks/$', object_list, dict(queryset=Trackback.objects.all().select_related(depth=1).order_by('-create_date'), paginate_by=settings.PAGENT_BY, allow_empty=True), name='everes_trackback_list'),
    url(r'archive/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', archive_day, CORE_DICT, name='everes_day_list'),
    url(r'archive/(?P<year>\d{4})/(?P<month>\d{1,2})/$', archive_month, CORE_DICT, name='everes_month_list'),
    url(r'^(?P<app>\w+)/tag/(?P<tag>.*)/$', list_by_app_and_tag, name='everes_list_by_app_and_tag'),
    url(r'^tag/(?P<tag>.*)/$', list_by_tag, name='everes_list_by_tag'),
    url(r'^(?P<app>\w+)/$', list_by_app, name='everes_list_by_app'),
    url(r'^(?P<app>\w+)/(?P<slug>\w+)/$', detail_by_slug, name='everes_detail_by_slug'),
    url(r'^(?P<app>\w+)/(?P<object_id>\d+)/add/comment/(?P<unique_id>.*)/$', add_comment, name='everes_add_comment'),
    url(r'^(?P<app>\w+)/(?P<object_id>\d+)/add/comment/$', noop, name='everes_add_comment_base'),
    url(r'^(?P<app>\w+)/(?P<object_id>\d+)/add/trackback/(?P<unique_id>.*)/$', add_trackback, name='everes_add_trackback'),
    url(r'^(?P<app>\w+)/(?P<object_id>\d+)/add/trackback/$', noop, name='everes_add_trackback_base'),
    url(r'^(?P<app>\w+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug_or_id>.*)/$', detail, name='everes_detail'),
    url(r'', object_list, dict(queryset=ContentsMeta.public_objects.all(), paginate_by=settings.PAGENT_BY, allow_empty=True)),
)
