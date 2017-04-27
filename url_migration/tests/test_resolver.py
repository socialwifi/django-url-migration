from unittest import mock

from django import test

from .. import models
from .. import views
from . import factories


class TestUrlResolverIntegration(test.TestCase):
    def test_if_url_is_resolved(self):
        factories.UrlMappingFactory(source_url='/bar', target_url='/foo')
        response = self.client.get('/bar')
        self.assertEqual('/foo', response.url)
        self.assertEqual(301, response.status_code)

    def test_if_url_is_resolved_by_regexp(self):
        factories.UrlRegexpMappingFactory(
            source_mapping=r'/profil-v/(?P<pk>[0-9]+)/',
            target_mapping=r'/profil-miejsca/\1/'
        )
        response = self.client.get('/profil-v/10/')
        self.assertEqual('/profil-miejsca/10/', response.url)
        self.assertEqual(301, response.status_code)

    def test_if_404_is_returned(self):
        response = self.client.get('/abc/10/')
        self.assertEqual(404, response.status_code)

    @mock.patch('url_migration.views.logger')
    def test_if_404_is_returned_for_invalid_redirect(self, logger):
        factories.UrlMappingFactory(
            source_url='/a/',
            target_url='/a/',
        )
        response = self.client.get('/a/')
        self.assertTrue(logger.exception.called)
        self.assertEqual(404, response.status_code)


class TestRegexpMapping(test.TestCase):
    META = {
        'HTTP_REFERER': 'http://google.pl',
        'HTTP_USER_AGENT': 'Firefox 1',
        'HTTP_X_REAL_IP': '10.0.0.2',
    }

    def test_if_get_or_create_url_mapping_returns_existing_mapping(self):
        rule = factories.UrlRegexpMappingFactory(
            source_mapping=r'/a/b/(?P<pk>[0-9]+)/')
        mapping = factories.RegexpGeneratedMappingFactory(
            source_url='/a/b/1/', regexp=rule)
        other_rule = factories.UrlRegexpMappingFactory(
            source_mapping=r'/a/(.*)/')

        request = mock.Mock(path='/a/b/1/')
        resolver = views.UrlResolver(request)
        result = resolver._get_or_create_url_mapping(other_rule)
        self.assertEqual(mapping, result)
        self.assertEqual(1, models.RegexpGeneratedMapping.objects.count())

    def test_if_get_or_create_url_mapping_creates_new_mapping(self):
        rule = factories.UrlRegexpMappingFactory(
            source_mapping=r'/a/(?P<pk>[0-9]+)/',
            target_mapping=r'/b/\1/',
        )
        factories.RegexpGeneratedMappingFactory(
            source_url='/a/1234/', regexp=rule)

        request = mock.Mock(path='/a/1/')
        resolver = views.UrlResolver(request)
        result = resolver._get_or_create_url_mapping(rule)
        expected = models.RegexpGeneratedMapping.objects.get(
            source_url='/a/1/',
            target_url='/b/1/',
            regexp=rule
        )
        self.assertEqual(expected, result)
        self.assertEqual(2, models.RegexpGeneratedMapping.objects.count())

    def test_if_exception_is_raised_for_redirect_loop(self):
        factories.UrlMappingFactory(
            source_url='/a/',
            target_url='/a/',
        )
        request = test.RequestFactory().get('/a/')
        resolver = views.UrlResolver(request)
        with self.assertRaises(views.InvalidRedirect):
            list(resolver.map())
