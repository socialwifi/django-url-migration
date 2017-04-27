from django.views import generic


class TestView(generic.TemplateView):
    template_name = 'test.html'

test_view = TestView.as_view()
