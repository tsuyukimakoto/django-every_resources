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
from django.contrib import admin
from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.forms.widgets import Select
from django.utils.safestring import mark_safe
from models import ContentsMeta, CmsUserProfile, LinkRole

class RowLevelAdmin(admin.ModelAdmin):
    
    def get_user_field_name(self):
        raise NotImplementedError
    
    def has_add_permission(self, request, obj=None):
        self._author = request.user
        if not obj:
            return True
        return (request.user.is_superuser
                or ('%s' % (request.user.id,) == request.POST.get(self.get_user_field_name(), None)))
    
    def has_change_permission(self, request, obj=None):
        self._author = request.user
        if not obj:
            return True
        return (request.user.is_superuser
                or ((request.POST.get(self.get_user_field_name(), None) == None
                    or '%s' % (request.user.id,) == request.POST.get(self.get_user_field_name(), None))
                    and request.user == getattr(obj, self.get_user_field_name())
                    and super(RowLevelAdmin, self).has_change_permission(request, obj)))
    
    def has_delete_permission(self, request, obj=None):
        self._author = request.user
        if not obj:
            return True
        return (request.user.is_superuser
                or ((request.POST.get(self.get_user_field_name(), None) == None
                    or '%s' % (request.user.id,) == request.POST.get(self.get_user_field_name(), None))
                    and request.user == getattr(obj, self.get_user_field_name())
                    and super(RowLevelAdmin, self).has_delete_permission(request, obj)))
    
    def queryset(self, request):
        default_queryset = super(RowLevelAdmin, self).queryset(request)
        if not request.user.is_superuser:
            kwarg = {self.get_user_field_name():request.user}
            return default_queryset.filter(**kwarg)
        return default_queryset
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(RowLevelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if not self._author.is_superuser:
            if db_field.name == self.get_user_field_name():
                field.widget = Select(choices=(('%d' % self._author.id, unicode(self._author)),))
        return field

GMAP_WIDTH = 500
GMAP_HEIGHT = 300

class LocationWidget(forms.widgets.Widget):
    def __init__(self, *args, **kwargs):
        self.map_width = kwargs.get("map_width", GMAP_WIDTH)
        self.map_height = kwargs.get("map_height", GMAP_HEIGHT)
        
        super(LocationWidget, self).__init__(*args, **kwargs)
        self.inner_widget = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):
        a, b = (0,0)
        if isinstance(value, unicode) and ',' in value:
            a, b = value.split(',')
        elif isinstance(value, type([])):
            a, b = value
        lat, lng = float(a), float(b)
        
        js = '''
        <script type="text/javascript" charset="utf-8" src="http://www.google.com/jsapi?key=%(google_api_key)s&hl=ja"></script>
        <script type="text/javascript">
        google.load("maps", "2");
        google.setOnLoadCallback(load_%(name)s);
        
        var map_%(name)s;
        
        function setDefault_%(name)s() {
            var point = new GLatLng(0,0);
            savePosition_%(name)s(point);
        }
        function saveDefaultPosition_%(name)s() {
            var latitude = document.getElementById("id_%(inner_widget_name)s");
            document.cookie = "map_%(name)s_point=" + escape(latitude.value) + "; ";
        }
        
        function loadDefaultPosition_%(name)s() {
            var cookies = document.cookie;
            var l = "0,0";
            var idx = cookies.indexOf('map_%(name)s_point=');
            if(idx >= 0) {
                var endidx = cookies.indexOf('; ', idx);
                l = unescape(cookies.substring(idx + 'map_%(name)s_point='.length, endidx));
            }
            var lat = l.split(',')[0];
            var lng = l.split(',')[1];
            var point = new GLatLng(parseFloat(lat), parseFloat(lng));
            savePosition_%(name)s(point);
        }
        
        function savePosition_%(name)s(point) {
            var latitude = document.getElementById("id_%(inner_widget_name)s");
            latitude.value = point.lat().toFixed(6) + "," + point.lng().toFixed(6);
            map_%(name)s.panTo(point);
        }
        function load_%(name)s() {
            if (GBrowserIsCompatible()) {
                map_%(name)s = new GMap2(document.getElementById("map_%(name)s"));
                map_%(name)s.addControl(new GSmallMapControl());
                map_%(name)s.addControl(new GMapTypeControl());
    
                var point = new GLatLng(%(lat)f, %(lng)f);
                map_%(name)s.setCenter(point, 8);
                mrk = new GMarker(point, {draggable: true});
    
                GEvent.addListener(mrk, "dragend",
                    function() {
                        point = mrk.getPoint();
                        savePosition_%(name)s(point);
                });
    
                map_%(name)s.addOverlay(mrk);
    
                GEvent.addListener(map_%(name)s, "click",
                    function (overlay, point) {
                        savePosition_%(name)s(point);
                    
                        map_%(name)s.clearOverlays();
                        mrk = new GMarker(point, {draggable: true});
        
                        GEvent.addListener(mrk, "dragend", function() {
                            point = mrk.getPoint();
                            savePosition_%(name)s(point);
                    });
                    map_%(name)s.addOverlay(mrk);
                });
            }
        }
        </script>
        ''' % dict(name=name.replace('-', '_'), inner_widget_name=name, lat=lat, lng=lng, google_api_key=settings.GOOGLE_API_KEY)
        html = self.inner_widget.render("%s" % name, "%f,%f" % (lat,lng), dict(id='id_%s' % name))
        html += """<div id="map_%s" class="gmap" style="width: %dpx; height: %dpx"></div>""" % (name.replace('-', '_'), self.map_width, self.map_height)
        html += """<input type="button" onclick="setDefault_%s();" value="clear"/>""" % (name.replace('-', '_'),)
        html += """<input type="button" onclick="saveDefaultPosition_%s();" value="save"/>""" % (name.replace('-', '_'),)
        html += """<input type="button" onclick="loadDefaultPosition_%s();" value="load"/>""" % (name.replace('-', '_'),)
        return mark_safe(js+html)

