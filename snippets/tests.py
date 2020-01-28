from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, CoreAPIClient

from snippets.models import Snippet
from snippets.serializers import SnippetSerializer


SNIPPETS_LIST_URL = reverse('snippet-list')
USERS_LIST_URL = reverse('user-list')


def create_sample_user(username='test', password='test1234'):
    return User.objects.create_user(
        username=username,
        password=password
    )


def snippet_detail_url(id):
    return reverse('snippet-detail', args=[id])


def user_detail_url(id):
    return reverse('user-detail', args=[id])


class SnippetViewsTests(TestCase):
    """Test the basic function-based views"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = create_sample_user(username='user1', password='password1')
        self.user2 = create_sample_user(username='user2', password='password2')

    def test_retrieve_snippets_list(self):
        payload1 = {
            'title': 'Snippet 1',
            'code': 'print("Hello, World!")'
        }
        payload2 = {
            'title': 'Snippet 2',
            'code': 'foo = bar'
        }

        self.client.force_authenticate(self.user1)
        self.client.post(SNIPPETS_LIST_URL, payload1)
        self.client.force_authenticate(self.user2)
        self.client.post(SNIPPETS_LIST_URL, payload2)

        res = self.client.get(SNIPPETS_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_create_snippet_success(self):
        payload = {
            'title': 'new snippet',
            'code': 'print("OHAI!")'
        }
        self.client.force_authenticate(self.user1)
        res = self.client.post(SNIPPETS_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        snippet = Snippet.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(snippet, key))

    def test_create_snippet_fail(self):
        payload = {
            'title': 'bad snippet'
        }
        self.client.force_authenticate(self.user2)
        res = self.client.post(SNIPPETS_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_snippet_detail_success(self):
        snippet = Snippet.objects.create(
            owner=self.user1,
            title='Test',
            code='print("test!")'
        )

        res = self.client.get(snippet_detail_url(snippet.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], snippet.id)

    def test_retrieve_snippet_detail_fail(self):
        snippet = Snippet.objects.create(
            owner=self.user1,
            title='Test',
            code='print("test!")'
        )

        res = self.client.get(snippet_detail_url(snippet.id + 1))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_snippet(self):
        snippet = Snippet.objects.create(
            owner=self.user1,
            title='Test',
            code='print("test!")'
        )
        self.client.force_authenticate(self.user1)
        res = self.client.delete(snippet_detail_url(snippet.id))
        res2 = self.client.get(SNIPPETS_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(res2.data), 0)

    def test_edit_snippet_success(self):
        snippet = Snippet.objects.create(
            owner=self.user1,
            title='Test',
            code='print("test!")'
        )
        payload={
            'title': 'Updated Title',
            'code': 'Updated Code'
        }
        self.client.force_authenticate(self.user1)
        res = self.client.put(snippet_detail_url(snippet.id), payload)

        snippet.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(snippet.title, payload['title'])
        self.assertEqual(snippet.code, payload['code'])

    def test_edit_snippet_wrong_user(self):
        """Test that wrong user can't edit snippet"""
        snippet = Snippet.objects.create(
            owner=self.user1,
            title='Test',
            code='Test'
        )
        payload={
            'title': 'Updated Title',
            'code': 'Updated Code'
        }
        self.client.force_authenticate(self.user2)
        res = self.client.put(snippet_detail_url(snippet.id), payload)

        snippet.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(snippet.title, payload['title'])
        self.assertNotEqual(snippet.code, payload['code'])

    def test_create_snippet_unauthenticated(self):
        """Test that a snippet can't be created if no authenticated user"""
        payload={
            'title': 'New Snippet',
            'code': "This shouldn't work!"
        }
        res = self.client.post(SNIPPETS_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Snippet.objects.all().count(), 0)


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = create_sample_user('user1')
        self.user2 = create_sample_user('user2')

    def test_retrieve_user_list(self):
        res = self.client.get(USERS_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.all().count(), 2)

    def test_retrieve_user_detail_success(self):
        res = self.client.get(user_detail_url(self.user1.id))
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], self.user1.id)

    def test_retrieve_user_detail_fail(self):
        res = self.client.get(user_detail_url(99))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
