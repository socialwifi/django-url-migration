from datetime import timedelta

from django.conf import settings
from django.db import models


class LastUsageLog(models.Model):
    used_date = models.DateTimeField()
    referer = models.TextField()
    user_agent = models.TextField()
    ip = models.GenericIPAddressField()
    user = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.used_date)


class UrlMapping(models.Model):
    source_url = models.CharField(max_length=200, unique=True)
    target_url = models.CharField(max_length=200)
    expire_after = models.DurationField(
        help_text='Time of inactivity after which the mapping expires. Format: "DD HH:MM:SS"',
        default=timedelta(days=180)
    )
    last_usage = models.OneToOneField(
        LastUsageLog, null=True, editable=False, on_delete=models.SET_NULL)

    def lock(self):
        return UrlMapping.objects.select_for_update().get(pk=self.pk)

    def __str__(self):
        return '%s -> %s' % (self.source_url, self.target_url)


class UrlRegexpMapping(models.Model):
    source_mapping = models.CharField(max_length=200, unique=True)
    target_mapping = models.CharField(max_length=200)
    expire_after = models.DurationField(
        help_text='Time of inactivity after which the mapping expires. Format: "DD HH:MM:SS"',
        default=timedelta(days=180))
    mapping_duration = models.DurationField(
        help_text='Time of inactivity after which the created url mapping expires. Format: "DD HH:MM:SS"',
        default=timedelta(days=180)
    )
    last_usage = models.OneToOneField(
        LastUsageLog, null=True, editable=False, on_delete=models.SET_NULL)
    test_source_url = models.CharField(max_length=200)
    if settings.DEBUG:
        test_source_url.help_text = (
            '<b><span style="color: red;">'
            'You are in the debug mode - url mapping is disabled. '
            'You can test it here only.'
            '</span></b>'
        )
    test_target_url = models.CharField(
        max_length=200, help_text=('Provide example old/new urls you are attempting to map. Test urls will be used to test your regexp mappings.'
                                   '<br>For example <b>/a/(?P&lt;pk&gt;[0-9]+)/</b> mapping with <b>/b/\g&lt;pk&gt;/</b> target mapping'
                                   ' will change /a/1/ to /b/1/.'))

    def __str__(self):
        return '%s -> %s' % (self.source_mapping, self.target_mapping)

    def lock(self):
        return UrlRegexpMapping.objects.select_for_update().get(pk=self.pk)


class RegexpGeneratedMapping(UrlMapping):
    regexp = models.ForeignKey(UrlRegexpMapping, on_delete=models.SET_NULL, null=True)
