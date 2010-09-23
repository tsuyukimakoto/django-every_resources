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
import pydiigo
from django.conf import settings
from datetime import datetime, timedelta
import time
import string

from everes_core.models import Tag
from models import DiigoUser, DiigoBookmark

_YMDHIS_LENGTH = 19

def _get_time_from_diigo_datetime(str):
    """
    >>> test_str = '2009/03/04 02:57:09 +0000'
    >>> result_date = _get_time_from_diigo_datetime(test_str)
    >>> assert result_date.year == 2009
    >>> assert result_date.month == 3
    >>> assert result_date.day == 4
    >>> assert result_date.hour == 2
    >>> assert result_date.minute == 57
    >>> assert result_date.second == 9
    """
    if len(str) < _YMDHIS_LENGTH:
        return None
    d = datetime(*(time.strptime(str[:_YMDHIS_LENGTH], '%Y/%m/%d %H:%M:%S')[:6]))
    if len(str) == _YMDHIS_LENGTH + 6:
        h_dlt = timedelta(hours=int(str[-6] + str[-5:-3]))
        m_dlt = timedelta(minutes=int(str[-6] + str[-2:]))
        d = d - h_dlt - m_dlt
    return d
        

def update_feeds():
    n = datetime.now()
    delta = timedelta(1)
    date_from = n - delta
    
    for du in DiigoUser.objects.all():
        api = pydiigo.DiigoApi(user=du.username, password=du.password)
        
        bms = api.bookmarks_find(users=du.username)
        exist_tags = {}
        for bm in bms:
            create_datetime = _get_time_from_diigo_datetime(bm.created_at)
            update_datetime = _get_time_from_diigo_datetime(bm.updated_at)
            db_bm, created = DiigoBookmark.objects.get_or_create(url=bm.url,
                              defaults={'title': bm.title,
                                        'summary': bm.desc,
                                        'create_date': create_datetime,
                                        'update_date': update_datetime,
                                        'published_from': create_datetime,
                                        'author': du.user})
            db_bm.tags.all().delete()
            for tag in bm.tags.split(','):
                if len(tag.strip()) > 0:
                    t, created = Tag.objects.get_or_create(name__iexact=tag.strip(), defaults={'name': tag.strip(),'author': du.user, 'view_at_front': False})
                    db_bm.tags.add(t)
            db_bm.save()
