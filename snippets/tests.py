from django.test import TestCase

from snippets.models import Snippet
from snippets.serializers import SnippetSerializer


class SnippetSerializerTests(TestCase):
    """Test snippet serializer"""

    def create_default_snippet(self):
        return Snippet.objects.create(
            title='Test Snippet',
            code='print("Hello, World!")\n',
            linenos=True,
            language='python',
            style='friendly'
        )

    def test_create_snippet_success(self):
        data = {
            'title': 'New Snippet',
            'code': 'print("Hello, World!")\n',
            'linenos': True,
            'language': 'python',
            'style': 'friendly',
        }
        serializer = SnippetSerializer(data=data)
        snippet_valid = serializer.is_valid()

        if snippet_valid:
            serializer.save()

        self.assertTrue(snippet_valid)
        self.assertEqual(len(Snippet.objects.all()), 1)
        self.assertEqual(serializer.validated_data.get('title'), 'New Snippet')

    def test_create_snippet_fail(self):
        data = {
            'title': 'Bad Snippet',
            'language': 'ColdFusion',
        }
        serializer = SnippetSerializer(data=data)
        snippet_valid = serializer.is_valid()

        if snippet_valid:
            serializer.save()

        self.assertFalse(snippet_valid)
        self.assertEqual(len(Snippet.objects.all()), 0)
