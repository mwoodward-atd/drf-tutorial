from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, CoreAPIClient

from snippets.models import Snippet
from snippets.serializers import SnippetSerializer


def create_default_snippet(title='Test Snippet',
                           code='print("Hello, World!")\n',
                           linenos=True,
                           language='python',
                           style='friendly'):
    return Snippet.objects.create(
        title=title,
        code=code,
        linenos=linenos,
        language=language,
        style=style
    )


class SnippetSerializerTests(TestCase):
    """Test snippet serializer"""

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


class SnippetViewsTests(TestCase):
    """Test the basic function-based views"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_snippets_list(self):
        snippet1 = create_default_snippet(title='new snippet')
        snippet2 = create_default_snippet(title='another snippet')

        res = self.client.get(reverse('snippets:list'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_snippet_success(self):
        payload = {
            'title': 'new snippet',
            'code': 'print("OHAI!")'
        }
        res = self.client.post(reverse('snippets:list'), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        snippet = Snippet.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(snippet, key))

    def test_create_snippet_fail(self):
        payload = {
            'title': 'bad snippet'
        }
        res = self.client.post(reverse('snippets:list'), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_snippet_detail_success(self):
        snippet = create_default_snippet()

        res = self.client.get(reverse('snippets:detail', args=[snippet.id]))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], snippet.id)

    def test_retrieve_snippet_detail_fail(self):
        snippet = create_default_snippet()

        res = self.client.get(reverse('snippets:detail', args=[snippet.id + 1]))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_snippet(self):
        snippet = create_default_snippet()

        res = self.client.delete(reverse('snippets:detail', args=[snippet.id]))
        res2 = self.client.get(reverse('snippets:list'))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(res2.data), 0)
