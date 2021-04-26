import logging
import re

from django.db import transaction
from django import http
from django.utils import timezone
from django.views import defaults

from . import models


logger = logging.getLogger(__name__)


def page_not_found(request, exception, template_name='404.html'):
    return next(get_response(request, template_name, UrlResolver))


def get_response(request, template_name, resolver_class):
    try:
        resolver = resolver_class(request)
        yield from resolver.map()
    except InvalidRedirect as e:
        logger.exception(e)
    yield defaults.page_not_found(request, template_name)


class UrlResolver:
    def __init__(self, request):
        self.request = request
        self.path = request.path
        self.meta = request.META

    def map(self):
        yield from self._map_by_path()
        yield from self._map_by_regexp()

    def _map_by_path(self):
        try:
            mapping = self._get_matching_url_mapping()
            yield self._log_and_get_response(mapping)
        except models.UrlMapping.DoesNotExist:
            return

    def _get_matching_url_mapping(self):
        return models.UrlMapping.objects.get(source_url=self.path)

    def _map_by_regexp(self):
        for mapping in self._get_matching_regexp_mappings():
            url_mapping = self._get_or_create_url_mapping(mapping)
            self._update_usage(url_mapping.regexp)
            yield self._log_and_get_response(url_mapping)

    def _log_and_get_response(self, rule):
        path = self.request.get_full_path()
        redirect_to = path.replace(rule.source_url, rule.target_url)
        if path == redirect_to:
            raise InvalidRedirect('Redirect loop detected for {}'.format(path))
        else:
            self._update_usage(rule)
            return self._redirect_response(redirect_to)

    def _get_matching_regexp_mappings(self):
        for mapping in models.UrlRegexpMapping.objects.all():
            if re.match(mapping.source_mapping, self.path):
                yield mapping

    def _get_or_create_url_mapping(self, regexp_rule):
        target_url = generate_url(regexp_rule.source_mapping, regexp_rule.target_mapping, self.path)
        rule, _ = models.RegexpGeneratedMapping.objects.get_or_create(
            source_url=self.path, defaults={
                'regexp': regexp_rule,
                'target_url': target_url,
                'expire_after': regexp_rule.mapping_duration,
            })
        return rule

    @staticmethod
    def _redirect_response(redirect_to):
        return http.HttpResponsePermanentRedirect(redirect_to=redirect_to)

    @transaction.atomic
    def _update_usage(self, rule):
        rule = rule.lock()
        data = self._get_usage_data_dict()
        if rule.last_usage:
            rule.last_usage.delete()
        rule.last_usage = self._log_usage(data)
        rule.save()

    @staticmethod
    def _log_usage(data):
        return models.LastUsageLog.objects.create(**data)

    def _get_usage_data_dict(self):
        return {
            'used_date': timezone.now(),
            'referer': self.meta.get('HTTP_REFERER', ''),
            'user_agent': self.meta.get('HTTP_USER_AGENT', ''),
            'ip': self.meta.get('HTTP_X_REAL_IP', '0.0.0.0'),
            'user': self._get_user(),
        }

    def _get_user(self):
        if self.request.user.is_authenticated:
            return self.request.user
        else:
            return None


def generate_url(source_mapping, target_mapping, path):
    return re.sub(source_mapping, target_mapping, path)


class InvalidRedirect(Exception):
    pass
