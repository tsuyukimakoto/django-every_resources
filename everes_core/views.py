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
from django.core import serializers
from django.core.cache import cache
from django.db import transaction
from django.db.models.loading import get_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader, RequestContext

from django.views.generic import date_based, list_detail

from models import UniqueId, ContentsMeta
from forms import CommentForm, TrackbackForm
from utils import get_app


@login_required
def preview(request, app_label, model_name):
    PreviewModel = get_model(app_label, model_name)
    data = PreviewModel(request.POST)
    return render_to_response('%s/%s_detail.html' % (app_label, model_name.lower(),),
                              dict(obj=data),
                              context_instance=RequestContext(request))

def detail(request, app, year, month, day, slug_or_id):
    app_dict, mod = get_app(request, app)
    if getattr(mod, 'USE_SLUG'):
        app_dict.update(slug=slug_or_id)
    else :
        app_dict.update(object_id=slug_or_id)
    app_dict.update(year=year)
    app_dict.update(month=month)
    app_dict.update(day=day)
    app_dict.update(extra_context=dict(form=CommentForm()))
    return date_based.object_detail(request, **app_dict)

def detail_by_slug(request, app, slug):
    app_dict, mod = get_app(request, app)
    if not getattr(mod, 'USE_SLUG'):
        raise Http404()
    queryset = app_dict['queryset']
    return list_detail.object_detail(request, queryset=queryset, slug=slug, extra_context=dict(form=CommentForm()))

def list_by_app(request, app):
    app_dict, mod = get_app(request, app)
    return list_detail.object_list(request,
            queryset=app_dict['queryset'],
            paginate_by=settings.PAGENT_BY,
            extra_context=dict(filtered_app=app))

def list_by_tag(request, tag):
    return list_detail.object_list(request,
            queryset=ContentsMeta.public_objects.filter(tags__name__iexact=tag),
            paginate_by=settings.PAGENT_BY,
            extra_context=dict(filtered_tag=tag))

def list_by_app_and_tag(request, app, tag):
    app_dict, mod = get_app(request, app)
    return list_detail.object_list(request,
            queryset=app_dict['queryset'].filter(tags__name__iexact=tag),
            paginate_by=settings.PAGENT_BY,
            extra_context=dict(filtered_app=app,filtered_tag=tag))

@transaction.commit_on_success
def add_comment(request, app, object_id, unique_id):
    if request.method == 'POST':
        try:
            mod = __import__('everes_%s' % app, {}, {}, [])
        except NameError:
            raise Http404()
        form = CommentForm(request.POST)
        if form.is_valid():
            app_dict = getattr(mod, 'APP_DICT')
            data = get_object_or_404(app_dict.get('queryset'), pk=object_id)
            uid = get_object_or_404(UniqueId.public_objects.all(), uniqueId=unique_id)
            uid.valid = False
            uid.save()
            comment = form.save(commit=False)
            comment.contents = data
            comment.save()
            return HttpResponseRedirect(data.get_absolute_url())
        #TODO なんとかしてdetailにformを渡して返す
        raise NotImplementedError
    else:
        raise Http404

@transaction.commit_on_success
def add_trackback(request, app, object_id, unique_id):
    if request.method == 'POST':
        try:
            mod = __import__('everes_%s' % app, {}, {}, [])
        except NameError:
            raise Http404()
        form = TrackbackForm(request.POST)
        if form.is_valid():
            app_dict = getattr(mod, 'APP_DICT')
            data = get_object_or_404(app_dict.get('queryset'), pk=object_id)
            uid = get_object_or_404(UniqueId.public_objects.all(), uniqueId=unique_id)
            uid.valid = False
            uid.save()
            trackback = form.save(commit=False)
            trackback.contents = data
            trackback.save()
            return HttpResponse('{"result": 1}')
        raise Http404
    else:
        raise Http404

def google_sitemaps(request) :
    response = HttpResponse(mimetype='text/xml')
    sitemap = cache.get('everes_sitemap')
    if not sitemap:
        t = loader.get_template('google_sitemaps.html')

        c = RequestContext(request, {
            'object_list': ContentsMeta.public_objects.order_by('-create_date'),
        })
        sitemap = t.render(c)
    response.write(sitemap)
    return response


def generate_uuid(request):
    uniqueId = UniqueId()
    uniqueId.save()
    json_data = serializers.serialize('json', (uniqueId,), fields = ('uniqueId',))
    return HttpResponse(json_data, mimetype='application/json')
