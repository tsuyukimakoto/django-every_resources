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
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.utils.tzinfo import LocalTimezone

from django.conf import settings
from django.db import connection

class DBDebugMiddleware:
    """
    "DBDebug" middleware for debug out O/R Mapper's SQL:
    """

    def process_response(self, request, response):
        if settings.DEBUG :
            for query in connection.queries:
                print "cost: %s \n sql:%s" % (query['time'], query['sql'])
        return response

def get_app_list():
    app_list = sorted(
        set(
            [x['app_label'][len('everes_'):] for x in ContentType.objects.
                filter(app_label__startswith='everes_').
                exclude(Q(app_label='everes_core')
                        | Q(app_label__startswith='everes_functional')
    					| Q(app_label__startswith='everes_theme')
                        ).values('app_label')]))
    app_list.reverse()
    return app_list

def get_app(request, app):
    try:
        mod = __import__('everes_%s' % app, {}, {}, [])
    except NameError:
        raise Http404()
    app_dict = getattr(mod, 'APP_DICT')
    return app_dict, mod
    
def get_file_name(fullpath):
    while os.path.exists(fullpath):
        try:
            dot_index = fullpath.rindex('.')
        except ValueError: # filename has no dot
            fullpath += '_'
        else:
            fullpath = fullpath[:dot_index] + '_' + fullpath[dot_index:]
    return fullpath

def iso8601(dt):
    try:
        offset = LocalTimezone(dt).utcoffset(dt).seconds
        if offset == 0:
            return u'Z'
        hours = offset/3600
        minutes = offset%3600
        difference = u'+'
        if offset < 0:
            difference = u'-'
        return '%s%02d:%02d' % (difference, hours, minutes,)
    except:
        return u'Z'


