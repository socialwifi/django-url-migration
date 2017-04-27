import re

from django.contrib import admin
from django import forms

from . import models
from . import views


class UrlMappingAdmin(admin.ModelAdmin):
    list_display = ['source_url', 'target_url', 'expire_after', 'last_usage']
    search_fields = ['source_url', 'target_url']


class UrlRegexpMappingForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        expected = cleaned_data.get('test_target_url', '')
        try:
            result = views.generate_url(
                self.cleaned_data.get('source_mapping', ''),
                self.cleaned_data.get('target_mapping', ''),
                cleaned_data.get('test_source_url', '')
            )
        except re.error as e:
            self.add_error('source_mapping', 'One of regexps is invalid: %s' % str(e))
        else:
            if result != expected:
                self.add_error('test_source_url', 'Expected %s got %s' % (expected, result))
        return cleaned_data

    class Meta:
        model = models.UrlRegexpMapping
        fields = ['source_mapping', 'target_mapping', 'expire_after', 'mapping_duration',
                  'test_source_url', 'test_target_url']


class UrlRegexpMappingAdmin(admin.ModelAdmin):
    form = UrlRegexpMappingForm
    list_display = ['source_mapping', 'target_mapping', 'expire_after', 'mapping_duration', 'last_usage']
    search_fields = ['source_mapping', 'target_mapping']
    fieldsets = (
        (None, {
            'fields': ('source_mapping', 'target_mapping', 'expire_after', 'mapping_duration'),
        }),
        ('Test', {
            'fields': ('test_source_url', 'test_target_url'),
        }),
    )


admin.site.register(models.UrlMapping, UrlMappingAdmin)
admin.site.register(models.UrlRegexpMapping, UrlRegexpMappingAdmin)
