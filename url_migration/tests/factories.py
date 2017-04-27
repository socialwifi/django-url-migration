from datetime import timedelta

import factory

from django.utils import timezone

from .. import models


class UrlMappingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.UrlMapping

    expire_after = timedelta(days=10)


class UrlRegexpMappingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.UrlRegexpMapping

    expire_after = timedelta(days=10)
    mapping_duration = timedelta(days=7)


class RegexpGeneratedMappingFactory(UrlMappingFactory):
    class Meta:
        model = models.RegexpGeneratedMapping

    regexp = factory.SubFactory(UrlRegexpMappingFactory)


class LastUsageLogFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.LastUsageLog

    used_date = timezone.now()
    referer = 'http://www.google.pl'
    user_agent = 'Firefox'
    ip = '10.0.0.2'
