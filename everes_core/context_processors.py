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
from django.contrib.sites.models import Site
from django.core.cache import cache

from models import Tag, ContentsMeta
from utils import get_app_list
import re

p = re.compile('iPhone|iPod', re.IGNORECASE)

def site(request):
    """
    """
    return {'current_site': Site.objects.get_current()}

def everes_root_template(request):
    if p.search(request.META['HTTP_USER_AGENT']):
        return {'root_template': 'iphone_index.html'}
    return {'root_template': 'desktop_index.html'}

def everes_apps(request):
    """
    """
    app_list = cache.get('everes_apps')
    if not app_list:
        app_list = get_app_list()
        cache.set('everes_apps', app_list)
    return {'everes_apps': app_list}

def everes_tags(request):
    """
    """
    tag_list = cache.get('everes_tags')
    if not tag_list:
        tag_list = Tag.objects.filter(view_at_front=True).order_by('name')
        cache.set('everes_tags', tag_list)
    return {'everes_tags': tag_list}

def everes_days(request):
    day_list = cache.get('everes_days')
    if not day_list:
        day_list = ContentsMeta.public_objects.dates('published_from', 'month')
        cache.set('everes_days', day_list)
    return {'everes_days': day_list}

def api_keys(request):
    """
    """
    return {'google_api_key': settings.GOOGLE_API_KEY,
            'google_analytics_key': settings.GOOGLE_ANALYTICS,
            'google_search_key': settings.GOOGLE_SEARCH,
            'google_adsense_key': settings.GOOGLE_ADSENSE,
            'google_ad_slot_key': settings.GOOGLE_AD_SLOT}
