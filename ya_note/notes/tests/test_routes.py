from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

from http import HTTPStatus

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый пользователь')
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            slug='testNote',
            author=cls.author
        )

    def test_pages_available_for_anonymous_usr(self):
        names = [
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup'
        ]
        for name in names:
            with self.subTest():
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_usr(self):
        namespace = 'notes:'
        names = {
            'add': None,
            'edit': (self.note.slug,),
            'detail': (self.note.slug,),
            'delete': (self.note.slug,),
            'list': None,
            'success': None
        }
        for name, args in names.items():
            with self.subTest():
                full_name = namespace + name
                url = reverse(full_name, args=args)
                login_url = reverse('users:login')
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_available_for_authenticated_usr(self):
        namespace = 'notes:'
        names = [
            'add',
            'list',
            'success'
        ]
        for name in names:
            with self.subTest():
                full_name = namespace + name
                url = reverse(full_name)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_statuses_for_users(self):
        namespace = 'notes:'
        names = (
            ('edit', (self.note.slug,)),
            ('detail', (self.note.slug,)),
            ('delete', (self.note.slug,))
        )
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name, args in names:
                with self.subTest(name=name, user=user):
                    full_name = namespace + name
                    url = reverse(full_name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
