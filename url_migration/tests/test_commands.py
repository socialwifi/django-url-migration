from unittest import mock

from django.core import management
from django import test
from django.utils import timezone
import pytz

from .. import models
from . import factories


@mock.patch('django.utils.timezone.now', mock.Mock(return_value=timezone.datetime(2000, 12, 10, 22, 11, tzinfo=pytz.utc)))
class TestRemoveExpiredRedirects(test.TestCase):
    def test_if_url_mapping_is_removed(self):
        log = factories.LastUsageLogFactory(used_date=timezone.datetime(1999, 12, 10, 22, 11, tzinfo=pytz.utc))
        factories.UrlMappingFactory(last_usage=log, id=199)
        management.call_command('remove_expired_redirects')
        self.assertFalse(models.UrlMapping.objects.filter(pk=199).exists())

    def test_if_regexp_mapping_is_removed(self):
        log = factories.LastUsageLogFactory(used_date=timezone.datetime(1999, 12, 10, 22, 11, tzinfo=pytz.utc))
        factories.UrlRegexpMappingFactory(last_usage=log, id=233)
        management.call_command('remove_expired_redirects')
        self.assertFalse(models.UrlRegexpMapping.objects.filter(pk=233).exists())

    def test_if_used_mapping_is_not_removed(self):
        log = factories.LastUsageLogFactory(used_date=timezone.datetime(2001, 12, 10, 22, 11, tzinfo=pytz.utc))
        factories.UrlMappingFactory(last_usage=log, id=344)
        management.call_command('remove_expired_redirects')
        self.assertTrue(models.UrlMapping.objects.filter(pk=344).exists())

    def test_if_used_regexp_mapping_is_not_removed(self):
        log = factories.LastUsageLogFactory(used_date=timezone.datetime(2001, 12, 10, 22, 11, tzinfo=pytz.utc))
        factories.UrlRegexpMappingFactory(last_usage=log, id=422)
        management.call_command('remove_expired_redirects')
        self.assertTrue(models.UrlRegexpMapping.objects.filter(pk=422).exists())

    def test_if_unused_mapping_is_not_removed(self):
        factories.UrlMappingFactory(id=566)
        management.call_command('remove_expired_redirects')
        self.assertTrue(models.UrlMapping.objects.filter(pk=566).exists())

    def test_if_unused_regexp_mapping_is_not_removed(self):
        factories.UrlRegexpMappingFactory(id=229)
        management.call_command('remove_expired_redirects')
        self.assertTrue(models.UrlRegexpMapping.objects.filter(pk=229).exists())

    def test_if_removing_regexp_mapping_does_not_remove_generated_mappings(self):
        log = factories.LastUsageLogFactory(used_date=timezone.datetime(1999, 12, 10, 22, 11, tzinfo=pytz.utc))
        mapping = factories.UrlRegexpMappingFactory(last_usage=log, id=988)
        factories.RegexpGeneratedMappingFactory(regexp=mapping, id=1022)
        management.call_command('remove_expired_redirects')
        self.assertTrue(models.RegexpGeneratedMapping.objects.filter(pk=1022).exists())
