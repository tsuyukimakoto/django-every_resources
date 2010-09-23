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
from django.db import models
from django.utils.translation import ugettext_lazy as _

from everes_core import models as cms_models
from everes_photo.extlib import EXIF
from everes_photo.utils import calc_thumb_size, crop_rect

import os
import re
from datetime import datetime
from PIL import Image

EXIF_FOR_RECORD = ('Image Make', 'Image Model', 'EXIF DateTimeOriginal',
    'EXIF FocalLengthIn35mmFilm', 'EXIF FNumber', 'EXIF ISOSpeedRatings',
    'EXIF ExposureTime', 'EXIF ExposureBiasValue', 'EXIF MeteringMode',
    'Image ImageDescription', 'EXIF ExifImageWidth', 'EXIF ExifImageLength',
    'EXIF Flash', 'EXIF Contrast', 'EXIF ExposureProgram',
    'EXIF SubjectDistance', 'EXIF FocalLength', 'EXIF BrightnessValue',
    'EXIF UserComment', 'GPSLatitude', 'GPSLongitude', 'GPSAltitude', )

exif_datetime_re = re.compile(r'([0-9][0-9][0-9][0-9]):([0-9][0-9]):([0-9][0-9]) ([0-9][0-9]):([0-9][0-9]):([0-9][0-9])')

def datetime_from_exif(data):
    """
    >>> success_data = '2008:11:30 23:59:13'
    >>> d1 = datetime_from_exif(success_data)
    >>> assert 2008 == d.year
    >>> assert 11 == d.month
    >>> assert 30 == d.day
    >>> assert 23 == d.hour
    >>> assert 59 == d.minute
    >>> assert 13 == d.second
    >>> assert datetime_from_exif(None) is None
    >>> assert datetime_from_exif('') is None
    """
    m = exif_datetime_re.search(data)
    try:
        if m:
            return datetime(*[int(x) for x in m.groups()])
    except: pass
    return None

class Shot(cms_models.ImageContentsMeta):
    raw_exif = models.TextField(_('EXIF'), blank=True)
    
    exif_maker                = models.CharField(_('Maker'), max_length=50, blank=True, editable=False)
    exif_model                = models.CharField(_('Model'), max_length=50, blank=True, editable=False)
    exif_datetime             = models.DateTimeField(_('Date Time Original'), blank=True, null=True, editable=False)
    exif_focal_length_in_35mm = models.CharField(_('Focal Length in 35mm Film'), max_length=10, blank=True, editable=False)
    exif_f_number             = models.CharField(_('F Number'), max_length=10, blank=True, editable=False)
    exif_iso                  = models.CharField(_('ISO Speed Ratings'), max_length=10, blank=True, editable=False)
    exif_exposure_time        = models.CharField(_('Exposure Time'), max_length=10, blank=True, editable=False)
    exif_exposure_bias_value  = models.CharField(_('Exposure Bias Value'), max_length=10, blank=True, editable=False)
    exif_metering_mode        = models.CharField(_('Metering Mode'), max_length=20, blank=True, editable=False)
    exif_gps_latitude         = models.CharField(_('GPS Latitude'), max_length=20, blank=True, editable=False)
    exif_gps_longitude        = models.CharField(_('GPS Longitude'), max_length=20, blank=True, editable=False)
    exif_gps_altitude         = models.CharField(_('GPS Altitude'), max_length=20, blank=True, editable=False)

    objects = models.Manager()
    public_objects = cms_models.PublicManager()

    def save(self):
        if not self.id:
            f = open(self.file.path)
            tags = EXIF.process_file(f)
            self.exif_maker = str(tags.get('Image Make', '')).strip()
            self.exif_model = str(tags.get('Image Model', '')).strip()
            self.exif_datetime = datetime_from_exif(str(tags.get('EXIF DateTimeOriginal', '')).strip())
            self.exif_focal_length_in_35mm = str(tags.get('EXIF FocalLengthIn35mmFilm', '')).strip()
            self.exif_f_number = str(tags.get('EXIF FNumber', '')).strip()
            self.exif_iso = str(tags.get('EXIF ISOSpeedRatings', '')).strip()
            self.exif_exposure_time = str(tags.get('EXIF ExposureTime', '')).strip()
            self.exif_exposure_bias_value = str(tags.get('EXIF ExposureBiasValue', '')).strip()
            self.exif_metering_mode = str(tags.get('EXIF MeteringMode', '')).strip()
            self.exif_gps_latitude = str(tags.get('GPSLatitude', '')).strip()
            self.exif_gps_longitude = str(tags.get('GPSLongitude', '')).strip()
            self.exif_gps_altitude = str(tags.get('GPSAltitude', '')).strip()
            raw = []
            for exif in EXIF_FOR_RECORD:
                raw.append('%s: %s' % (exif, str(tags.get(exif, '')).strip(),))
            self.raw_exif = '\n'.join(raw)
        super(Shot, self).save()


from django.db.models.signals import pre_save, post_save

def save_file(signal, sender, instance, **kwds):
    img = Image.open(instance.file.path)
    base_dir = os.path.dirname(instance.file.path)
    for additional in settings.ADDITIONAL_IMAGES:
        im = img.copy()
        width = additional[1][0]
        height = additional[1][1]
        diff = width - height
        if diff > 0:
            large = width
            dim = (0, 0+diff/2-height/2, width-1, 0+diff/2+height/2)
        elif diff < 0:
            large = height
            dim = (0+(diff*-1)/2-width/2, 0, 0(diff*-1)/2+width/2, height-1)
        else:
            large = width
            dim = (0,0,width-1,height-1)
        im = im.resize(calc_thumb_size(im.size[0], im.size[1], large), Image.ANTIALIAS)
        im = im.crop(dim)
        dr = os.path.join(base_dir, additional[0])
        if not os.path.exists(dr):
            os.mkdir(dr)
        if instance.id :
            im.save(os.path.join(dr, '%d.jpg' % (instance.id,)))

post_save.connect(save_file, sender = Shot)
