from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from .demo_application.views import test_view

urlpatterns = [
    url(r'^$', test_view),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'url_migration.views.page_not_found'
