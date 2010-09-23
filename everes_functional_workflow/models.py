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
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import models as auth_models

from everes_core import models as cms_models

# Create your models here.
"""
・承認権限の定義を行う
・複数の承認者を順序を指定して定義できるようにする
  ( ('user1', 'user2'), ('user3',), ('user4')) みたいな定義にしたい
  上記の場合、user1とuser2は順不同。user1とuser2が承認したら、uesr3が承認できるようになり、
  全ての承認者が承認した時点で承認フローが完了したこととする
・ワークフローの定義をできるようにする。Adminで特定の権限を持ったユーザが定義できるようにしたい。
・差し戻した場合には、前承認がクリアされてワークフロースタート前の状態になる。
・ワークフローがスタートしている状態は、編集ができない。こととする。
・？ワークフロー完了後のデータ修正はどのように行うか？
・最終承認者が先に承認をするようなパターンには対応しない"""


class Workflow(models.Model):
    name = models.CharField(_('Name'), max_length=20)

class UnitOfApprove(models.Model):
    workflow = models.ForeignKey(Workflow)
    everyone = models.BooleanField(default=True)

class Approver(models.Model):
    user = models.ForeignKey(auth_models.User)


