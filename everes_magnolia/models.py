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

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from everes_core import models as cms_models

MAGNOLIA_RANK = ((0,0),(1,1),(2,2),(3,3),(4,4),(5,5),)

class MagnoliaUser(models.Model):
    user = models.ForeignKey(User, unique=True)
    username = models.CharField(max_length=12)
    api_key = models.CharField(max_length=100)
    limit_rank = models.SmallIntegerField(default=1, choices=MAGNOLIA_RANK)

class Bookmark(cms_models.ContentsMeta):
    url   = models.URLField(blank=True, verify_exists=False)
    screenshot = models.CharField(blank=True, max_length=500)
    rating = models.SmallIntegerField(blank=True, null=True)

    objects = models.Manager()
    public_objects = cms_models.PublicManager()
