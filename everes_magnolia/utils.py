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
import pymagnolia
from django.conf import settings
from datetime import datetime, timedelta
import time
import string

from everes_core.models import Tag
from models import MagnoliaUser, Bookmark

_YMDHIS_LENGTH = 19

def _get_time_from_iso8601(str):
    if len(str) < _YMDHIS_LENGTH:
        return None
    d = datetime(*(time.strptime(str[:_YMDHIS_LENGTH], '%Y-%m-%dT%H:%M:%S')[:6]))
    if len(str) == _YMDHIS_LENGTH + 6:
        h_dlt = timedelta(hours=int(str[-6] + str[-5:-3]))
        m_dlt = timedelta(minutes=int(str[-6] + str[-2:]))
        d = d - h_dlt - m_dlt
    return d
        

def update_feeds():
    n = datetime.now()
    delta = timedelta(1)
    date_from = n - delta
    
    for mu in MagnoliaUser.objects.all():
        api = pymagnolia.MagnoliaApi(mu.api_key)
        
        bms = api.bookmarks_find(person=mu.username, rating=mu.limit_rank,
                     date_from='%04d/%02d/%02d' % (date_from.year, date_from.month, date_from.day))
        exist_tags = {}
        for bm in bms:
            create_datetime = _get_time_from_iso8601(bm.created)
            update_datetime = _get_time_from_iso8601(bm.updated)
            db_bm, created = Bookmark.objects.get_or_create(url=bm.url,
                              defaults={'title': bm.title,
                                        'summary': bm.description,
                                        'screenshot': bm.screenshot,
                                        'rating': bm.rating,
                                        'create_date': create_datetime,
                                        'update_date': update_datetime,
                                        'published_from': create_datetime,
                                        'author': mu.user})
            db_bm.tags.all().delete()
            for tag in bm.tags:
                if len(tag.strip()) > 0:
                    t, created = Tag.objects.get_or_create(name__iexact=tag.strip(), defaults={'name': tag.strip(),'author': mu.user, 'view_at_front': False})
                    db_bm.tags.add(t)
            db_bm.save()
