from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

from http import HTTPStatus

User = get_user_model()

# name constants
NAME_HOME = 'notes:home'
NAME_LOGIN = 'users:login'
NAME_LOGOUT = 'users:logout'
NAME_SIGNUP = 'users:signup'
NAME_ADD = 'notes:add'
NAME_EDIT = 'notes:edit'
NAME_DELETE = 'notes:delete'
NAME_DETAIL = 'notes:detail'
NAME_LIST = 'notes:list'
NAME_SUCCESS = 'notes:success'


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый пользователь')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            slug='testNote',
            author=cls.author
        )

    def test_pages_available_for_anonymous_usr(self):
        names = [
            NAME_HOME,
            NAME_LOGIN,
            NAME_LOGOUT,
            NAME_SIGNUP
        ]
        for name in names:
            with self.subTest():
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_usr(self):
        names = {
            NAME_ADD: None,
            NAME_EDIT: (self.note.slug,),
            NAME_DETAIL: (self.note.slug,),
            NAME_DELETE: (self.note.slug,),
            NAME_LIST: None,
            NAME_SUCCESS: None
        }
        for name, args in names.items():
            with self.subTest():
                url = reverse(name, args=args)
                login_url = reverse(NAME_LOGIN)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_available_for_authenticated_usr(self):
        names = [
            NAME_ADD,
            NAME_LIST,
            NAME_SUCCESS
        ]
        for name in names:
            with self.subTest():
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_statuses_for_users(self):
        names = (
            (NAME_EDIT, (self.note.slug,)),
            (NAME_DETAIL, (self.note.slug,)),
            (NAME_DELETE, (self.note.slug,))
        )
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name, args in names:
                with self.subTest(name=name, user=user):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
