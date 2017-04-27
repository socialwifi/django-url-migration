from django.core.management.base import BaseCommand
from django.utils import timezone

from url_migration import models


class Command(BaseCommand):
    def handle(self, **options):
        for rule in models.UrlRegexpMapping.objects.filter(last_usage__isnull=False):
            self._remove_if_unused(rule)
        for rule in models.UrlMapping.objects.filter(last_usage__isnull=False):
            self._remove_if_unused(rule)

    def _remove_if_unused(self, rule):
        if rule.last_usage.used_date + rule.expire_after < timezone.now():
            self.stdout.write('Removing expired rule %s' % str(rule))
            rule.delete()