class LocationField(forms.Field):
    widget = LocationWidget

    def clean(self, value):
        if isinstance(value, unicode) and ',' in value:
            a, b = value.split(',')
        else:
            a, b = value
            
        lat, lng = float(a), float(b)
        return "%f,%f" % (lat, lng)

class LocationForm(forms.ModelForm):
    location = LocationField()
    class Meta:
        model = ContentsMeta

class TagAdmin(RowLevelAdmin):
    def get_user_field_name(self):
        return 'author'

class CmsUserProfileAdmin(RowLevelAdmin):
    list_display = ('user', 'nickname',)
    def get_user_field_name(self):
        return 'user'

class EveresAdmin(RowLevelAdmin):
    list_display = ('title', 'published_from','author',)
    list_filter = ('published', 'author',)
    date_hierarchy = 'published_from'
    form = LocationForm
    search_fields = ('title', 'summary',)
    fieldsets = (
        ('Basic Meta Info', {
            'fields': (('published_from', 'published'), ('title', 'author'), 'summary', 'tags', 'location',)
        }),
        ('Special Attributes', {
            'classes': ['collapse',],
            'fields': ('related_item', 'affiliates', 'input_mode', )
        })
    )
    
    def get_user_field_name(self):
        return 'author'


class CmsUserLocationForm(forms.ModelForm):
    location = LocationField()
    class Meta:
        model = CmsUserProfile

class CmsLinkRoleAdmin(RowLevelAdmin):
    def get_user_field_name(self):
        return 'profile__user'

    class Meta:
        model = LinkRole

class CmsUserProfileInlineAdmin(admin.StackedInline):
    form = CmsUserLocationForm
    model = CmsUserProfile
    max_num = 1
    min_num = 1

class CmsUserAdmin(UserAdmin):
    inlines = [CmsUserProfileInlineAdmin]

from models import Tag, Affiliate, Comment, Trackback, CmsUserProfile
admin.site.register(Tag, TagAdmin)
admin.site.register(Affiliate, admin.ModelAdmin)
admin.site.register(Comment, admin.ModelAdmin)
admin.site.register(Trackback, admin.ModelAdmin)
admin.site.register(CmsUserProfile, CmsUserProfileAdmin)
admin.site.unregister(User)
admin.site.register(User, CmsUserAdmin)
admin.site.register(LinkRole, CmsLinkRoleAdmin)

